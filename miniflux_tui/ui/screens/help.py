"""Help screen showing keyboard shortcuts and application information."""

import platform
import sys

import textual
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from miniflux_tui.utils import get_app_version


class HelpScreen(Screen):
    """Screen displaying keyboard shortcuts and help information."""

    BINDINGS: list[Binding] = [  # noqa: RUF012
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
    ]

    def __init__(self, **kwargs):
        """Initialize help screen with server info placeholders."""
        super().__init__(**kwargs)
        self.server_version: str = "Loading..."
        self.api_version: str = "Loading..."
        self.username: str = "Loading..."

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with VerticalScroll():
            yield Static("[bold cyan]Miniflux TUI - Keyboard Shortcuts[/bold cyan]\n")

            yield Static("[bold yellow]Entry List View[/bold yellow]")
            yield Static("  ↑/↓ or k/j      Navigate entries")
            yield Static("  Enter           Open entry")
            yield Static("  m               Toggle read/unread")
            yield Static("  *               Toggle star")
            yield Static("  e               Save entry to third-party service")
            yield Static("  s               Cycle sort mode (date/feed/status)")
            yield Static("  g               Toggle grouping by feed")
            yield Static("  Shift+G         Expand all feeds")
            yield Static("  Shift+Z         Collapse all feeds")
            yield Static("  o               Toggle fold/unfold on feed header")
            yield Static("  h or ←          Collapse individual feed")
            yield Static("  l or →          Expand individual feed")
            yield Static("  r or ,          Refresh entries")
            yield Static("  u               Show unread entries")
            yield Static("  t               Show starred entries")
            yield Static("  ?               Show this help")
            yield Static("  q               Quit application\n")

            yield Static("[bold yellow]Entry Reader View[/bold yellow]")
            yield Static("  ↑/↓ or k/j      Scroll up/down")
            yield Static("  PageUp/PageDown Fast scroll")
            yield Static("  b or Esc        Back to list")
            yield Static("  u               Mark as unread")
            yield Static("  *               Toggle star")
            yield Static("  e               Save entry to third-party service")
            yield Static("  o               Open in browser")
            yield Static("  f               Fetch original content")
            yield Static("  J               Next entry")
            yield Static("  K               Previous entry")
            yield Static("  ?               Show this help\n")

            yield Static("[bold yellow]About[/bold yellow]")
            yield Static(self._get_about_text())
            yield Static()

            yield Static("[bold yellow]System Information[/bold yellow]")
            yield Static(self._get_system_info_text())
            yield Static()

            yield Static("[dim]Press Esc or q to close this help screen[/dim]")

        yield Footer()

    def _get_about_text(self) -> str:
        """Generate about section text with application information.

        Returns:
            Formatted text with app info
        """
        app_version = get_app_version()
        return (
            f"  Application:     Miniflux TUI\n"
            f"  Version:         {app_version}\n"
            f"  Repository:      github.com/reuteras/miniflux-tui-py\n"
            f"  License:         MIT"
        )

    def _get_system_info_text(self) -> str:
        """Generate system information text.

        Returns:
            Formatted text with system and server info
        """
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        platform_name = platform.system()

        return (
            f"  Python:          {python_version}\n"
            f"  Platform:        {platform_name}\n"
            f"  Textual:         {textual.__version__}\n"
            f"  Miniflux API:    {self.api_version}\n"
            f"  Miniflux Server: {self.server_version}\n"
            f"  Username:        {self.username}"
        )

    async def on_mount(self) -> None:
        """Called when screen is mounted - load server information."""
        await self._load_server_info()

    async def _load_server_info(self) -> None:
        """Load server version and user information from API."""
        if not hasattr(self.app, "client") or not getattr(self.app, "client", None):
            self.api_version = "unavailable"
            self.server_version = "unavailable"
            self.username = "unavailable"
            return

        try:
            client = getattr(self.app, "client", None)
            # Get version info
            version_info = await client.get_version()
            self.api_version = version_info.get("version", "unknown")

            # Get user info
            user_info = await client.get_user_info()
            self.username = user_info.get("username", "unknown")
            self.server_version = version_info.get("version", "unknown")

            # Update the screen to show new info
            self._update_system_info()
        except Exception as e:
            self.app.log(f"Error loading server info: {e}")
            self.api_version = f"error: {type(e).__name__}"
            self.server_version = "error"
            self.username = "error"
            self._update_system_info()

    def _update_system_info(self) -> None:
        """Update the system information display."""
        # Find and update the system info widget
        for widget in self.query("Static"):
            if (
                hasattr(widget, "renderable")
                and widget.renderable  # type: ignore[attr-defined]
                and isinstance(widget.renderable, str)  # type: ignore[attr-defined]
                and "System Information" in str(widget.renderable)  # type: ignore[attr-defined]
            ):
                # Update the next static widget with system info
                widgets = list(self.query("Static"))
                for i, w in enumerate(widgets):
                    if w is widget and i + 1 < len(widgets):
                        next_widget = widgets[i + 1]
                        next_widget.update(self._get_system_info_text())  # type: ignore[union-attr]
                        break

    def action_close(self):
        """Close the help screen."""
        self.app.pop_screen()
