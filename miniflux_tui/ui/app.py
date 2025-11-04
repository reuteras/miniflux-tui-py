"""Main TUI application."""

from __future__ import annotations

import traceback
from importlib import import_module
from typing import TYPE_CHECKING, cast

from textual.app import App
from textual.driver import Driver

from miniflux_tui.api.client import MinifluxClient
from miniflux_tui.api.models import Category, Entry, Feed
from miniflux_tui.config import Config
from miniflux_tui.constants import DEFAULT_ENTRY_LIMIT

from .screens.help import HelpScreen
from .screens.loading import LoadingScreen

if TYPE_CHECKING:
    from miniflux_tui.ui.screens.entry_history import EntryHistoryScreen
    from miniflux_tui.ui.screens.entry_list import EntryListScreen
    from miniflux_tui.ui.screens.entry_reader import EntryReaderScreen
    from miniflux_tui.ui.screens.feed_management import FeedManagementScreen
    from miniflux_tui.ui.screens.settings_management import SettingsScreen
    from miniflux_tui.ui.screens.status import StatusScreen


def _load_entry_list_screen_cls() -> type[EntryListScreen]:
    """Import and return the entry list screen class."""

    module = import_module("miniflux_tui.ui.screens.entry_list")
    return cast("type[EntryListScreen]", module.EntryListScreen)


def _load_status_screen_cls() -> type[StatusScreen]:
    """Import and return the status screen class."""

    module = import_module("miniflux_tui.ui.screens.status")
    return cast("type[StatusScreen]", module.StatusScreen)


def _load_settings_screen_cls() -> type[SettingsScreen]:
    """Import and return the settings screen class."""

    module = import_module("miniflux_tui.ui.screens.settings_management")
    return cast("type[SettingsScreen]", module.SettingsScreen)


def _load_history_screen_cls() -> type[EntryHistoryScreen]:  # nosec: CWE-1047 - Type-only import avoids cyclic dependency
    """Import and return the history screen class."""

    module = import_module("miniflux_tui.ui.screens.entry_history")
    return cast("type[EntryHistoryScreen]", module.EntryHistoryScreen)


