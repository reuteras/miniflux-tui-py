# SPDX-License-Identifier: MIT
"""Main Toga application for Miniflux GUI."""

import asyncio
import html
import re
import webbrowser
from typing import TYPE_CHECKING

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from miniflux_tui.api.client import MinifluxClient
from miniflux_tui.config import load_config

if TYPE_CHECKING:
    from miniflux_tui.api.models import Entry


class MinifluxGUI(toga.App):
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

    def startup(self):
        """Construct and show the Toga application.

        This is called when the app is first started.
        """
        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)

        # Load configuration
        try:
            config = load_config()
            self.client = MinifluxClient(
                base_url=config["server_url"],
                api_key=config["api_key"],
                allow_invalid_certs=config.get("allow_invalid_certs", False),
            )
        except Exception as e:
            self.show_error(f"Failed to load configuration: {e}")
            # Create a simple error screen
            self.main_window.content = self.create_config_error_screen()
            self.main_window.show()
            return

        # Create the main UI
        self.main_window.content = self.create_loading_screen()
        self.main_window.show()

        # Load entries asynchronously
        self._load_task = asyncio.create_task(self.load_entries())

    def create_config_error_screen(self) -> toga.Box:
        """Create an error screen for configuration issues."""
        error_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        error_label = toga.Label(
            "Configuration Error",
            style=Pack(padding=5, font_size=20, font_weight="bold"),
        )

        instructions = toga.Label(
            "Please run 'miniflux-tui --init' to set up your configuration.",
            style=Pack(padding=5),
        )

        error_box.add(error_label)
        error_box.add(instructions)

        return error_box

    def create_loading_screen(self) -> toga.Box:
        """Create a loading screen while entries are fetched."""
        loading_box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment="center"))

        loading_label = toga.Label(
            "Loading entries...",
            style=Pack(padding=5, font_size=16),
        )

        loading_box.add(loading_label)
        return loading_box

    async def load_entries(self):
        """Load entries from the Miniflux API."""
        if not self.client:
            return

        try:
            # Fetch unread entries
            self.entries = await self.client.get_unread_entries()

            # Update UI with entries
            self.main_window.content = self.create_entry_list_screen()
        except Exception as e:
            self.show_error(f"Failed to load entries: {e}")

    def create_entry_list_screen(self) -> toga.Box:
        """Create the entry list screen."""
        main_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Header
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))
        header_label = toga.Label(
            f"Unread Entries ({len(self.entries)})",
            style=Pack(padding=5, font_size=18, font_weight="bold", flex=1),
        )
        refresh_button = toga.Button(
            "Refresh",
            on_press=self.on_refresh,
            style=Pack(padding=5),
        )
        header_box.add(header_label)
        header_box.add(refresh_button)

        # Entry list using DetailedList
        if self.entries:
            entry_data = [
                {
                    "icon": None,
                    "title": entry.title,
                    "subtitle": f"{entry.feed.title} • {entry.published_at.strftime('%Y-%m-%d %H:%M')}",
                }
                for entry in self.entries
            ]

            entry_list = toga.DetailedList(
                data=entry_data,
                on_select=self.on_entry_select,
                style=Pack(flex=1),
            )
        else:
            entry_list = toga.Label(
                "No unread entries",
                style=Pack(padding=10, font_size=14),
            )

        main_box.add(header_box)
        main_box.add(entry_list)

        return main_box

    def on_entry_select(self, _widget, row):
        """Handle entry selection."""
        if row is None:
            return

        # Get the selected entry from the list
        self.selected_entry = self.entries[row.index] if hasattr(row, "index") else None

        if self.selected_entry:
            # Show entry detail screen
            self.main_window.content = self.create_entry_detail_screen(self.selected_entry)

    def create_entry_detail_screen(self, entry: "Entry") -> toga.Box:
        """Create the entry detail screen."""
        detail_box = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Header with back button
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))
        back_button = toga.Button(
            "← Back",
            on_press=self.on_back_to_list,
            style=Pack(padding=5),
        )
        header_box.add(back_button)

        # Entry metadata
        title_label = toga.Label(
            entry.title,
            style=Pack(padding=5, font_size=18, font_weight="bold"),
        )

        feed_label = toga.Label(
            f"Feed: {entry.feed.title}",
            style=Pack(padding=5, font_size=12),
        )

        date_label = toga.Label(
            f"Published: {entry.published_at.strftime('%Y-%m-%d %H:%M')}",
            style=Pack(padding=5, font_size=12),
        )

        # Convert HTML content to plain text (simple approach for now)
        # In production, you'd use html2text here
        content_text = html.unescape(entry.content)
        # Remove HTML tags (very basic)
        content_text = re.sub("<[^<]+?>", "", content_text)

        # Content in a scrollable container
        content_view = toga.MultilineTextInput(
            value=content_text,
            readonly=True,
            style=Pack(flex=1, padding=5),
        )

        # Action buttons
        action_box = toga.Box(style=Pack(direction=ROW, padding=5))

        mark_read_button = toga.Button(
            "Mark as Read" if entry.is_unread else "Mark as Unread",
            on_press=lambda _: asyncio.create_task(self.on_toggle_read(entry)),
            style=Pack(padding=5, flex=1),
        )

        star_button = toga.Button(
            "★ Unstar" if entry.starred else "☆ Star",
            on_press=lambda _: asyncio.create_task(self.on_toggle_star(entry)),
            style=Pack(padding=5, flex=1),
        )

        open_button = toga.Button(
            "Open in Browser",
            on_press=lambda _: self.on_open_browser(entry),
            style=Pack(padding=5, flex=1),
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
        self.main_window.content = self.create_entry_list_screen()

    def on_refresh(self, _widget):
        """Refresh the entry list."""
        self.main_window.content = self.create_loading_screen()
        self._load_task = asyncio.create_task(self.load_entries())

    async def on_toggle_read(self, entry: "Entry"):
        """Toggle the read status of an entry."""
        if not self.client:
            return

        try:
            if entry.is_unread:
                await self.client.mark_as_read(entry.id)
                entry.status = "read"
            else:
                await self.client.mark_as_unread(entry.id)
                entry.status = "unread"

            # Refresh the detail screen
            if self.selected_entry:
                self.main_window.content = self.create_entry_detail_screen(self.selected_entry)
        except Exception as e:
            self.show_error(f"Failed to toggle read status: {e}")

    async def on_toggle_star(self, entry: "Entry"):
        """Toggle the starred status of an entry."""
        if not self.client:
            return

        try:
            await self.client.toggle_starred(entry.id)
            entry.starred = not entry.starred

            # Refresh the detail screen
            if self.selected_entry:
                self.main_window.content = self.create_entry_detail_screen(self.selected_entry)
        except Exception as e:
            self.show_error(f"Failed to toggle star status: {e}")

    def on_open_browser(self, entry: "Entry"):
        """Open the entry URL in the default browser."""
        webbrowser.open(entry.url)

    def show_error(self, message: str):
        """Show an error dialog."""
        self.main_window.error_dialog("Error", message)


def main():
    """Entry point for the GUI application."""
    return MinifluxGUI()
