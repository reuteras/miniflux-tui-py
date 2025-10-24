"""Help screen showing keyboard shortcuts."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class HelpScreen(Screen):
    """Screen displaying keyboard shortcuts and help information."""

    BINDINGS = [  # noqa: RUF012
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
    ]

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
            yield Static("  Version:        0.1.0")
            yield Static("  Repository:     github.com/reuteras/miniflux-tui-py")
            yield Static("  License:        MIT\n")

            yield Static("[dim]Press Esc or q to close this help screen[/dim]")

        yield Footer()

    def action_close(self):
        """Close the help screen."""
        self.app.pop_screen()
