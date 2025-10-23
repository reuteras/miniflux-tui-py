"""Main TUI application."""

from textual.app import App
from textual.driver import Driver

from ..api.client import MinifluxClient
from ..api.models import Entry
from ..config import Config
from .screens.entry_list import EntryListScreen
from .screens.entry_reader import EntryReaderScreen
from .screens.help import HelpScreen


class MinifluxTUI(App):
    """A Textual TUI application for Miniflux."""

    CSS = """
    Screen {
        background: $surface;
    }

    .entry-title {
        padding: 1 2;
        background: $boost;
    }

    .entry-meta {
        padding: 0 2;
    }

    .entry-url {
        padding: 0 2 1 2;
    }

    .separator {
        padding: 0 2;
        color: $border;
    }

    .entry-content {
        padding: 1 2;
    }

    ListView {
        background: $surface;
        color: $text;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: $boost;
    }

    ListItem.-active {
        background: $accent;
    }
    """

    def __init__(
        self,
        config: Config,
        driver_class: Driver | None = None,
        css_path: str | None = None,
        watch_css: bool = False,
    ):
        """
        Initialize the Miniflux TUI application.

        Args:
            config: Application configuration
            driver_class: Textual driver class
            css_path: Path to custom CSS file
            watch_css: Whether to watch CSS file for changes
        """
        super().__init__(
            driver_class=driver_class,
            css_path=css_path,
            watch_css=watch_css,
        )
        self.config = config
        self.client: MinifluxClient | None = None
        self.entries: list[Entry] = []
        self.current_view = "unread"  # or "starred"

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        # Initialize API client
        self.client = MinifluxClient(
            base_url=self.config.server_url,
            api_key=self.config.api_key,
            allow_invalid_certs=self.config.allow_invalid_certs,
        )

        # Load initial entries
        await self.load_entries()

        # Install screens
        self.install_screen(
            EntryListScreen(
                entries=self.entries,
                unread_color=self.config.unread_color,
                read_color=self.config.read_color,
                default_sort=self.config.default_sort,
                group_by_feed=self.config.default_group_by_feed,
            ),
            name="entry_list",
        )

        self.install_screen(HelpScreen(), name="help")

        # Push initial screen
        self.push_screen("entry_list")

    async def load_entries(self, view: str = "unread") -> None:
        """
        Load entries from Miniflux API.

        Args:
            view: View type - "unread" or "starred"
        """
        if not self.client:
            return

        try:
            if view == "starred":
                self.entries = await self.client.get_starred_entries(limit=100)
                self.current_view = "starred"
            else:
                self.entries = await self.client.get_unread_entries(limit=100)
                self.current_view = "unread"

            # Update the entry list screen if it exists
            if self.is_screen_installed("entry_list"):
                screen = self.get_screen("entry_list")
                if isinstance(screen, EntryListScreen):
                    screen.entries = self.entries
                    screen._populate_list()

        except Exception as e:
            self.notify(f"Error loading entries: {e}", severity="error")

    def push_entry_reader(self, entry: Entry) -> None:
        """
        Push entry reader screen for a specific entry.

        Args:
            entry: Entry to display
        """
        reader_screen = EntryReaderScreen(
            entry=entry,
            unread_color=self.config.unread_color,
            read_color=self.config.read_color,
        )
        self.push_screen(reader_screen)

    async def action_refresh_entries(self) -> None:
        """Refresh entries from API."""
        await self.load_entries(self.current_view)
        self.notify("Entries refreshed")

    async def action_show_unread(self) -> None:
        """Show unread entries."""
        await self.load_entries("unread")
        self.notify("Showing unread entries")

    async def action_show_starred(self) -> None:
        """Show starred entries."""
        await self.load_entries("starred")
        self.notify("Showing starred entries")

    async def on_unmount(self) -> None:
        """Called when app is unmounted."""
        # Close API client
        if self.client:
            await self.client.close()


async def run_tui(config: Config) -> None:
    """
    Run the Miniflux TUI application.

    Args:
        config: Application configuration
    """
    app = MinifluxTUI(config)
    await app.run_async()
