# SPDX-License-Identifier: MIT
"""Settings screen showing user information and integrations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from miniflux_tui.ui.screens.settings_edit_dialog import SettingsEditDialog

if TYPE_CHECKING:
    pass


class SettingsScreen(Screen):
    """Screen displaying user settings and integrations information."""

    BINDINGS: list[Binding] = [  # noqa: RUF012
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
        Binding("r", "refresh", "Refresh"),
        Binding("o", "open_web_settings", "Web Settings"),
        Binding("e", "edit_settings", "Edit"),
        Binding("i", "toggle_info_messages", "Toggle Info Messages"),
    ]

    def __init__(self, **kwargs):
        """Initialize settings screen."""
        super().__init__(**kwargs)
        self.server_url: str = "Loading..."
        self.username: str = "Loading..."
        self.timezone: str = "Loading..."
        self.language: str = "Loading..."
        self.theme: str = "Loading..."
        self.entries_per_page: int = 0
        self.keyboard_shortcuts: bool = True
        self.show_reading_time: bool = True
        self.mark_read_on_view: bool = False
        self.entry_sorting_order: str = "Loading..."
        self.entry_sorting_direction: str = "Loading..."
        self.integrations_enabled: bool = False
        self.user_id: int = 0
        self._user_data: dict = {}
        self._header_widget: Header | None = None
        self._scroll_container: VerticalScroll | None = None
        self._footer_widget: Footer | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        header = Header()
        scroll = VerticalScroll()
        footer = Footer()

        self._header_widget = header
        self._scroll_container = scroll
        self._footer_widget = footer

        yield header

        with scroll:
            yield Static("[bold cyan]User Settings[/bold cyan]\n", id="title")

            yield Static("[bold yellow]User Information[/bold yellow]")
            yield Static(id="user-info")
            yield Static()

            yield Static("[bold yellow]Display Preferences[/bold yellow]")
            yield Static(id="display-prefs")
            yield Static()

            yield Static("[bold yellow]Reading Preferences[/bold yellow]")
            yield Static(id="reading-prefs")
            yield Static()

            yield Static("[bold yellow]TUI Configuration[/bold yellow]")
            yield Static(id="tui-config")
            yield Static()

            yield Static("[bold yellow]Integrations Status[/bold yellow]")
            yield Static(id="integrations-status")
            yield Static()

            yield Static("[dim]Press i to toggle info messages, e to edit, o for web settings, r to refresh, Esc or q to close[/dim]")

        yield footer

    async def on_mount(self) -> None:
        """Called when screen is mounted - load settings information."""
        await self._load_settings()

    async def _load_settings(self) -> None:
        """Load user settings and integrations from API."""
        if not hasattr(self.app, "client") or not getattr(self.app, "client", None):
            self._update_error_state("API client not available")
            return

        try:
            client = getattr(self.app, "client", None)
            self.server_url = client.base_url

            # Get user info
            user_info = await client.get_user_info()
            self._user_data = user_info
            self.user_id = user_info.get("id", 0)
            self.username = user_info.get("username", "unknown")
            self.timezone = user_info.get("timezone", "UTC")
            self.language = user_info.get("language", "en_US")
            self.theme = user_info.get("theme", "system_serif")
            self.entries_per_page = user_info.get("entries_per_page", 100)
            self.keyboard_shortcuts = user_info.get("keyboard_shortcuts", True)
            self.show_reading_time = user_info.get("show_reading_time", True)
            self.mark_read_on_view = user_info.get("mark_read_on_view", False)
            self.entry_sorting_order = user_info.get("entry_sorting_order", "published_at")
            self.entry_sorting_direction = user_info.get("entry_sorting_direction", "desc")

            # Get integrations status
            self.integrations_enabled = await client.get_integrations_status()

            # Update the display
            self._update_display()

        except Exception as e:
            self.app.log(f"Error loading settings: {e}")
            self._update_error_state(f"Error: {type(e).__name__}: {e}")

    def _update_error_state(self, error_message: str) -> None:
        """Update display when an error occurs."""
        try:
            user_info = self.query_one("#user-info", Static)
            user_info.update(f"[red]{error_message}[/red]")

            display_prefs = self.query_one("#display-prefs", Static)
            display_prefs.update("[dim]Unable to load display preferences[/dim]")

            reading_prefs = self.query_one("#reading-prefs", Static)
            reading_prefs.update("[dim]Unable to load reading preferences[/dim]")

            integrations = self.query_one("#integrations-status", Static)
            integrations.update("[dim]Unable to load integrations[/dim]")
        except Exception as e:
            self.app.log(f"Could not update error state: {e}")

    def _update_display(self) -> None:
        """Update all settings displays."""
        self._update_user_info()
        self._update_display_preferences()
        self._update_reading_preferences()
        self._update_tui_config()
        self._update_integrations()

    def _update_user_info(self) -> None:
        """Update the user information display."""
        try:
            widget = self.query_one("#user-info", Static)
            lines = [
                f"  Username:        {self.username}",
                f"  Server:          {self.server_url}",
            ]
            widget.update("\n".join(lines))
        except Exception as e:
            self.app.log(f"Could not update user info: {e}")

    def _update_display_preferences(self) -> None:
        """Update the display preferences display."""
        try:
            widget = self.query_one("#display-prefs", Static)
            lines = [
                f"  Theme:           {self.theme}",
                f"  Timezone:        {self.timezone}",
                f"  Language:        {self.language}",
                f"  Entries/Page:    {self.entries_per_page}",
            ]
            widget.update("\n".join(lines))
        except Exception as e:
            self.app.log(f"Could not update display preferences: {e}")

    def _update_reading_preferences(self) -> None:
        """Update the reading preferences display."""
        try:
            widget = self.query_one("#reading-prefs", Static)
            lines = [
                f"  Sort Order:      {self.entry_sorting_order}",
                f"  Sort Direction:  {self.entry_sorting_direction}",
                f"  Keyboard Shortcuts: {'Enabled' if self.keyboard_shortcuts else 'Disabled'}",
                f"  Show Reading Time:  {'Yes' if self.show_reading_time else 'No'}",
                f"  Mark Read on View:  {'Yes' if self.mark_read_on_view else 'No'}",
                "  [dim]Edit settings with 'e' key[/dim]",
            ]
            widget.update("\n".join(lines))
        except Exception as e:
            self.app.log(f"Could not update reading preferences: {e}")

    def _update_tui_config(self) -> None:
        """Update the TUI configuration display."""
        try:
            widget = self.query_one("#tui-config", Static)

            # Get config from app
            config = getattr(self.app, "config", None)
            if config:
                show_info = getattr(self.app, "show_info_messages", config.show_info_messages)

                lines = [
                    f"  Show Info Messages:  {'Enabled' if show_info else 'Disabled'}",
                    f"  Unread Color:        {config.unread_color}",
                    f"  Read Color:          {config.read_color}",
                    f"  Default Sort:        {config.default_sort}",
                    f"  Group by Feed:       {'Yes' if config.default_group_by_feed else 'No'}",
                    "  [dim]Press 'i' to toggle info messages[/dim]",
                    "  [dim]Edit config file to change other settings[/dim]",
                ]
                widget.update("\n".join(lines))
            else:
                widget.update("[dim]TUI configuration not available[/dim]")
        except Exception as e:
            self.app.log(f"Could not update TUI config: {e}")

    def _update_integrations(self) -> None:
        """Update the integrations display."""
        try:
            widget = self.query_one("#integrations-status", Static)

            if self.integrations_enabled:
                text = (
                    "  [green]At least one third-party integration is enabled ✓[/green]\n"
                    "  [dim]Manage integrations in web UI (server_url/integrations)[/dim]"
                )
            else:
                text = "  [dim]No integrations enabled[/dim]"

            widget.update(text)
        except Exception as e:
            self.app.log(f"Could not update integrations: {e}")

    def action_toggle_info_messages(self):
        """Toggle the display of information messages."""
        toggle_func = getattr(self.app, "toggle_info_messages", None)
        if toggle_func and callable(toggle_func):
            toggle_func()
            # Update the display to show the new state
            self._update_tui_config()

    def action_close(self):
        """Close the settings screen."""
        self.app.pop_screen()

    async def action_refresh(self):
        """Refresh the settings information."""
        # Show loading message
        try:
            user_info = self.query_one("#user-info", Static)
            user_info.update("[dim]Refreshing...[/dim]")
        except Exception as e:
            # Widget might not be mounted yet, silently continue
            self.app.log(f"Could not update refresh message: {e}")

        # Reload settings
        await self._load_settings()

        # Notify user
        self.app.notify("Settings refreshed")

    def action_open_web_settings(self):
        """Open web UI for advanced settings."""
        if self.server_url and self.server_url != "Loading...":
            settings_url = f"{self.server_url}/settings"
            self.app.notify(f"To manage advanced settings, visit: {settings_url}")
        else:
            self.app.notify("Server URL not available")

    def action_edit_settings(self):
        """Open dialog to edit user settings."""
        if not self.user_id:
            self.app.notify("User information not loaded yet", severity="warning")
            return

        def handle_save(updated_settings: dict | None) -> None:
            """Handle saved settings from dialog."""
            if updated_settings:
                self.run_worker(self._save_settings(updated_settings))

        # Prepare current settings for the dialog
        current_settings = {
            "timezone": self.timezone,
            "language": self.language,
            "theme": self.theme,
            "entries_per_page": self.entries_per_page,
            "entry_sorting_order": self.entry_sorting_order,
            "entry_sorting_direction": self.entry_sorting_direction,
            "keyboard_shortcuts": self.keyboard_shortcuts,
            "show_reading_time": self.show_reading_time,
            "mark_read_on_view": self.mark_read_on_view,
        }

        self.app.push_screen(SettingsEditDialog(current_settings), handle_save)

    async def _save_settings(self, updated_settings: dict) -> None:
        """Save updated settings to the server."""
        if not hasattr(self.app, "client") or not getattr(self.app, "client", None):
            self.app.notify("API client not available", severity="error")
            return

        try:
            client = getattr(self.app, "client", None)
            self.app.notify("Saving settings...")

            # Update user settings via API
            await client.update_user_settings(self.user_id, **updated_settings)

            self.app.notify("Settings saved successfully!", severity="information")

            # Reload settings to reflect changes
            await self._load_settings()

        except Exception as e:
            error_msg = f"Error saving settings: {type(e).__name__}: {e}"
            self.app.log(error_msg)
            # Show actual error in notification so user knows what went wrong
            short_error = str(e)[:100]  # Limit to 100 chars for notification
            self.app.notify(f"Failed to save: {short_error}", severity="error")
