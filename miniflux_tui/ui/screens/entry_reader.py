# SPDX-License-Identifier: MIT
"""Entry reader screen for viewing feed entry content."""

import re
import traceback
import webbrowser
from contextlib import suppress
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import html2text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Markdown, Static

from miniflux_tui.api.models import Entry
from miniflux_tui.constants import CONTENT_SEPARATOR
from miniflux_tui.ui.protocols import EntryReaderAppProtocol
from miniflux_tui.utils import (
    extract_images_from_html,
    get_star_icon,
    is_valid_image_url,
)

# Optional image support - gracefully handle when textual-image is not available
# Use TYPE_CHECKING to avoid import errors during static analysis when library is not installed
if TYPE_CHECKING:
    from textual_image.widget import Image

    IMAGE_SUPPORT: bool
else:
    try:
        from textual_image.widget import Image

        IMAGE_SUPPORT = True
    except ImportError:
        IMAGE_SUPPORT = False
        Image = None  # type: ignore[assignment]


class EntryReaderScreen(Screen):
    """Screen for reading a single feed entry."""

    BINDINGS: list[Binding] = [  # noqa: RUF012
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("J", "next_entry", "Next Entry", show=True),
        Binding("K", "previous_entry", "Previous Entry", show=True),
        Binding("pagedown", "page_down", "Page Down"),
        Binding("pageup", "page_up", "Page Up"),
        Binding("b", "back", "Back to List"),
        Binding("u", "mark_unread", "Mark Unread"),
        Binding("asterisk", "toggle_star", "Toggle Star"),
        Binding("e", "save_entry", "Save Entry"),
        Binding("o", "open_browser", "Open in Browser"),
        Binding("f", "fetch_original", "Fetch Original"),
        Binding("I", "toggle_images", "Toggle Images"),
        Binding("X", "scraping_helper", "Scraping Helper"),
        Binding("tab", "next_link", "Next Link", show=True),
        Binding("shift+tab", "previous_link", "Previous Link", show=True),
        Binding("n", "next_link", "Next Link", show=False),
        Binding("p", "previous_link", "Previous Link", show=False),
        Binding("enter", "open_focused_link", "Open Link", show=True),
        Binding("c", "clear_link_focus", "Clear Link", show=True),
        Binding("question_mark", "show_help", "Help"),
        Binding("i", "show_status", "Status"),
        Binding("S", "show_settings", "Settings"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "back", "Back", show=False),
    ]

    app: EntryReaderAppProtocol

    def __init__(
        self,
        entry: Entry,
        entry_list: list | None = None,
        current_index: int = 0,
        unread_color: str = "cyan",
        read_color: str = "gray",
        show_images: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entry = entry
        self.entry_list = entry_list or []
        self.current_index = current_index
        self.unread_color = unread_color
        self.read_color = read_color
        self.scroll_container = None
        self.links: list[dict[str, str]] = []  # List of {text: str, url: str}
        self.focused_link_index: int | None = None  # Currently focused link index
        self.link_indicator: Static | None = None  # Widget to show focused link
        self.show_images = show_images

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        # Entry metadata
        star_icon = get_star_icon(self.entry.starred)

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
            yield Static(CONTENT_SEPARATOR, classes="separator")

            # Convert HTML content to markdown for better display
            content = self._html_to_markdown(self.entry.content)

            # Extract links from content
            self.links = self._extract_links(content)

            yield Markdown(content, classes="entry-content")

            # Link navigation indicator
            link_indicator = Static("", id="link-indicator", classes="link-indicator")
            self.link_indicator = link_indicator
            yield link_indicator

        yield Footer()

    async def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Get reference to the scroll container after mount
        self.scroll_container = self.query_one(VerticalScroll)

        # Mark entry as read when opened
        if self.entry.is_unread:
            await self._mark_entry_as_read()

    def _get_image_urls(self) -> list[str]:
        """Get all image URLs from entry (enclosures and content).

        Returns:
            List of valid image URLs
        """
        image_urls = []

        # Get images from enclosures
        if self.entry.image_enclosures:
            image_urls.extend([enc.url for enc in self.entry.image_enclosures])

        # Get images from HTML content
        content_images = extract_images_from_html(self.entry.content, self.entry.url)
        image_urls.extend(content_images)

        # Filter and deduplicate
        seen = set()
        unique_images = []
        for url in image_urls:
            if url not in seen and is_valid_image_url(url):
                seen.add(url)
                unique_images.append(url)

        return unique_images

    def _resolve_app(self) -> EntryReaderAppProtocol | None:
        """Return the parent TUI app if it satisfies the expected protocol."""

        app = self.app
        if isinstance(app, EntryReaderAppProtocol):
            return app
        return None

    async def _mark_entry_as_read(self):
        """Mark the current entry as read via API."""
        app = self._resolve_app()
        if app and app.client:
            try:
                await app.client.mark_as_read(self.entry.id)
                self.entry.status = "read"
            except Exception as e:
                self.log(f"Error marking as read: {e}")
                self.log(traceback.format_exc())
                self.notify(f"Error marking as read: {e}", severity="error")

    @staticmethod
    def _html_to_markdown(html_content: str) -> str:
        """Convert HTML content to markdown for display.

        Converts HTML from RSS feed entries to markdown format for better
        terminal display. Preserves links, images, and formatting information.

        Args:
            html_content: Raw HTML content from the entry

        Returns:
            Markdown-formatted string suitable for terminal display
        """
        h = html2text.HTML2Text()
        # Preserve links, images, and emphasis in the output
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        # Disable body width wrapping - let Textual handle terminal wrapping
        h.body_width = 0
        return h.handle(html_content)

    @staticmethod
    def _extract_links(markdown_content: str) -> list[dict[str, str]]:
        """Extract all links from markdown content.

        Finds both markdown-style links [text](url) and plain URLs in the content.

        Args:
            markdown_content: Markdown-formatted content

        Returns:
            List of dictionaries with 'text' and 'url' keys for each link found
        """
        links = []

        # Extract markdown links: [text](url)
        markdown_link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for match in re.finditer(markdown_link_pattern, markdown_content):
            text, url = match.groups()
            links.append({"text": text.strip(), "url": url.strip()})

        # Extract plain URLs (http/https) that aren't already in markdown links
        # This is a simple pattern - doesn't catch all edge cases
        plain_url_pattern = r"(?<!\()(https?://[^\s)\]]+)"
        for match in re.finditer(plain_url_pattern, markdown_content):
            url = match.group(1).strip()
            # Only add if not already in our links list
            if not any(link["url"] == url for link in links):
                links.append({"text": url, "url": url})

        return links

    def _ensure_scroll_container(self) -> VerticalScroll:
        """Ensure scroll container is initialized and return it.

        Lazily initializes the scroll container reference if not already set.
        This eliminates the repeated pattern of checking and initializing
        the scroll container across multiple scroll action methods.

        Returns:
            The VerticalScroll container widget
        """
        if not self.scroll_container:
            self.scroll_container = self.query_one(VerticalScroll)
        return self.scroll_container

    def action_scroll_down(self):
        """Scroll down one line."""
        self._ensure_scroll_container().scroll_down()

    def action_scroll_up(self):
        """Scroll up one line."""
        self._ensure_scroll_container().scroll_up()

    def action_page_down(self):
        """Scroll down one page."""
        self._ensure_scroll_container().scroll_page_down()

    def action_page_up(self):
        """Scroll up one page."""
        self._ensure_scroll_container().scroll_page_up()

    def action_back(self):
        """Return to entry list."""
        app = self._resolve_app()
        if app:
            app.pop_screen()

    async def action_mark_unread(self):
        """Mark entry as unread."""
        app = self._resolve_app()
        if app and app.client:
            try:
                await app.client.mark_as_unread(self.entry.id)
                self.entry.status = "unread"
                self.notify("Marked as unread")
            except Exception as e:
                self.notify(f"Error marking as unread: {e}", severity="error")

    async def action_toggle_star(self):
        """Toggle star status."""
        app = self._resolve_app()
        if app and app.client:
            try:
                await app.client.toggle_starred(self.entry.id)
                self.entry.starred = not self.entry.starred
                status = "starred" if self.entry.starred else "unstarred"
                self.notify(f"Entry {status}")

                # Refresh display to update star icon
                await self.refresh_screen()
            except Exception as e:
                self.notify(f"Error toggling star: {e}", severity="error")

    async def action_save_entry(self):
        """Save entry to third-party service."""
        app = self._resolve_app()
        if app and app.client:
            try:
                await app.client.save_entry(self.entry.id)
                self.notify(f"Entry saved: {self.entry.title}")
            except Exception as e:
                self.notify(f"Failed to save entry: {e}", severity="error")

    @staticmethod
    def _is_safe_external_url(url: str) -> bool:
        """Return True if the URL uses an allowed scheme and has a hostname."""
        if not url:
            return False

        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"}:
            return False
        if not parsed.netloc:
            return False

        return not any(ord(char) < 32 for char in url)

    def action_open_browser(self):
        """Open entry URL in web browser."""
        url = (self.entry.url or "").strip()
        if not url:
            self.notify("Entry does not contain a URL to open", severity="warning")
            return
        if not self._is_safe_external_url(url):
            self.notify("Refused to open unsafe entry URL", severity="error")
            if url:
                with suppress(Exception):
                    self.log(f"Blocked attempt to open unsafe URL: {url!r}")
            return

        try:
            webbrowser.open(url)
            self.notify(f"Opened in browser: {url}")
        except Exception as e:
            self.notify(f"Error opening browser: {e}", severity="error")

    async def action_fetch_original(self):
        """Fetch original content from source."""
        app = self._resolve_app()
        if app and app.client:
            try:
                self.notify("Fetching original content...")

                # Fetch original content from API
                original_content = await app.client.fetch_original_content(self.entry.id)

                if original_content:
                    # Update the entry's content
                    self.entry.content = original_content

                    # Refresh the screen to show new content
                    await self.refresh_screen()

                    self.notify("Original content loaded")
                else:
                    self.notify("No original content available", severity="warning")
            except Exception as e:
                self.log(f"Error fetching original content: {e}")
                self.log(traceback.format_exc())
                self.notify(f"Error fetching content: {e}", severity="error")

    async def action_toggle_images(self):
        """Toggle image display on/off."""
        self.show_images = not self.show_images
        status = "enabled" if self.show_images else "disabled"
        self.notify(f"Image display {status}")

        # Refresh the screen to apply changes
        await self.refresh_screen()

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
        scroll = self._get_scroll_container()
        self._clear_scroll_content(scroll)
        self._mount_entry_content(scroll)
        scroll.scroll_home(animate=False)

        # Mark as read after displaying
        if self.entry.is_unread:
            await self._mark_entry_as_read()

    def _get_scroll_container(self) -> VerticalScroll:
        """Get scroll container widget.

        Deprecated: Use _ensure_scroll_container() instead. This method
        is kept for backward compatibility and delegates to the new helper.
        """
        return self._ensure_scroll_container()

    @staticmethod
    def _clear_scroll_content(scroll: VerticalScroll):
        """Remove all children from scroll container."""
        for child in scroll.children:
            child.remove()

    def _mount_entry_content(self, scroll: VerticalScroll):
        """Mount entry content widgets (title, metadata, URL, content)."""
        self._mount_title(scroll)
        self._mount_metadata(scroll)
        self._mount_url(scroll)
        self._mount_separator(scroll)
        self._mount_content(scroll)

    def _mount_title(self, scroll: VerticalScroll):
        """Mount entry title widget with star icon."""
        star_icon = get_star_icon(self.entry.starred)
        scroll.mount(
            Static(
                f"[bold cyan]{star_icon} {self.entry.title}[/bold cyan]",
                classes="entry-title",
            )
        )

    def _mount_metadata(self, scroll: VerticalScroll):
        """Mount entry metadata widget (feed name and published date)."""
        scroll.mount(
            Static(
                f"[dim]{self.entry.feed.title} | {self.entry.published_at.strftime('%Y-%m-%d %H:%M')}[/dim]",
                classes="entry-meta",
            )
        )

    def _mount_url(self, scroll: VerticalScroll):
        """Mount entry URL widget."""
        scroll.mount(Static(f"[dim]{self.entry.url}[/dim]", classes="entry-url"))

    @staticmethod
    def _mount_separator(scroll: VerticalScroll):
        """Mount visual separator widget."""
        scroll.mount(Static(CONTENT_SEPARATOR, classes="separator"))

    def _mount_content(self, scroll: VerticalScroll):
        """Mount entry content widget (converted HTML to Markdown) and images."""
        # Display images if enabled and image support is available
        if self.show_images and IMAGE_SUPPORT:
            image_urls = self._get_image_urls()
            if image_urls:
                scroll.mount(Static("[bold]Images:[/bold]", classes="images-header"))
                for url in image_urls:
                    try:
                        # Mount image widget with error handling
                        if Image is not None:
                            scroll.mount(Image(url, classes="entry-image"))
                    except Exception as e:
                        self.log(f"Error loading image {url}: {e}")
                        # Show a text placeholder if image fails to load
                        scroll.mount(Static(f"[dim]Image: {url}[/dim]", classes="image-placeholder"))

                scroll.mount(Static(CONTENT_SEPARATOR, classes="separator"))
        elif self.show_images and not IMAGE_SUPPORT:
            # Show helpful message if user tries to enable images but support isn't available
            image_urls = self._get_image_urls()
            if image_urls:
                scroll.mount(
                    Static(
                        "[yellow]Image support not available. Install with: pip install miniflux-tui-py[images][/yellow]",
                        classes="image-warning",
                    )
                )
                scroll.mount(Static("[bold]Image URLs:[/bold]", classes="images-header"))
                for url in image_urls[:5]:  # Limit to first 5 to avoid clutter
                    scroll.mount(Static(f"[dim]• {url}[/dim]", classes="image-url"))
                if len(image_urls) > 5:
                    scroll.mount(Static(f"[dim]... and {len(image_urls) - 5} more[/dim]", classes="image-url"))
                scroll.mount(Static(CONTENT_SEPARATOR, classes="separator"))

        # Mount text content
        content = self._html_to_markdown(self.entry.content)

        # Extract links from content
        self.links = self._extract_links(content)
        self.focused_link_index = None  # Reset link focus on new content

        scroll.mount(Markdown(content, classes="entry-content"))

        # Mount or update link indicator
        if not self.link_indicator:
            self.link_indicator = Static("", id="link-indicator", classes="link-indicator")
            scroll.mount(self.link_indicator)
        else:
            self._update_link_indicator()

    async def action_scraping_helper(self) -> None:
        """Open scraping helper for current entry."""
        # Import here to avoid circular dependency

        from miniflux_tui.ui.screens.scraping_helper import (  # noqa: PLC0415
            ScrapingHelperScreen,
        )

        # Create callback for saving scraper rules
        async def save_scraper_rule(feed_id: int, selector: str) -> None:
            """Save scraper rule to feed settings."""
            if not self.app.client:
                msg = "API client not available"
                raise RuntimeError(msg)

            # Update feed with scraper rules
            # Type ignore because protocol doesn't include all methods
            await self.app.client.update_feed(  # type: ignore[attr-defined]
                feed_id,
                scraper_rules=selector,
            )

            self.notify(
                f"Scraper rule saved for feed: {self.entry.feed.title}",
                severity="information",
            )

        # Push scraping helper screen
        screen = ScrapingHelperScreen(
            entry_url=self.entry.url,
            feed_id=self.entry.feed.id,
            feed_title=self.entry.feed.title,
            on_save_callback=save_scraper_rule,
        )
        # Type ignore because protocol only expects string, but actual app accepts Screen
        self.app.push_screen(screen)  # type: ignore[arg-type]

    def action_show_help(self):
        """Show keyboard help."""
        app = self._resolve_app()
        if app:
            app.push_screen("help")

    def action_show_status(self):
        """Show system status and feed health."""
        app = self._resolve_app()
        if app:
            app.push_screen("status")

    def action_show_settings(self):
        """Show user settings and integrations."""
        app = self._resolve_app()
        if app:
            app.push_screen("settings")

    def _update_link_indicator(self):
        """Update the link indicator widget with current focused link info."""
        if not self.link_indicator:
            return

        if self.focused_link_index is None or not self.links:
            self.link_indicator.update("")
            return

        # Show focused link info
        link = self.links[self.focused_link_index]
        link_num = self.focused_link_index + 1
        total_links = len(self.links)

        # Truncate long URLs/text for display
        display_text = link["text"]
        if len(display_text) > 60:
            display_text = display_text[:57] + "..."

        display_url = link["url"]
        if len(display_url) > 80:
            display_url = display_url[:77] + "..."

        indicator_text = f"[bold yellow]Link {link_num}/{total_links}:[/bold yellow] [cyan]{display_text}[/cyan]\n[dim]{display_url}[/dim]"

        self.link_indicator.update(indicator_text)

    def action_next_link(self):
        """Navigate to the next link in the content."""
        if not self.links:
            self.notify("No links found in this entry", severity="warning")
            return

        if self.focused_link_index is None:
            # Start at first link
            self.focused_link_index = 0
        else:
            # Move to next link (wrap around)
            self.focused_link_index = (self.focused_link_index + 1) % len(self.links)

        self._update_link_indicator()

    def action_previous_link(self):
        """Navigate to the previous link in the content."""
        if not self.links:
            self.notify("No links found in this entry", severity="warning")
            return

        if self.focused_link_index is None:
            # Start at last link
            self.focused_link_index = len(self.links) - 1
        else:
            # Move to previous link (wrap around)
            self.focused_link_index = (self.focused_link_index - 1) % len(self.links)

        self._update_link_indicator()

    def action_open_focused_link(self):
        """Open the currently focused link in the browser."""
        if self.focused_link_index is None or not self.links:
            self.notify("No link focused. Use Tab to focus a link first.", severity="warning")
            return

        link = self.links[self.focused_link_index]
        url = link["url"].strip()

        if not self._is_safe_external_url(url):
            self.notify("Refused to open unsafe URL", severity="error")
            if url:
                with suppress(Exception):
                    self.log(f"Blocked attempt to open unsafe URL: {url!r}")
            return

        try:
            webbrowser.open(url)
            self.notify(f"Opened link: {link['text']}")
        except Exception as e:
            self.notify(f"Error opening link: {e}", severity="error")

    def action_clear_link_focus(self):
        """Clear the current link focus."""
        self.focused_link_index = None
        self._update_link_indicator()
        self.notify("Link focus cleared")

    def action_quit(self):
        """Quit the application."""
        app = self._resolve_app()
        if app:
            app.exit()
