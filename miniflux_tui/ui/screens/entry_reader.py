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

    async def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Get reference to the scroll container after mount
        self.scroll_container = self.query_one(VerticalScroll)

        # Mark entry as read when opened
        if self.entry.is_unread:
            await self._mark_entry_as_read()

    async def _mark_entry_as_read(self):
        """Mark the current entry as read via API."""
        from ..app import MinifluxTUI
        if isinstance(self.app, MinifluxTUI) and self.app.client:
            try:
                await self.app.client.mark_as_read(self.entry.id)
                self.entry.status = "read"
            except Exception as e:
                self.notify(f"Error marking as read: {e}", severity="error")

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

    async def action_mark_unread(self):
        """Mark entry as unread."""
        from ..app import MinifluxTUI
        if isinstance(self.app, MinifluxTUI) and self.app.client:
            try:
                await self.app.client.mark_as_unread(self.entry.id)
                self.entry.status = "unread"
                self.notify("Marked as unread")
            except Exception as e:
                self.notify(f"Error marking as unread: {e}", severity="error")

    async def action_toggle_star(self):
        """Toggle star status."""
        from ..app import MinifluxTUI
        if isinstance(self.app, MinifluxTUI) and self.app.client:
            try:
                await self.app.client.toggle_starred(self.entry.id)
                self.entry.starred = not self.entry.starred
                status = "starred" if self.entry.starred else "unstarred"
                self.notify(f"Entry {status}")

                # Refresh display to update star icon
                await self.refresh_screen()
            except Exception as e:
                self.notify(f"Error toggling star: {e}", severity="error")

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

    async def action_next_entry(self):
        """Navigate to next entry."""
        if not self.entry_list or self.current_index >= len(self.entry_list) - 1:
            self.notify("No next entry", severity="warning")
            return

        # Move to next entry
        self.current_index += 1
        self.entry = self.entry_list[self.current_index]

        # Refresh the screen with new entry
        await self.refresh_screen()

    async def action_previous_entry(self):
        """Navigate to previous entry."""
        if not self.entry_list or self.current_index <= 0:
            self.notify("No previous entry", severity="warning")
            return

        # Move to previous entry
        self.current_index -= 1
        self.entry = self.entry_list[self.current_index]

        # Refresh the screen with new entry
        await self.refresh_screen()

    async def refresh_screen(self):
        """Refresh the screen with current entry."""
        # Instead of removing and re-mounting, just update the content widgets
        scroll = self.query_one(VerticalScroll)

        # Remove only the content inside the scroll container
        for child in scroll.children:
            child.remove()

        # Entry metadata
        star_icon = "★" if self.entry.starred else "☆"

        # Re-mount the content
        scroll.mount(
            Static(
                f"[bold cyan]{star_icon} {self.entry.title}[/bold cyan]",
                classes="entry-title",
            )
        )
        scroll.mount(
            Static(
                f"[dim]{self.entry.feed.title} | {self.entry.published_at.strftime('%Y-%m-%d %H:%M')}[/dim]",
                classes="entry-meta",
            )
        )
        scroll.mount(Static(f"[dim]{self.entry.url}[/dim]", classes="entry-url"))
        scroll.mount(Static("─" * 80, classes="separator"))

        # Convert HTML content to markdown
        content = self._html_to_markdown(self.entry.content)
        scroll.mount(Markdown(content, classes="entry-content"))

        # Scroll to top
        scroll.scroll_home(animate=False)

        # Mark as read
        if self.entry.is_unread:
            await self._mark_entry_as_read()

    def action_show_help(self):
        """Show keyboard help."""
        self.app.push_screen("help")
