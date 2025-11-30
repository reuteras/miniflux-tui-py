# SPDX-License-Identifier: MIT
"""Main Toga application for Miniflux GUI."""

import asyncio
import html
import re
import sys
import threading
import traceback
import webbrowser
from contextlib import suppress
from typing import TYPE_CHECKING, Literal

import html2text
import toga  # type: ignore[import-untyped]
from toga.style import Pack  # type: ignore[import-untyped]
from toga.style.pack import COLUMN, ROW  # type: ignore[attr-defined]

from miniflux_tui.api.client import MinifluxClient

if TYPE_CHECKING:
    from miniflux_tui.api.models import Entry

ViewMode = Literal["unread", "starred", "all"]

# Dark theme colors
DARK_BG = "#1a1a1a"  # Main background
DARK_BG_SECONDARY = "#2d2d2d"  # Secondary background (cards, inputs)
DARK_TEXT = "#e0e0e0"  # Primary text
DARK_TEXT_DIM = "#a0a0a0"  # Secondary text
DARK_ACCENT = "#4a9eff"  # Accent color (buttons, links)
DARK_SUCCESS = "#50c878"  # Success color
DARK_ERROR = "#ff6b6b"  # Error color


class MinifluxGUI(toga.App):  # pylint: disable=inherit-non-class
    """Main Toga application for Miniflux reader."""

    def __init__(self):
        """Initialize the Toga app."""
        super().__init__(
            "Miniflux Reader",
            "com.reuteras.miniflux",
        )
        self.client: MinifluxClient | None = None
        self.entries: list[Entry] = []
        self.selected_entry: Entry | None = None
        self.current_view: ViewMode = "unread"

        # Initialize html2text converter
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.ignore_emphasis = False
        self.html_converter.body_width = 0  # Don't wrap text

    def _run_async(self, coro):
        """Run an async coroutine in a background thread with its own event loop."""

        def run_in_thread():
            try:
                print(f"[DEBUG] Starting async operation: {coro}", flush=True)
                asyncio.run(coro)
                print("[DEBUG] Async operation completed successfully", flush=True)
            except Exception as e:
                print(f"[ERROR] Async operation failed: {e}", flush=True)
                traceback.print_exc()

        print("[DEBUG] Starting background thread", flush=True)
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

    def _load_settings(self) -> dict[str, str] | None:
        """Load settings from platform-specific storage."""
        if sys.platform == "ios":
            from rubicon.objc import ObjCClass  # type: ignore[import-untyped]  # noqa: PLC0415

            NSUserDefaults = ObjCClass("NSUserDefaults")  # type: ignore[attr-defined]  # pylint: disable=invalid-name  # noqa: N806
            defaults = NSUserDefaults.standardUserDefaults
            server_url = defaults.stringForKey("miniflux_server_url")
            api_key = defaults.stringForKey("miniflux_api_key")

            if server_url and api_key:
                return {
                    "server_url": str(server_url),
                    "api_key": str(api_key),
                }
        return None

    def _save_settings(self, server_url: str, api_key: str):
        """Save settings to platform-specific storage."""
        if sys.platform == "ios":
            from rubicon.objc import ObjCClass  # type: ignore[import-untyped]  # noqa: PLC0415

            NSUserDefaults = ObjCClass("NSUserDefaults")  # type: ignore[attr-defined]  # pylint: disable=invalid-name  # noqa: N806
            defaults = NSUserDefaults.standardUserDefaults
            defaults.setObject_forKey_(server_url, "miniflux_server_url")
            defaults.setObject_forKey_(api_key, "miniflux_api_key")
            defaults.synchronize()

    def startup(self):
        """Construct and show the Toga application.

        This is called when the app is first started.
        """
        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)

        # Try to load settings (iOS) or config file (desktop)
        config = None
        if sys.platform == "ios":
            config = self._load_settings()

        # Always show settings screen first - avoid startup async issues
        # After user saves settings, we'll load entries
        if not config:
            self.main_window.content = self.create_settings_screen(first_run=True)  # type: ignore[attr-defined]
        else:
            # Pre-configure client but don't load yet
            try:
                self.client = MinifluxClient(
                    base_url=config["server_url"],
                    api_key=config["api_key"],
                    allow_invalid_certs=config.get("allow_invalid_certs", False),
                    timeout=15.0,  # 15 second timeout
                )
            except Exception as e:
                self._show_error_screen(
                    "Configuration Error",
                    f"Failed to initialize client: {e}",
                    "Please check your settings.",
                    show_settings_button=True,
                )
                self.main_window.show()  # type: ignore[attr-defined]
                return

            # Show welcome screen with Connect button instead of auto-loading
            self.main_window.content = self.create_welcome_screen()  # type: ignore[attr-defined]

        self.main_window.show()  # type: ignore[attr-defined]

    def create_welcome_screen(self) -> toga.Box:
        """Create a welcome screen with Connect button."""
        welcome_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                margin=20,
                align_items="center",
                background_color=DARK_BG,
            )
        )

        welcome_label = toga.Label(
            "Ready to Connect",
            style=Pack(margin=10, font_size=20, font_weight="bold", color=DARK_TEXT),
        )

        info_label = toga.Label(
            "Your server settings are configured.\nTap Connect to load your feeds.",
            style=Pack(margin=10, font_size=14, color=DARK_TEXT_DIM),
        )

        connect_button = toga.Button(
            "Connect",
            on_press=self.on_connect,
            style=Pack(margin=10, background_color=DARK_ACCENT, color=DARK_TEXT),
        )

        settings_button = toga.Button(
            "⚙️ Settings",
            on_press=lambda _: self._show_settings(),
            style=Pack(margin=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
        )

        welcome_box.add(welcome_label)
        welcome_box.add(info_label)
        welcome_box.add(connect_button)
        welcome_box.add(settings_button)

        return welcome_box

    def on_connect(self, _widget):
        """Connect and load entries."""
        self.main_window.content = self.create_loading_screen("Connecting to server...")  # type: ignore[attr-defined]
        self._run_async(self._safe_load_entries())

    def create_settings_screen(self, first_run: bool = False) -> toga.Box:
        """Create the settings screen for server configuration."""
        settings_box = toga.Box(style=Pack(direction=COLUMN, margin=20, background_color=DARK_BG))

        # Title
        title_label = toga.Label(
            "Miniflux Server Settings" if first_run else "Settings",
            style=Pack(margin=10, font_size=20, font_weight="bold", color=DARK_TEXT),
        )

        if first_run:
            intro_label = toga.Label(
                "Configure your server:",
                style=Pack(margin=5, font_size=14, color=DARK_TEXT_DIM),
            )
            settings_box.add(intro_label)

        settings_box.add(title_label)

        # Server URL input
        url_label = toga.Label(
            "Server URL:",
            style=Pack(margin_top=10, margin_bottom=5, font_size=14, color=DARK_TEXT),
        )
        self.server_url_input = toga.TextInput(
            placeholder="https://miniflux.example.com",
            style=Pack(margin=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
        )

        # API Key input
        api_key_label = toga.Label(
            "API Key:",
            style=Pack(margin_top=10, margin_bottom=5, font_size=14, color=DARK_TEXT),
        )
        self.api_key_input = toga.TextInput(
            placeholder="Your Miniflux API key",
            style=Pack(margin=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
        )

        # Load existing settings if available
        if not first_run and sys.platform == "ios":
            config = self._load_settings()
            if config:
                self.server_url_input.value = config.get("server_url", "")
                self.api_key_input.value = config.get("api_key", "")

        # Save button
        save_button = toga.Button(
            "Save & Connect",
            on_press=self.on_save_settings,
            style=Pack(margin=10, background_color=DARK_SUCCESS, color=DARK_TEXT),
        )

        # Back button (only if not first run)
        if not first_run:
            back_button = toga.Button(
                "← Back",
                on_press=lambda _: self._return_to_list(),
                style=Pack(margin=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
            )
            settings_box.add(back_button)

        settings_box.add(url_label)
        settings_box.add(self.server_url_input)
        settings_box.add(api_key_label)
        settings_box.add(self.api_key_input)
        settings_box.add(save_button)

        return settings_box

    def on_save_settings(self, _widget):
        """Save settings and connect to server."""
        server_url = self.server_url_input.value.strip()
        api_key = self.api_key_input.value.strip()

        # Validate inputs
        if not server_url or not api_key:
            self.show_error("Please enter both server URL and API key.")
            return

        # Save settings
        self._save_settings(server_url, api_key)

        # Create client
        try:
            self.client = MinifluxClient(
                base_url=server_url,
                api_key=api_key,
                allow_invalid_certs=False,
            )
        except Exception as e:
            self.show_error(f"Failed to create client: {e}")
            return

        # Load entries
        self.main_window.content = self.create_loading_screen("Connecting to server...")  # type: ignore[attr-defined]
        self._run_async(self._safe_load_entries())

    def _return_to_list(self):
        """Return to the entry list screen."""
        if self.client:
            self.main_window.content = self.create_entry_list_screen()  # type: ignore[attr-defined]
        else:
            self.show_error("No connection established. Please configure settings first.")

    def _show_error_screen(self, title: str, error: str, suggestion: str = "", show_settings_button: bool = False):
        """Show an error screen with details and suggestion."""
        error_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                margin=20,
                align_items="center",
                background_color=DARK_BG,
            )
        )

        error_title = toga.Label(
            title,
            style=Pack(margin=10, font_size=20, font_weight="bold", color=DARK_ERROR),
        )

        error_message = toga.Label(
            error,
            style=Pack(margin=5, font_size=14, color=DARK_TEXT),
        )

        error_box.add(error_title)
        error_box.add(error_message)

        if suggestion:
            suggestion_label = toga.Label(
                suggestion,
                style=Pack(margin=5, font_size=12, color=DARK_TEXT_DIM),
            )
            error_box.add(suggestion_label)

        # Button container
        button_box = toga.Box(style=Pack(direction=ROW, margin=10))

        # Add retry button
        retry_button = toga.Button(
            "Retry",
            on_press=self._retry_load,
            style=Pack(margin=5, background_color=DARK_ACCENT, color=DARK_TEXT),
        )
        button_box.add(retry_button)

        # Add settings button if requested
        if show_settings_button:
            settings_button = toga.Button(
                "⚙️ Settings",
                on_press=lambda _: self._show_settings(),
                style=Pack(margin=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
            )
            button_box.add(settings_button)

        error_box.add(button_box)

        self.main_window.content = error_box  # type: ignore[attr-defined]
        self.main_window.show()  # type: ignore[attr-defined]

    def _retry_load(self, _widget=None):
        """Retry loading entries after an error."""
        self.main_window.content = self.create_loading_screen("Retrying connection...")  # type: ignore[attr-defined]
        self._run_async(self._safe_load_entries())

    def create_loading_screen(self, message: str = "Loading...") -> toga.Box:
        """Create a loading screen with custom message."""
        loading_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                margin=20,
                align_items="center",
                background_color=DARK_BG,
            )
        )

        loading_label = toga.Label(
            message,
            style=Pack(margin=10, font_size=16, color=DARK_TEXT),
        )

        loading_box.add(loading_label)
        return loading_box

    async def _safe_load_entries(self):
        """Load entries with error handling."""
        print("[DEBUG] _safe_load_entries: Starting...", flush=True)
        try:
            print("[DEBUG] _safe_load_entries: Calling load_entries()...", flush=True)
            await self.load_entries()
            print("[DEBUG] _safe_load_entries: load_entries() completed successfully", flush=True)
        except ConnectionError as e:
            print(f"[ERROR] _safe_load_entries: ConnectionError: {e}", flush=True)
            self._show_error_screen(
                "Connection Error",
                f"Failed to connect to Miniflux server: {e}",
                "Please check your network connection and server URL.",
                show_settings_button=True,
            )
        except Exception as e:
            print(f"[ERROR] _safe_load_entries: Exception: {e}", flush=True)
            traceback.print_exc()
            self._show_error_screen(
                "Error Loading Entries",
                f"An error occurred: {e}",
                "Please try again or check your configuration.",
                show_settings_button=True,
            )

    async def load_entries(self):
        """Load entries from the Miniflux API based on current view."""
        try:
            print("[DEBUG] load_entries: Starting...", flush=True)
            print("[DEBUG] load_entries: Step 1 - Client check", flush=True)

            if not self.client:
                print("[DEBUG] load_entries: No client, returning", flush=True)
                return

            print("[DEBUG] load_entries: Step 2 - Client OK, loading entries", flush=True)

            # Load entries based on current view mode
            if self.current_view == "unread":
                print("[DEBUG] load_entries: Step 3 - Calling get_unread_entries", flush=True)
                self.entries = await self.client.get_unread_entries()
            elif self.current_view == "starred":
                print("[DEBUG] load_entries: Step 3 - Calling get_starred_entries", flush=True)
                self.entries = await self.client.get_starred_entries()
            else:  # all
                print("[DEBUG] load_entries: Step 3 - Calling get all entries", flush=True)
                # Get both unread and read entries (limited)
                unread = await self.client.get_unread_entries()
                read = await self.client.get_read_entries(limit=50)
                self.entries = unread + read
                # Sort by published date, newest first
                self.entries.sort(key=lambda e: e.published_at, reverse=True)

            print(f"[DEBUG] load_entries: Step 4 - Loaded {len(self.entries)} entries", flush=True)
            print("[DEBUG] load_entries: Step 5 - Updating UI", flush=True)
            # Update UI with entries
            self.main_window.content = self.create_entry_list_screen()  # type: ignore[attr-defined]
            print("[DEBUG] load_entries: Step 6 - UI updated", flush=True)
        except Exception as e:
            print(f"[ERROR] load_entries: Exception at some step: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            raise

    def create_entry_list_screen(self) -> toga.Box:
        """Create the entry list screen with navigation."""
        main_box = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color=DARK_BG))

        # Navigation bar with view mode buttons
        nav_box = toga.Box(style=Pack(direction=ROW, padding=5, background_color=DARK_BG))

        unread_button = toga.Button(
            f"📬 Unread ({len([e for e in self.entries if e.is_unread]) if self.current_view != 'unread' else len(self.entries)})",
            on_press=lambda _: self._switch_view("unread"),
            style=Pack(
                padding=3,
                flex=1,
                background_color=DARK_ACCENT if self.current_view == "unread" else DARK_BG_SECONDARY,
                color=DARK_TEXT,
            ),
        )

        starred_button = toga.Button(
            "⭐ Starred",
            on_press=lambda _: self._switch_view("starred"),
            style=Pack(
                padding=3,
                flex=1,
                background_color=DARK_ACCENT if self.current_view == "starred" else DARK_BG_SECONDARY,
                color=DARK_TEXT,
            ),
        )

        all_button = toga.Button(
            "📚 All",
            on_press=lambda _: self._switch_view("all"),
            style=Pack(
                padding=3,
                flex=1,
                background_color=DARK_ACCENT if self.current_view == "all" else DARK_BG_SECONDARY,
                color=DARK_TEXT,
            ),
        )

        nav_box.add(unread_button)
        nav_box.add(starred_button)
        nav_box.add(all_button)

        # Header with title and buttons
        header_box = toga.Box(style=Pack(direction=ROW, padding=5, background_color=DARK_BG))

        view_titles = {
            "unread": "Unread Entries",
            "starred": "Starred Entries",
            "all": "All Entries",
        }

        header_label = toga.Label(
            f"{view_titles[self.current_view]} ({len(self.entries)})",
            style=Pack(padding=5, font_size=18, font_weight="bold", flex=1, color=DARK_TEXT),
        )

        settings_button = toga.Button(
            "⚙️",
            on_press=lambda _: self._show_settings(),
            style=Pack(padding=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
        )

        refresh_button = toga.Button(
            "🔄",
            on_press=self.on_refresh,
            style=Pack(padding=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
        )

        header_box.add(header_label)
        header_box.add(settings_button)
        header_box.add(refresh_button)

        # Entry list using DetailedList
        if self.entries:
            entry_data = [
                {
                    "icon": "⭐" if entry.starred else ("📭" if entry.is_read else "📬"),
                    "title": entry.title,
                    "subtitle": f"{entry.feed.title} • {entry.published_at.strftime('%Y-%m-%d %H:%M')}",
                }
                for entry in self.entries
            ]

            entry_list = toga.DetailedList(
                data=entry_data,
                on_select=self.on_entry_select,
                style=Pack(flex=1, background_color=DARK_BG),
            )
        else:
            empty_messages = {
                "unread": "No unread entries! 🎉",
                "starred": "No starred entries yet. Star some articles to see them here!",
                "all": "No entries found.",
            }

            entry_list = toga.Label(
                empty_messages[self.current_view],
                style=Pack(padding=20, font_size=14, text_align="center", color=DARK_TEXT_DIM),
            )

        main_box.add(nav_box)
        main_box.add(header_box)
        main_box.add(entry_list)

        return main_box

    def _switch_view(self, view_mode: ViewMode):
        """Switch between different view modes."""
        if self.current_view == view_mode:
            return  # Already in this view

        self.current_view = view_mode
        self.main_window.content = self.create_loading_screen(f"Loading {view_mode} entries...")  # type: ignore[attr-defined]
        self._run_async(self._safe_load_entries())

    def _show_settings(self):
        """Show the settings screen."""
        self.main_window.content = self.create_settings_screen(first_run=False)  # type: ignore[attr-defined]

    def on_entry_select(self, _widget, row):
        """Handle entry selection."""
        if row is None:
            return

        # Get the selected entry from the list
        self.selected_entry = self.entries[row.index] if hasattr(row, "index") else None

        if self.selected_entry:
            # Show entry detail screen
            self.main_window.content = self.create_entry_detail_screen(self.selected_entry)  # type: ignore[attr-defined]

    def create_entry_detail_screen(self, entry: "Entry") -> toga.Box:
        """Create the entry detail screen."""
        detail_box = toga.Box(style=Pack(direction=COLUMN, flex=1, background_color=DARK_BG))

        # Header with back button
        header_box = toga.Box(style=Pack(direction=ROW, padding=5, background_color=DARK_BG))
        back_button = toga.Button(
            "← Back",
            on_press=self.on_back_to_list,
            style=Pack(padding=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
        )
        header_box.add(back_button)

        # Entry metadata
        title_label = toga.Label(
            entry.title,
            style=Pack(padding=5, font_size=18, font_weight="bold", color=DARK_TEXT),
        )

        feed_label = toga.Label(
            f"Feed: {entry.feed.title}",
            style=Pack(padding=5, font_size=12, color=DARK_TEXT_DIM),
        )

        date_label = toga.Label(
            f"Published: {entry.published_at.strftime('%Y-%m-%d %H:%M')}",
            style=Pack(padding=5, font_size=12, color=DARK_TEXT_DIM),
        )

        # Convert HTML content to Markdown using html2text
        try:
            content_markdown = self.html_converter.handle(entry.content)
        except Exception:
            # Fallback to basic HTML stripping if html2text fails
            content_markdown = html.unescape(entry.content)
            content_markdown = re.sub("<[^<]+?>", "", content_markdown)

        # Content in a scrollable container
        content_view = toga.MultilineTextInput(
            value=content_markdown,
            readonly=True,
            style=Pack(flex=1, padding=5, background_color=DARK_BG_SECONDARY, color=DARK_TEXT),
        )

        # Action buttons
        action_box = toga.Box(style=Pack(direction=ROW, padding=5, background_color=DARK_BG))

        # Create button handler functions that capture the entry
        def toggle_read_handler(_widget):
            self._run_async(self._safe_toggle_read(entry))

        def toggle_star_handler(_widget):
            self._run_async(self._safe_toggle_star(entry))

        mark_read_button = toga.Button(
            "Mark as Read" if entry.is_unread else "Mark as Unread",
            on_press=toggle_read_handler,
            style=Pack(padding=5, flex=1, background_color=DARK_ACCENT, color=DARK_TEXT),
        )

        star_button = toga.Button(
            "★ Unstar" if entry.starred else "☆ Star",
            on_press=toggle_star_handler,
            style=Pack(padding=5, flex=1, background_color=DARK_ACCENT, color=DARK_TEXT),
        )

        open_button = toga.Button(
            "🌐 Open",
            on_press=lambda _: self.on_open_browser(entry),
            style=Pack(padding=5, flex=1, background_color=DARK_ACCENT, color=DARK_TEXT),
        )

        action_box.add(mark_read_button)
        action_box.add(star_button)
        action_box.add(open_button)

        # Assemble the detail screen
        detail_box.add(header_box)
        detail_box.add(title_label)
        detail_box.add(feed_label)
        detail_box.add(date_label)
        detail_box.add(content_view)
        detail_box.add(action_box)

        return detail_box

    def on_back_to_list(self, _widget):
        """Navigate back to entry list."""
        self.main_window.content = self.create_entry_list_screen()  # type: ignore[attr-defined]

    def on_refresh(self, _widget):
        """Refresh the entry list."""
        self.main_window.content = self.create_loading_screen("Refreshing...")  # type: ignore[attr-defined]
        self._run_async(self._safe_load_entries())

    async def _safe_toggle_read(self, entry: "Entry"):
        """Toggle read status with error handling."""
        try:
            await self.on_toggle_read(entry)
        except Exception as e:
            self.show_error(f"Failed to toggle read status: {e}")

    async def on_toggle_read(self, entry: "Entry"):
        """Toggle the read status of an entry."""
        if not self.client:
            return

        if entry.is_unread:
            await self.client.mark_as_read(entry.id)
            entry.status = "read"
        else:
            await self.client.mark_as_unread(entry.id)
            entry.status = "unread"

        # Refresh the detail screen
        if self.selected_entry:
            self.main_window.content = self.create_entry_detail_screen(self.selected_entry)  # type: ignore[attr-defined]

    async def _safe_toggle_star(self, entry: "Entry"):
        """Toggle star status with error handling."""
        try:
            await self.on_toggle_star(entry)
        except Exception as e:
            self.show_error(f"Failed to toggle star status: {e}")

    async def on_toggle_star(self, entry: "Entry"):
        """Toggle the starred status of an entry."""
        if not self.client:
            return

        await self.client.toggle_starred(entry.id)
        entry.starred = not entry.starred

        # Refresh the detail screen
        if self.selected_entry:
            self.main_window.content = self.create_entry_detail_screen(self.selected_entry)  # type: ignore[attr-defined]

    def on_open_browser(self, entry: "Entry"):
        """Open the entry URL in the default browser."""
        try:
            webbrowser.open(entry.url)
        except Exception as e:
            self.show_error(f"Failed to open browser: {e}")

    def show_error(self, message: str):
        """Show an error dialog."""
        # Fallback if error dialog fails
        with suppress(Exception):
            self.main_window.error_dialog("Error", message)  # type: ignore[attr-defined]


def main():
    """Entry point for the GUI application."""
    return MinifluxGUI()
