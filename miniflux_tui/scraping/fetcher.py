# SPDX-License-Identifier: MIT
"""Secure web content fetcher with strict validation and safety measures.

Runs from the user's machine, so every URL it touches is treated as hostile:
the scheme, host, resolved addresses and each redirect hop are validated, and
the response body is streamed with a hard size cap.
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import ClassVar
from urllib.parse import urljoin

import requests

from miniflux_tui.security import hostname_resolves_to_private, validate_feed_url

_REDIRECT_STATUSES: frozenset[int] = frozenset({301, 302, 303, 307, 308})
_ALLOWED_CONTENT_TYPES: tuple[str, ...] = ("text/html", "application/xhtml+xml", "text/xml", "application/xml", "text/plain")


class SecureFetcher:
    """Safely fetch and validate web content with security constraints."""

    MAX_SIZE: ClassVar[int] = 5 * 1024 * 1024  # 5MB max response size
    TIMEOUT: ClassVar[int] = 10  # seconds
    MAX_REDIRECTS: ClassVar[int] = 5
    ALLOWED_SCHEMES: ClassVar[set[str]] = {"http", "https"}
    _CHUNK_SIZE: ClassVar[int] = 64 * 1024

    def __init__(self) -> None:
        """Initialize a requests session with safety settings."""
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (compatible; MinifluxTUI)"
        # Never let requests follow redirects on its own; each hop is validated in _fetch_sync.
        self.session.max_redirects = 0

    async def fetch(self, url: str) -> str:
        """Safely fetch URL content with validation and size limits.

        Args:
            url: The URL to fetch

        Returns:
            The response text content

        Raises:
            ValueError: If URL is unsafe, redirects somewhere unsafe, or the response is too large
            TimeoutError: If request times out
            RuntimeError: For other fetch errors
        """
        self._validate_url(url)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(self._fetch_sync, url))

    def _fetch_sync(self, url: str) -> str:
        """Blocking fetch that follows redirects manually, validating every hop."""
        current = url
        for _ in range(self.MAX_REDIRECTS + 1):
            try:
                response = self.session.get(current, timeout=self.TIMEOUT, stream=True, allow_redirects=False)
            except requests.Timeout as e:
                msg = f"Timeout fetching {current}"
                raise TimeoutError(msg) from e
            except requests.RequestException as e:
                msg = f"Fetch error for {current}: {type(e).__name__}"
                raise RuntimeError(msg) from e

            with response:
                if response.status_code in _REDIRECT_STATUSES:
                    location = response.headers.get("location")
                    if not location:
                        msg = f"Redirect without Location header from {current}"
                        raise RuntimeError(msg)
                    current = urljoin(current, location)
                    self._validate_url(current)
                    continue

                if response.status_code >= 400:
                    msg = f"HTTP error {response.status_code}: {current}"
                    raise RuntimeError(msg)

                self._check_content_type(response, current)
                self._check_content_length_header(response, current)
                body = self._read_capped(response, current)
                encoding = response.encoding or "utf-8"
                return body.decode(encoding, errors="replace")

        msg = f"Too many redirects fetching {url}"
        raise ValueError(msg)

    def _validate_url(self, url: str) -> None:
        """Validate that URL is safe to fetch.

        Args:
            url: The URL to validate

        Raises:
            ValueError: If URL is unsafe
        """
        if not self._is_safe_url(url):
            msg = f"Unsafe URL: {url}"
            raise ValueError(msg)

    def _check_content_type(self, response: requests.Response, url: str) -> None:
        """Reject binary responses; only text-like documents are analyzable."""
        content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
        if content_type and not content_type.startswith(_ALLOWED_CONTENT_TYPES):
            msg = f"Unsupported content type {content_type!r} from {url}"
            raise ValueError(msg)

    def _check_content_length_header(self, response: requests.Response, url: str) -> None:
        """Check Content-Length header before reading the body.

        Raises:
            ValueError: If Content-Length header exceeds MAX_SIZE or is malformed
        """
        content_length = response.headers.get("content-length")
        if content_length is None:
            return
        try:
            declared = int(content_length)
        except ValueError as e:
            msg = f"Malformed Content-Length header from {url}"
            raise ValueError(msg) from e
        if declared > self.MAX_SIZE:
            msg = f"Response too large: {declared} bytes from {url}"
            raise ValueError(msg)

    def _read_capped(self, response: requests.Response, url: str) -> bytes:
        """Stream the body, aborting as soon as MAX_SIZE is exceeded."""
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=self._CHUNK_SIZE):
            total += len(chunk)
            if total > self.MAX_SIZE:
                msg = f"Response too large: more than {self.MAX_SIZE} bytes from {url}"
                raise ValueError(msg)
            chunks.append(chunk)
        return b"".join(chunks)

    def _is_safe_url(self, url: str) -> bool:
        """Validate URL is safe to fetch from this machine.

        Reuses the shared SSRF checks (scheme, IP literal ranges, control
        characters) and additionally resolves the hostname so that names
        pointing at loopback, link-local or private addresses are rejected.

        Args:
            url: The URL to validate

        Returns:
            True if URL is safe to fetch, False otherwise
        """
        is_valid, _ = validate_feed_url(url)
        if not is_valid:
            return False
        return not hostname_resolves_to_private(url)

    async def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    async def __aenter__(self) -> SecureFetcher:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
