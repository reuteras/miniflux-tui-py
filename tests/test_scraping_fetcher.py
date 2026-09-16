# SPDX-License-Identifier: MIT
"""Tests for the secure content fetcher."""

from __future__ import annotations

from unittest.mock import patch

import pytest
import requests
from requests.structures import CaseInsensitiveDict

from miniflux_tui.scraping import fetcher as fetcher_module
from miniflux_tui.scraping.fetcher import SecureFetcher

PUBLIC_IP = "93.184.216.34"


class _FakeResponse:
    """Minimal stand-in for ``requests.Response`` supporting streaming and ``with``."""

    def __init__(
        self,
        status: int = 200,
        headers: dict[str, str] | None = None,
        body: bytes = b"<html><body>Test content</body></html>",
        encoding: str | None = "utf-8",
        chunks: list[bytes] | None = None,
    ) -> None:
        self.status_code = status
        self.headers = CaseInsensitiveDict(headers if headers is not None else {"content-type": "text/html; charset=utf-8"})
        self._body = body
        self._chunks = chunks
        self.encoding = encoding
        self.closed = False

    def iter_content(self, chunk_size: int):
        if self._chunks is not None:
            yield from self._chunks
            return
        for i in range(0, len(self._body), chunk_size):
            yield self._body[i : i + chunk_size]

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.closed = True
        return False


@pytest.fixture(autouse=True)
def fake_dns(monkeypatch):
    """Resolve every hostname to a public address so tests never hit DNS."""
    monkeypatch.setattr(
        fetcher_module.hostname_resolves_to_private.__globals__["socket"],
        "getaddrinfo",
        lambda *_a, **_k: [(0, 0, 0, "", (PUBLIC_IP, 80))],
    )


