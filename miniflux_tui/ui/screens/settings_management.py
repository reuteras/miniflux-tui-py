"""Settings screen showing user information and integrations."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class SettingsScreen(Screen):
    """Screen displaying user settings and integrations information."""

    BINDINGS: list[Binding] = [  # noqa: RUF012
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
        Binding("r", "refresh", "Refresh"),
        Binding("o", "open_web_settings", "Web Settings"),
    ]

    def __init__(self, **kwargs):
        """Initialize settings screen."""
        super().__init__(**kwargs)
        self.server_url: str = "Loading..."
        self.username: str = "Loading..."
        self.timezone: str = "Loading..."
        self.language: str = "Loading..."
        self.integrations_enabled: bool = False
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

            yield Static("[bold yellow]Integrations Status[/bold yellow]")
            yield Static(id="integrations-status")
            yield Static()

            yield Static("[dim]Press o to open web settings, r to refresh, Esc or q to close[/dim]")

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
            self.username = user_info.get("username", "unknown")
            self.timezone = user_info.get("timezone", "unknown")
            self.language = user_info.get("language", "unknown")

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

            integrations = self.query_one("#integrations-status", Static)
            integrations.update("[dim]Unable to load integrations[/dim]")
        except Exception as e:
            self.app.log(f"Could not update error state: {e}")

    def _update_display(self) -> None:
        """Update all settings displays."""
        self._update_user_info()
        self._update_display_preferences()
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
                f"  Timezone:        {self.timezone}",
                f"  Language:        {self.language}",
                "  [dim]Additional settings available in web UI[/dim]",
            ]
            widget.update("\n".join(lines))
        except Exception as e:
            self.app.log(f"Could not update display preferences: {e}")

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
