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
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("J", "next_entry", "Next Entry", show=True),
        Binding("K", "previous_entry", "Previous Entry", show=True),
        Binding("pagedown", "page_down", "Page Down"),
        Binding("pageup", "page_up", "Page Up"),
        Binding("b", "back", "Back to List"),
        Binding("u", "mark_unread", "Mark Unread"),
        Binding("asterisk", "toggle_star", "Toggle Star"),
        Binding("o", "open_browser", "Open in Browser"),
        Binding("f", "fetch_original", "Fetch Original"),
        Binding("question_mark", "show_help", "Help"),
        Binding("escape", "back", "Back", show=False),
    ]

    def __init__(
        self,
        entry: Entry,
        entry_list: list = None,
        current_index: int = 0,
        unread_color: str = "cyan",
        read_color: str = "gray",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entry = entry
        self.entry_list = entry_list or []
        self.current_index = current_index
        self.unread_color = unread_color
        self.read_color = read_color
        self.scroll_container = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        # Entry metadata
        star_icon = "★" if self.entry.starred else "☆"
        status_icon = "●" if self.entry.is_unread else "○"

        # Create scrollable container with entry content
        with VerticalScroll():
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

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Get reference to the scroll container after mount
        self.scroll_container = self.query_one(VerticalScroll)

        # Mark entry as read when opened
        if self.entry.is_unread:
            self.entry.status = "read"
            # TODO: Call API to mark as read

    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to markdown."""
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0  # No wrapping
        return h.handle(html_content)

    def action_scroll_down(self):
        """Scroll down one line."""
        if not self.scroll_container:
            self.scroll_container = self.query_one(VerticalScroll)
        self.scroll_container.scroll_down()

    def action_scroll_up(self):
        """Scroll up one line."""
        if not self.scroll_container:
            self.scroll_container = self.query_one(VerticalScroll)
        self.scroll_container.scroll_up()

    def action_page_down(self):
        """Scroll down one page."""
        if not self.scroll_container:
            self.scroll_container = self.query_one(VerticalScroll)
        self.scroll_container.scroll_page_down()

    def action_page_up(self):
        """Scroll up one page."""
        if not self.scroll_container:
            self.scroll_container = self.query_one(VerticalScroll)
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
        if not self.entry_list or self.current_index >= len(self.entry_list) - 1:
            self.notify("No next entry", severity="warning")
            return

        # Move to next entry
        self.current_index += 1
        self.entry = self.entry_list[self.current_index]

        # Refresh the screen with new entry
        self.refresh_screen()

    def action_previous_entry(self):
        """Navigate to previous entry."""
        if not self.entry_list or self.current_index <= 0:
            self.notify("No previous entry", severity="warning")
            return

        # Move to previous entry
        self.current_index -= 1
        self.entry = self.entry_list[self.current_index]

        # Refresh the screen with new entry
        self.refresh_screen()

    def refresh_screen(self):
        """Refresh the screen with current entry."""
        # Remove all children and re-compose
        self.query("*").remove()

        # Re-compose with new entry
        for widget in self.compose():
            self.mount(widget)

        # Reset scroll position
        self.scroll_container = self.query_one(VerticalScroll)

        # Mark as read
        if self.entry.is_unread:
            self.entry.status = "read"

    def action_show_help(self):
        """Show keyboard help."""
        self.app.push_screen("help")