class TestSecureFetcher:
    """Test suite for SecureFetcher class."""

    def test_init(self):
        fetcher = SecureFetcher()
        assert fetcher.MAX_SIZE == 5 * 1024 * 1024
        assert fetcher.TIMEOUT == 10
        assert {"http", "https"} == fetcher.ALLOWED_SCHEMES
        # requests must never follow redirects on its own; each hop is validated manually
        assert fetcher.session.max_redirects == 0

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            # Valid URLs
            ("https://example.com", True),
            ("http://example.com", True),
            ("https://example.com/path?a=1&b=2", True),
            ("https://subdomain.example.com", True),
            ("http://example.com:8080/path", True),
            # Invalid schemes
            ("ftp://example.com", False),
            ("file:///etc/passwd", False),
            ("javascript:alert(1)", False),
            ("data:text/html,<script>", False),
            # Localhost variants
            ("http://localhost", False),
            ("http://localhost:8080", False),
            ("https://LOCALHOST", False),
            # Loopback and private IPv4
            ("http://127.0.0.1", False),
            ("http://127.0.0.2", False),
            ("http://10.0.0.1", False),
            ("http://192.168.1.1", False),
            ("http://172.16.0.1", False),
            ("http://172.31.255.255", False),
            ("http://169.254.169.254", False),
            ("http://0.0.0.0", False),
            ("http://100.64.1.1", False),
            # Alternate spellings that used to bypass the prefix blocklist
            ("http://[::1]/", False),
            ("http://[::ffff:127.0.0.1]/", False),
            ("http://[fd00::1]/", False),
            ("http://2130706433/", False),
            ("http://0x7f000001/", False),
            # Junk
            ("", False),
            ("not a url", False),
            ("http://", False),
            ("http://exa mple.com", False),
        ],
    )
    def test_is_safe_url(self, url, expected):
        fetcher = SecureFetcher()
        assert fetcher._is_safe_url(url) is expected

    def test_hostname_resolving_to_private_address_is_unsafe(self, monkeypatch):
        monkeypatch.setattr(
            fetcher_module.hostname_resolves_to_private.__globals__["socket"],
            "getaddrinfo",
            lambda *_a, **_k: [(0, 0, 0, "", ("127.0.0.1", 80))],
        )
        assert SecureFetcher()._is_safe_url("http://localtest.me/") is False

    @pytest.mark.asyncio
    async def test_fetch_success(self):
        fetcher = SecureFetcher()
        response = _FakeResponse(headers={"content-type": "text/html", "content-length": "38"})
        with patch.object(fetcher.session, "get", return_value=response) as mock_get:
            result = await fetcher.fetch("https://example.com")
        assert result == "<html><body>Test content</body></html>"
        mock_get.assert_called_once_with("https://example.com", timeout=fetcher.TIMEOUT, stream=True, allow_redirects=False)
        assert response.closed is True

    @pytest.mark.asyncio
    async def test_fetch_unsafe_url(self):
        fetcher = SecureFetcher()
        with patch.object(fetcher.session, "get") as mock_get, pytest.raises(ValueError, match="Unsafe URL"):
            await fetcher.fetch("http://127.0.0.1/admin")
        mock_get.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_response_too_large_header(self):
        fetcher = SecureFetcher()
        response = _FakeResponse(headers={"content-type": "text/html", "content-length": str(10 * 1024 * 1024)})
        with patch.object(fetcher.session, "get", return_value=response), pytest.raises(ValueError, match="too large"):
            await fetcher.fetch("https://example.com")

    @pytest.mark.asyncio
    async def test_fetch_malformed_content_length(self):
        fetcher = SecureFetcher()
        response = _FakeResponse(headers={"content-type": "text/html", "content-length": "lots"})
        with patch.object(fetcher.session, "get", return_value=response), pytest.raises(ValueError, match="Malformed"):
            await fetcher.fetch("https://example.com")

    @pytest.mark.asyncio
    async def test_fetch_response_too_large_streamed(self):
        """Without a Content-Length header the body is still capped while streaming."""
        fetcher = SecureFetcher()
        chunk = b"x" * (1024 * 1024)
        response = _FakeResponse(headers={"content-type": "text/html"}, chunks=[chunk] * 6)
        with patch.object(fetcher.session, "get", return_value=response), pytest.raises(ValueError, match="too large"):
            await fetcher.fetch("https://example.com")

    @pytest.mark.asyncio
    async def test_fetch_rejects_binary_content_type(self):
        fetcher = SecureFetcher()
        response = _FakeResponse(headers={"content-type": "application/octet-stream"})
        with patch.object(fetcher.session, "get", return_value=response), pytest.raises(ValueError, match="content type"):
            await fetcher.fetch("https://example.com/file.bin")

    @pytest.mark.asyncio
    async def test_fetch_follows_safe_redirect(self):
        fetcher = SecureFetcher()
        redirect = _FakeResponse(status=302, headers={"location": "/moved"})
        final = _FakeResponse(body=b"<p>moved</p>")
        with patch.object(fetcher.session, "get", side_effect=[redirect, final]) as mock_get:
            result = await fetcher.fetch("https://example.com/start")
        assert result == "<p>moved</p>"
        assert [c.args[0] for c in mock_get.call_args_list] == ["https://example.com/start", "https://example.com/moved"]

    @pytest.mark.asyncio
    async def test_fetch_rejects_redirect_to_private_address(self):
        """A public page redirecting to an internal address is refused before the second request."""
        fetcher = SecureFetcher()
        redirect = _FakeResponse(status=302, headers={"location": "http://169.254.169.254/latest/meta-data/"})
        with patch.object(fetcher.session, "get", side_effect=[redirect]) as mock_get, pytest.raises(ValueError, match="Unsafe URL"):
            await fetcher.fetch("https://example.com/start")
        assert mock_get.call_count == 1

    @pytest.mark.asyncio
    async def test_fetch_rejects_redirect_loop(self):
        fetcher = SecureFetcher()
        responses = [_FakeResponse(status=301, headers={"location": "https://example.com/loop"}) for _ in range(10)]
        with patch.object(fetcher.session, "get", side_effect=responses), pytest.raises(ValueError, match="Too many redirects"):
            await fetcher.fetch("https://example.com/loop")

    @pytest.mark.asyncio
    async def test_fetch_redirect_without_location(self):
        fetcher = SecureFetcher()
        response = _FakeResponse(status=302, headers={})
        with patch.object(fetcher.session, "get", return_value=response), pytest.raises(RuntimeError, match="Location"):
            await fetcher.fetch("https://example.com")

    @pytest.mark.asyncio
    async def test_fetch_timeout(self):
        fetcher = SecureFetcher()
        with patch.object(fetcher.session, "get", side_effect=requests.Timeout("slow")), pytest.raises(TimeoutError, match="Timeout"):
            await fetcher.fetch("https://example.com")

    @pytest.mark.asyncio
    async def test_fetch_http_error(self):
        fetcher = SecureFetcher()
        response = _FakeResponse(status=404)
        with patch.object(fetcher.session, "get", return_value=response), pytest.raises(RuntimeError, match="HTTP error 404"):
            await fetcher.fetch("https://example.com/missing")

    @pytest.mark.asyncio
    async def test_fetch_connection_error_does_not_leak_details(self):
        fetcher = SecureFetcher()
        error = requests.ConnectionError("socket says: internal detail")
        with patch.object(fetcher.session, "get", side_effect=error), pytest.raises(RuntimeError) as excinfo:
            await fetcher.fetch("https://example.com")
        assert "ConnectionError" in str(excinfo.value)
        assert "internal detail" not in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_fetch_decodes_with_declared_encoding(self):
        fetcher = SecureFetcher()
        response = _FakeResponse(body="<p>héllo</p>".encode("latin-1"), encoding="latin-1")
        with patch.object(fetcher.session, "get", return_value=response):
            result = await fetcher.fetch("https://example.com")
        assert result == "<p>héllo</p>"

    @pytest.mark.asyncio
    async def test_close(self):
        fetcher = SecureFetcher()
        with patch.object(fetcher.session, "close") as mock_close:
            await fetcher.close()
        mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        async with SecureFetcher() as fetcher:
            assert isinstance(fetcher, SecureFetcher)