class MinifluxTuiApp(App):
    """A Textual TUI application for Miniflux."""

    CSS = """
    Screen {
        background: $surface;
    }

    .entry-title {
        padding: 1 2;
        background: $boost;
    }

    .entry-meta {
        padding: 0 2;
    }

    .entry-url {
        padding: 0 2 1 2;
    }

    .separator {
        padding: 0 2;
        color: $border;
    }

    .entry-content {
        padding: 1 2;
    }

    ListView {
        background: $surface;
        color: $text;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: $boost;
    }

    ListItem.-active {
        background: $accent;
    }

    /* Hide collapsed entries */
    ListItem.collapsed {
        display: none;
    }
    """

    def __init__(
        self,
        config: Config,
        driver_class: type[Driver] | None = None,
        css_path: str | None = None,
        watch_css: bool = False,
    ):
        """
        Initialize the Miniflux TUI application.

        Args:
            config: Application configuration
            driver_class: Textual driver class
            css_path: Path to custom CSS file
            watch_css: Whether to watch CSS file for changes
        """
        super().__init__(
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        self.config = config
        self.client: MinifluxClient | None = None
        self.entries: list[Entry] = []
        self.categories: list[Category] = []
        self.feeds: list[Feed] = []
        self.entry_category_map: dict[int, int] = {}  # Maps entry_id → category_id
        self.current_view = "unread"  # or "starred"
        self._entry_list_screen_cls: type[EntryListScreen] | None = None
        self._status_screen_cls: type[StatusScreen] | None = None

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        # Show loading screen immediately
        self.install_screen(LoadingScreen(), name="loading")
        self.push_screen("loading")

        # Schedule the data loading to happen after the screen is rendered
        self.call_after_refresh(self._load_data)

    async def _load_data(self) -> None:
        """Load data after loading screen is displayed."""
        # Initialize API client - this may block on password command
        self.client = MinifluxClient(
            base_url=self.config.server_url,
            api_key=self.config.api_key,
            allow_invalid_certs=self.config.allow_invalid_certs,
        )

        entry_list_cls: type[EntryListScreen] = _load_entry_list_screen_cls()
        self._entry_list_screen_cls = entry_list_cls
        self.install_screen(
            entry_list_cls(
                entries=self.entries,
                categories=self.categories,
                unread_color=self.config.unread_color,
                read_color=self.config.read_color,
                default_sort=self.config.default_sort,
                group_by_feed=self.config.default_group_by_feed,
                group_collapsed=self.config.group_collapsed,
            ),
            name="entry_list",
        )

        self.install_screen(HelpScreen(), name="help")

        status_cls: type[StatusScreen] = _load_status_screen_cls()
        self._status_screen_cls = status_cls
        self.install_screen(status_cls(), name="status")

        settings_cls: type[SettingsScreen] = _load_settings_screen_cls()
        self.install_screen(settings_cls(), name="settings")

        history_cls: type[EntryHistoryScreen] = _load_history_screen_cls()
        self.install_screen(history_cls(), name="history")

        # Load categories, feeds, and entries while loading screen is shown
        # Order matters: categories are needed to build entry→category mapping
        await self.load_categories()
        await self.load_feeds()

        # Build category mapping using category API (better than feed-based approach)
        # This creates a mapping of entry_id → category_id that we'll use later
        self.entry_category_map = await self._build_entry_category_mapping()

        await self.load_entries()

        # Dismiss loading screen and show entry list
        self.pop_screen()
        self.push_screen("entry_list")

    def _get_entry_list_screen(self) -> EntryListScreen | None:
        """Return the entry list screen instance if available."""
        entry_list_cls: type[EntryListScreen] = self._entry_list_screen_cls or _load_entry_list_screen_cls()
        self._entry_list_screen_cls = entry_list_cls

        if not self.is_screen_installed("entry_list"):
            return None

        screen = self.get_screen("entry_list")
        if isinstance(screen, entry_list_cls):
            return screen

        self.log("entry_list screen is installed but not an EntryListScreen instance")
        return None

    async def load_categories(self) -> None:
        """Load categories from Miniflux API."""
        if not self.client:
            self.notify("API client not initialized", severity="error")
            return

        try:
            self.categories = await self.client.get_categories()
            self.log(f"Loaded {len(self.categories)} categories")

            # Update the entry list screen if it exists
            entry_list_screen = self._get_entry_list_screen()
            if entry_list_screen:
                entry_list_screen.categories = self.categories
        except Exception as e:
            error_details = traceback.format_exc()
            self.notify(f"Error loading categories: {e}", severity="error")
            self.log(f"Full error:\n{error_details}")

    async def _build_entry_category_mapping(self) -> dict[int, int]:
        """Build a mapping of entry_id → category_id using the category API.

        Since the feeds endpoint doesn't include category_id, we use a different
        approach: fetch entries from each category and build a mapping.

        Returns:
            Dictionary mapping entry_id to category_id
        """
        if not self.client or not self.categories:
            self.log("Skipping category mapping: no client or categories")
            return {}

        entry_category_map: dict[int, int] = {}
        self.log(f"Building entry→category mapping from {len(self.categories)} categories...")

        for category in self.categories:
            try:
                # Fetch all entries in this category
                category_entries = await self.client.get_category_entries(category.id, limit=10000)
                self.log(f"  Category {category.id} ({category.title}): {len(category_entries)} entries")

                # Map each entry to this category
                for entry in category_entries:
                    entry_category_map[entry.id] = category.id
                    self.log(f"    ✓ Entry {entry.id} → Category {category.id}")

            except Exception as e:
                self.log(f"  ✗ Category {category.id}: failed to fetch entries - {e}")

        self.log(f"Built mapping for {len(entry_category_map)} entries across categories")
        return entry_category_map

    def _enrich_entries_with_category_mapping(self, entries: list, entry_category_map: dict[int, int]) -> list:
        """
        Enrich entries with category_id using a pre-built entry→category mapping.

        Args:
            entries: List of entries to enrich
            entry_category_map: Dictionary mapping entry_id to category_id

        Returns:
            List of entries with category information populated
        """
        self.log(f"Applying category mapping to {len(entries)} entries")
        self.log(f"Entry→category mapping has {len(entry_category_map)} entries")

        enriched_count = 0
        for entry in entries:
            if entry.id in entry_category_map:
                category_id = entry_category_map[entry.id]
                entry.feed.category_id = category_id
                enriched_count += 1
                self.log(f"  ✓ Entry {entry.id}: set category_id = {category_id}")
            else:
                self.log(f"  - Entry {entry.id}: not in any category")

        self.log(f"Applied category mapping to {enriched_count}/{len(entries)} entries")
        return entries

    async def load_entries(self, view: str = "unread") -> None:
        """
        Load entries from Miniflux API.

        Args:
            view: View type - "unread" or "starred"
        """
        if not self.client:
            self.notify("API client not initialized", severity="error")
            return

        try:
            if view == "starred":
                self.entries = await self.client.get_starred_entries(limit=DEFAULT_ENTRY_LIMIT)
                self.current_view = "starred"
                self.notify(f"Loaded {len(self.entries)} starred entries")
            else:
                self.entries = await self.client.get_unread_entries(limit=DEFAULT_ENTRY_LIMIT)
                self.current_view = "unread"
                self.notify(f"Loaded {len(self.entries)} unread entries")

            # Enrich entries with category information using the mapping
            if self.entry_category_map:
                self.entries = self._enrich_entries_with_category_mapping(self.entries, self.entry_category_map)

            # Update the entry list screen if it exists
            entry_list_screen = self._get_entry_list_screen()
            if entry_list_screen:
                self.log("entry_list screen is installed")
                self.log(f"Updating screen with {len(self.entries)} entries")
                entry_list_screen.entries = self.entries
                entry_list_screen._populate_list()
            else:
                self.log("entry_list screen is NOT installed!")

            # Show message if no entries
            if len(self.entries) == 0:
                self.notify(f"No {view} entries found", severity="warning")

        except Exception as e:
            error_details = traceback.format_exc()
            self.notify(f"Error loading entries: {e}", severity="error")
            # Log full error for debugging
            self.log(f"Full error:\n{error_details}")

    def push_entry_reader(self, entry: Entry, entry_list: list | None = None, current_index: int = 0) -> None:
        """
        Push entry reader screen for a specific entry.

        Args:
            entry: Entry to display
            entry_list: Full list of entries for navigation
            current_index: Current position in the entry list
        """
        entry_reader_module = import_module("miniflux_tui.ui.screens.entry_reader")
        entry_reader_cls: type[EntryReaderScreen]
        entry_reader_cls = entry_reader_module.EntryReaderScreen

        reader_screen: EntryReaderScreen = entry_reader_cls(
            entry=entry,
            entry_list=entry_list or self.entries,
            current_index=current_index,
            unread_color=self.config.unread_color,
            read_color=self.config.read_color,
        )
        self.push_screen(reader_screen)

    async def action_refresh_entries(self) -> None:
        """Refresh entries from API."""
        # Rebuild category mapping and reload entries
        self.entry_category_map = await self._build_entry_category_mapping()
        await self.load_entries(self.current_view)
        self.notify("Entries refreshed")

    async def action_show_unread(self) -> None:
        """Show unread entries."""
        await self.load_entries("unread")
        self.notify("Showing unread entries")

    async def action_show_starred(self) -> None:
        """Show starred entries."""
        await self.load_entries("starred")
        self.notify("Showing starred entries")

    async def load_feeds(self) -> None:
        """Load feeds from Miniflux API.

        Note: Category information is obtained via the category API, not from
        individual feeds (which don't expose category_id on all Miniflux versions).
        """
        if not self.client:
            self.notify("API client not initialized", severity="error")
            return

        try:
            self.feeds = await self.client.get_feeds()
            self.log(f"Loaded {len(self.feeds)} feeds")
            # Note: Category information will be obtained from category API via _build_entry_category_mapping()
        except Exception as e:
            error_details = traceback.format_exc()
            self.notify(f"Error loading feeds: {e}", severity="error")
            self.log(f"Full error:\n{error_details}")

    def push_feed_management_screen(self) -> None:
        """Push feed management screen."""
        feed_management_module = import_module("miniflux_tui.ui.screens.feed_management")
        feed_management_cls: type[FeedManagementScreen]
        feed_management_cls = feed_management_module.FeedManagementScreen

        management_screen: FeedManagementScreen = feed_management_cls(feeds=self.feeds)
        self.push_screen(management_screen)

    async def push_category_management_screen(self) -> None:
        """Push category management screen."""
        try:
            categories = await self.client.get_categories() if self.client else []
        except Exception:
            categories = []

        from miniflux_tui.ui.screens.category_management import (  # noqa: PLC0415
            CategoryManagementScreen,
        )

        management_screen = CategoryManagementScreen(categories=categories)
        self.push_screen(management_screen)

    async def on_unmount(self) -> None:
        """Called when app is unmounted."""
        # Close API client
        if self.client:
            await self.client.close()


async def run_tui(config: Config) -> None:
    """
    Run the Miniflux TUI application.

    Args:
        config: Application configuration
    """
    app = MinifluxTuiApp(config)
    await app.run_async()
