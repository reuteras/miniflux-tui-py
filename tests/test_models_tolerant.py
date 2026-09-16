# SPDX-License-Identifier: MIT
"""Tests for tolerant parsing of server records and client-side hardening."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from miniflux_tui.api import client as client_module
from miniflux_tui.api.client import MinifluxClient
from miniflux_tui.api.models import Category, Entry, Feed


def _entry(**overrides) -> dict:
    data = {
        "id": 1,
        "feed_id": 2,
        "title": "Title",
        "url": "https://example.com/post",
        "content": "<p>hi</p>",
        "feed": {"id": 2, "title": "Feed", "site_url": "https://example.com", "feed_url": "https://example.com/rss"},
        "status": "unread",
        "starred": False,
        "published_at": "2026-01-02T03:04:05Z",
    }
    data.update(overrides)
    return data


class TestTolerantModels:
    def test_entry_with_only_ids_parses(self) -> None:
        entry = Entry.from_dict({"id": 7, "feed": {"id": 3}})
        assert entry.id == 7
        assert entry.feed_id == 3
        assert entry.title == ""
        assert entry.status == "unread"
        assert entry.published_at == datetime.fromtimestamp(0, tz=UTC)

    def test_entry_without_feed_object_uses_feed_id(self) -> None:
        entry = Entry.from_dict({"id": 1, "feed_id": 9})
        assert entry.feed.id == 9

    def test_entry_without_any_feed_reference_raises(self) -> None:
        with pytest.raises(KeyError):
            Entry.from_dict({"id": 1})

    def test_entry_without_id_raises(self) -> None:
        data = _entry()
        del data["id"]
        with pytest.raises(KeyError):
            Entry.from_dict(data)

    @pytest.mark.parametrize("value", [None, "", "not a date", 12345, "2026-13-45T00:00:00Z"])
    def test_bad_published_at_falls_back_to_epoch(self, value) -> None:
        entry = Entry.from_dict(_entry(published_at=value))
        assert entry.published_at == datetime.fromtimestamp(0, tz=UTC)

    def test_naive_published_at_gets_utc(self) -> None:
        entry = Entry.from_dict(_entry(published_at="2026-01-02T03:04:05"))
        assert entry.published_at.tzinfo is not None

    def test_null_string_fields_become_empty(self) -> None:
        entry = Entry.from_dict(_entry(title=None, url=None, content=None))
        assert (entry.title, entry.url, entry.content) == ("", "", "")

    def test_non_string_title_is_stringified(self) -> None:
        assert Entry.from_dict(_entry(title=42)).title == "42"

    def test_malformed_enclosures_are_skipped(self) -> None:
        entry = Entry.from_dict(
            _entry(enclosures=[{"id": 1, "url": "https://x/a.png", "mime_type": "image/png"}, "junk", {"url": "no id"}, None])
        )
        assert entry.enclosures is not None
        assert len(entry.enclosures) == 1
        assert entry.image_enclosures[0].url == "https://x/a.png"

    def test_feed_with_odd_types(self) -> None:
        feed = Feed.from_dict(
            {"id": "5", "title": None, "category_id": "abc", "parsing_error_count": "3", "disabled": 1, "check_interval": None}
        )
        assert feed.id == 5
        assert feed.title == ""
        assert feed.category_id is None
        assert feed.parsing_error_count == 3
        assert feed.disabled is True
        assert feed.check_interval is None

    def test_category_without_title(self) -> None:
        assert Category.from_dict({"id": 1}).title == ""


class TestParseEntries:
    def test_skips_malformed_records_and_keeps_the_rest(self, caplog) -> None:
        raw = [_entry(id=1), "garbage", {"title": "no ids"}, None, _entry(id=2)]
        with caplog.at_level("WARNING"):
            entries = client_module._parse_entries(raw)
        assert [e.id for e in entries] == [1, 2]
        assert sum("Skipping malformed entry" in r.message for r in caplog.records) == 3

    def test_non_list_input_yields_empty(self) -> None:
        assert client_module._parse_entries({"entries": []}) == []
        assert client_module._parse_entries(None) == []


class TestClientHardening:
    def test_timeout_is_passed_to_official_client(self) -> None:
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base:
            MinifluxClient("http://localhost:8080", "key", timeout=7.5)
        mock_base.assert_called_once_with("http://localhost:8080", api_key="key", timeout=7.5)

    @pytest.mark.asyncio
    async def test_ssl_error_is_not_retried(self) -> None:
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "key")
        calls = 0

        def failing():
            nonlocal calls
            calls += 1
            msg = "certificate verify failed"
            raise requests.exceptions.SSLError(msg)

        with pytest.raises(requests.exceptions.SSLError):
            await client._call_with_retry(failing, max_retries=3, backoff_factor=0.001)
        assert calls == 1

    @pytest.mark.asyncio
    async def test_plain_connection_error_is_still_retried(self) -> None:
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "key")
        calls = 0

        def flaky():
            nonlocal calls
            calls += 1
            if calls < 3:
                msg = "reset"
                raise requests.exceptions.ConnectionError(msg)
            return "ok"

        assert await client._call_with_retry(flaky, max_retries=3, backoff_factor=0.001) == "ok"
        assert calls == 3

    @pytest.mark.asyncio
    async def test_default_limit_pages_through_everything(self) -> None:
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base:
            api = MagicMock()
            mock_base.return_value = api
            pages = [
                {"entries": [_entry(id=i) for i in range(100)]},
                {"entries": [_entry(id=i) for i in range(100, 130)]},
            ]
            api.get_entries.side_effect = pages
            client = MinifluxClient("http://localhost:8080", "key")
            entries = await client.get_unread_entries()
        assert len(entries) == 130
        assert api.get_entries.call_count == 2

    @pytest.mark.asyncio
    async def test_explicit_limit_is_a_single_request(self) -> None:
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base:
            api = MagicMock()
            mock_base.return_value = api
            api.get_entries.return_value = {"entries": [_entry(id=i) for i in range(100)]}
            client = MinifluxClient("http://localhost:8080", "key")
            entries = await client.get_starred_entries(limit=100)
        assert len(entries) == 100
        api.get_entries.assert_called_once()
        assert api.get_entries.call_args.kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_bad_record_does_not_abort_page(self) -> None:
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base:
            api = MagicMock()
            mock_base.return_value = api
            api.get_entries.return_value = {"entries": [_entry(id=1), {"broken": True}, _entry(id=3)]}
            client = MinifluxClient("http://localhost:8080", "key")
            entries = await client.get_read_entries(limit=50)
        assert [e.id for e in entries] == [1, 3]
