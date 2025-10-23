"""Entry reader screen for viewing feed entry content."""

import html2text
import webbrowser
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Markdown
from textual.binding import Binding

from ...api.models import Entry


class EntryReaderScreen(Screen):
    """Screen for reading a single feed entry."""

    BINDINGS = [
        Binding("j", "scroll_down", "Down", show=False),
        Binding("k", "scroll_up", "Up", show=False),
        Binding("pagedown", "page_down", "Page Down"),
        Binding("pageup", "page_up", "Page Up"),
        Binding("b", "back", "Back to List"),
        Binding("u", "mark_unread", "Mark Unread"),
        Binding("asterisk", "toggle_star", "Toggle Star"),
        Binding("o", "open_browser", "Open in Browser"),
        Binding("f", "fetch_original", "Fetch Original"),
        Binding("n", "next_entry", "Next Entry"),
        Binding("p", "previous_entry", "Previous Entry"),
        Binding("question_mark", "show_help", "Help"),
        Binding("escape", "back", "Back", show=False),
    ]

    def __init__(
        self,
        entry: Entry,
        unread_color: str = "cyan",
        read_color: str = "gray",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entry = entry
        self.unread_color = unread_color
        self.read_color = read_color
        self.scroll_container = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        # Create scrollable container
        with VerticalScroll() as scroll:
            self.scroll_container = scroll

            # Entry metadata
            star_icon = "★" if self.entry.starred else "☆"
            status_icon = "●" if self.entry.is_unread else "○"

            # Title and metadata
            yield Static(
                f"[bold cyan]{star_icon} {self.entry.title}[/bold cyan]",
                classes="entry-title",
            )
            yield Static(
                f"[dim]{self.entry.feed.title} | {self.entry.published_at.strftime('%Y-%m-%d %H:%M')}[/dim]",
                classes="entry-meta",
            )
            yield Static(f"[dim]{self.entry.url}[/dim]", classes="entry-url")
            yield Static("─" * 80, classes="separator")

            # Convert HTML content to markdown for better display
            content = self._html_to_markdown(self.entry.content)
            yield Markdown(content, classes="entry-content")

        yield Footer()

    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to markdown."""
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0  # No wrapping
        return h.handle(html_content)

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Mark entry as read when opened
        if self.entry.is_unread:
            self.entry.status = "read"
            # TODO: Call API to mark as read

    def action_scroll_down(self):
        """Scroll down one line."""
        if self.scroll_container:
            self.scroll_container.scroll_down()

    def action_scroll_up(self):
        """Scroll up one line."""
        if self.scroll_container:
            self.scroll_container.scroll_up()

    def action_page_down(self):
        """Scroll down one page."""
        if self.scroll_container:
            self.scroll_container.scroll_page_down()

    def action_page_up(self):
        """Scroll up one page."""
        if self.scroll_container:
            self.scroll_container.scroll_page_up()

    def action_back(self):
        """Return to entry list."""
        self.app.pop_screen()

    def action_mark_unread(self):
        """Mark entry as unread."""
        self.entry.status = "unread"
        # TODO: Call API to mark as unread
        self.notify("Marked as unread")

    def action_toggle_star(self):
        """Toggle star status."""
        self.entry.starred = not self.entry.starred
        # TODO: Call API to toggle star
        status = "starred" if self.entry.starred else "unstarred"
        self.notify(f"Entry {status}")

        # Refresh display to update star icon
        self.refresh()

    def action_open_browser(self):
        """Open entry URL in web browser."""
        try:
            webbrowser.open(self.entry.url)
            self.notify(f"Opened in browser: {self.entry.url}")
        except Exception as e:
            self.notify(f"Error opening browser: {e}", severity="error")

    def action_fetch_original(self):
        """Fetch original content from source."""
        # TODO: Call API to fetch original content
        self.notify("Fetching original content...")

    def action_next_entry(self):
        """Navigate to next entry."""
        # TODO: Implement navigation to next entry
        self.notify("Next entry (not yet implemented)")

    def action_previous_entry(self):
        """Navigate to previous entry."""
        # TODO: Implement navigation to previous entry
        self.notify("Previous entry (not yet implemented)")

    def action_show_help(self):
        """Show keyboard help."""
        self.app.push_screen("help")
