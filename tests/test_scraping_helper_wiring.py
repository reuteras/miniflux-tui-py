# SPDX-License-Identifier: MIT
"""The scraping helper must be reachable from the entry list and entry reader (``x``)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from textual.binding import Binding

from miniflux_tui.ui.screens.entry_list import EntryListItem, EntryListScreen
from miniflux_tui.ui.screens.entry_reader import EntryReaderScreen
from miniflux_tui.ui.screens.scraping_helper import ScrapingHelperScreen


def _bindings(screen_cls) -> dict[str, str]:
    return {b.key: b.action for b in screen_cls.BINDINGS if isinstance(b, Binding)}


class TestBindings:
    def test_entry_list_x_opens_scraping_helper_and_X_feed_settings(self) -> None:  # noqa: N802
        bindings = _bindings(EntryListScreen)
        assert bindings["x"] == "scraping_helper"
        assert bindings["X"] == "feed_settings"

    def test_entry_reader_x_opens_scraping_helper_and_X_feed_settings(self) -> None:  # noqa: N802
        bindings = _bindings(EntryReaderScreen)
        assert bindings["x"] == "scraping_helper"
        assert bindings["X"] == "feed_settings"


class TestEntryReaderAction:
    def test_pushes_helper_with_entry_details(self, sample_entry) -> None:
        screen = EntryReaderScreen(sample_entry)
        fake_app = MagicMock()
        fake_app.client = MagicMock()
        with patch.object(EntryReaderScreen, "app", new_callable=PropertyMock, return_value=fake_app):
            screen.action_scraping_helper()
        pushed = fake_app.push_screen.call_args.args[0]
        assert isinstance(pushed, ScrapingHelperScreen)
        assert pushed.entry_url == sample_entry.url
        assert pushed.feed_id == sample_entry.feed_id
        assert pushed.feed_title == sample_entry.feed.title

    @pytest.mark.asyncio
    async def test_save_callback_updates_feed_scraper_rules(self, sample_entry) -> None:
        screen = EntryReaderScreen(sample_entry)
        fake_app = MagicMock()
        fake_app.client = MagicMock()
        fake_app.client.update_feed = AsyncMock()
        with (
            patch.object(EntryReaderScreen, "app", new_callable=PropertyMock, return_value=fake_app),
            patch.object(EntryReaderScreen, "notify") as notify,
        ):
            screen.action_scraping_helper()
            pushed = fake_app.push_screen.call_args.args[0]
            await pushed.on_save_callback(sample_entry.feed_id, "article.content")
        fake_app.client.update_feed.assert_awaited_once_with(sample_entry.feed_id, scraper_rules="article.content")
        notify.assert_called_once()

    def test_without_client_warns_and_does_not_push(self, sample_entry) -> None:
        screen = EntryReaderScreen(sample_entry)
        fake_app = MagicMock()
        fake_app.client = None
        with (
            patch.object(EntryReaderScreen, "app", new_callable=PropertyMock, return_value=fake_app),
            patch.object(EntryReaderScreen, "notify") as notify,
        ):
            screen.action_scraping_helper()
        fake_app.push_screen.assert_not_called()
        assert notify.call_args.kwargs["severity"] == "error"

    def test_without_url_warns_and_does_not_push(self, sample_entry) -> None:
        sample_entry.url = ""
        screen = EntryReaderScreen(sample_entry)
        fake_app = MagicMock()
        with (
            patch.object(EntryReaderScreen, "app", new_callable=PropertyMock, return_value=fake_app),
            patch.object(EntryReaderScreen, "notify") as notify,
        ):
            screen.action_scraping_helper()
        fake_app.push_screen.assert_not_called()
        assert notify.call_args.kwargs["severity"] == "warning"


class TestEntryListAction:
    def test_pushes_helper_for_highlighted_entry(self, sample_entry) -> None:
        screen = EntryListScreen(entries=[sample_entry])
        screen.list_view = MagicMock(highlighted_child=EntryListItem(sample_entry))
        fake_app = MagicMock()
        fake_app.client = MagicMock()
        with patch.object(EntryListScreen, "app", new_callable=PropertyMock, return_value=fake_app):
            screen.action_scraping_helper()
        pushed = fake_app.push_screen.call_args.args[0]
        assert isinstance(pushed, ScrapingHelperScreen)
        assert pushed.entry_url == sample_entry.url
        assert pushed.feed_id == sample_entry.feed_id

    def test_without_selection_warns(self, sample_entry) -> None:
        screen = EntryListScreen(entries=[sample_entry])
        screen.list_view = MagicMock(highlighted_child=None)
        fake_app = MagicMock()
        with (
            patch.object(EntryListScreen, "app", new_callable=PropertyMock, return_value=fake_app),
            patch.object(EntryListScreen, "notify") as notify,
        ):
            screen.action_scraping_helper()
        fake_app.push_screen.assert_not_called()
        assert notify.call_args.kwargs["severity"] == "warning"
