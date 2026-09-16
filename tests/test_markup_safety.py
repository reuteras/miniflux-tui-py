# SPDX-License-Identifier: MIT
"""Regression tests: untrusted text must never be parsed as Textual markup.

Textual parses plain strings given to Static/Label/notify as markup. A feed
title or server error containing ``[/red]`` used to raise ``MarkupError`` and
take the whole app down; ``[bold]`` restyled the UI. These tests pin the
escaping and ``markup=False`` fixes.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from textual.app import App, ComposeResult
from textual.content import Content
from textual.widgets import Static

from miniflux_tui.api.models import Category, Feed
from miniflux_tui.config import Config
from miniflux_tui.ui.app import MinifluxTuiApp
from miniflux_tui.ui.screens.category_management import CategoryListItem
from miniflux_tui.ui.screens.feed_management import FeedListItem
from miniflux_tui.ui.screens.scraping_helper import ScrapingHelperScreen
from miniflux_tui.ui.screens.status import StatusScreen
from miniflux_tui.utils import escape_markup, strip_control_chars

HOSTILE = "[/red] evil [bold]title[/bold] [@click=app.quit]x[/]"


def _render_plain(widget: Static) -> str:
    """Render a Static/Label and return the plain text (raises on bad markup)."""
    rendered = widget.render()
    return rendered.plain if isinstance(rendered, Content) else str(rendered)


class TestHelpers:
    def test_escape_markup_neutralizes_tags_and_control_chars(self) -> None:
        escaped = escape_markup("\x1b[31m[/red] [bold]x[/bold] [@click=app.quit]y[/]")
        # Must parse without raising, apply no styles or actions, and keep the text
        content = Content.from_markup(escaped)
        assert not content.spans
        assert "\x1b" not in content.plain
        assert "[bold]x[/bold]" in content.plain
        assert "[@click=app.quit]y" in content.plain

    def test_strip_control_chars_removes_bidi_and_zero_width(self) -> None:
        # RTL override, zero-width space, word joiner, BOM, isolate controls
        assert strip_control_chars("a\u202eb\u200bc\u2060d\ufeffe\u2066f\u2069g") == "abcdefg"

    def test_strip_control_chars_keeps_ordinary_unicode(self) -> None:
        assert strip_control_chars("héllo “quoted” 日本語 🎉") == "héllo “quoted” 日本語 🎉"


class _Host(App):
    """Bare app used to mount screens and widgets under test."""

    def compose(self) -> ComposeResult:
        yield Static("host")


class TestListItems:
    @pytest.mark.asyncio
    async def test_feed_list_item_with_hostile_title_renders_plain(self) -> None:
        feed = Feed(id=1, title=HOSTILE, site_url="https://x", feed_url="https://x/feed")
        app = _Host()
        async with app.run_test() as pilot:
            item = FeedListItem(feed)
            await app.mount(item)
            await pilot.pause()
            assert HOSTILE[:40] in _render_plain(item.query_one(Static))

    @pytest.mark.asyncio
    async def test_category_list_item_with_hostile_title_renders_plain(self) -> None:
        app = _Host()
        async with app.run_test() as pilot:
            item = CategoryListItem(Category(id=1, title=HOSTILE), unread_count=1, read_count=2)
            await app.mount(item)
            await pilot.pause()
            assert HOSTILE in _render_plain(item.query_one(Static))


class TestStatusScreen:
    @pytest.mark.asyncio
    async def test_error_feeds_with_hostile_fields_do_not_crash(self) -> None:
        app = _Host()
        async with app.run_test() as pilot:
            screen = StatusScreen()
            app.push_screen(screen)
            await pilot.pause()
            screen.error_feeds = [
                Feed(
                    id=1,
                    title=HOSTILE,
                    site_url="https://x",
                    feed_url="https://x/?a[]=1[/dim]",
                    parsing_error_message="500 [/red] boom",
                    parsing_error_count=3,
                    checked_at="2026-01-01T00:00:00Z[/]",
                    disabled=True,
                )
            ]
            screen.feeds = screen.error_feeds
            screen._update_error_feeds()
            await pilot.pause()
            text = _render_plain(screen.query_one("#error-feeds-list", Static))
            assert "[/red] evil" in text
            assert "500 [/red] boom" in text
            assert "DISABLED" in text

    @pytest.mark.asyncio
    async def test_error_state_with_hostile_exception_text(self) -> None:
        app = _Host()
        async with app.run_test() as pilot:
            screen = StatusScreen()
            app.push_screen(screen)
            await pilot.pause()
            screen._update_error_state("Error: ClientError: [/red] from server \x1b[2J")
            await pilot.pause()
            text = _render_plain(screen.query_one("#server-info", Static))
            assert "[/red] from server" in text
            assert "\x1b" not in text

    @pytest.mark.asyncio
    async def test_server_info_with_hostile_values(self) -> None:
        app = _Host()
        async with app.run_test() as pilot:
            screen = StatusScreen()
            app.push_screen(screen)
            await pilot.pause()
            screen.server_url = "https://x/[/]"
            screen.server_version = "[bold]2.0[/bold]"
            screen.username = HOSTILE
            screen._update_server_info()
            await pilot.pause()
            text = _render_plain(screen.query_one("#server-info", Static))
            assert "[bold]2.0[/bold]" in text
            assert HOSTILE in text


class TestScrapingHelperScreen:
    @pytest.mark.asyncio
    async def test_hostile_feed_title_url_and_page_do_not_crash(self, monkeypatch) -> None:
        page = "<html><body><article class='w-[100px]'><p>text [/red] here</p></article></body></html>"
        monkeypatch.setattr(ScrapingHelperScreen, "_fetch_and_analyze", AsyncMock())
        app = _Host()
        async with app.run_test() as pilot:
            screen = ScrapingHelperScreen(entry_url="https://x/?q=[/dim]", feed_id=1, feed_title=HOSTILE)
            app.push_screen(screen)
            await pilot.pause()
            assert HOSTILE in _render_plain(screen.query_one("#feed-display", Static))
            assert "[/dim]" in _render_plain(screen.query_one("#url-display", Static))
            screen.raw_html = page
            await screen.action_view_raw()
            await pilot.pause()
            assert "[/red] here" in _render_plain(screen.query_one("#preview-content", Static))
            screen.query_one("#status-message", Static).update("❌ Invalid URL: Unsafe URL: http://x/[/red]")
            await pilot.pause()


class TestAppNotify:
    @pytest.mark.asyncio
    async def test_notify_never_parses_markup(self) -> None:
        config = Config(server_url="http://localhost:8080", password=["echo", "token"])
        app = MinifluxTuiApp(config)
        app.client = MagicMock()
        async with app.run_test() as pilot:
            app.notify(f"Entry saved: {HOSTILE}", severity="error")
            app.notify("Failed: \x1b[2J[/x]")
            await pilot.pause()
            messages = [n.message for n in app._notifications]
            assert f"Entry saved: {HOSTILE}" in messages
            assert "Failed: [2J[/x]" in messages
            assert all(not n.markup for n in app._notifications)
