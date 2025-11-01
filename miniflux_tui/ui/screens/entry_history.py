"""Entry history screen showing previously read entries."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, ListItem, ListView, Static

from miniflux_tui.api.models import Entry


class EntryHistoryItem(ListItem):
    """List item for a history entry."""

    def __init__(self, entry: Entry, **kwargs):
        """Initialize history item."""
        super().__init__(**kwargs)
        self.entry = entry

    def render(self) -> str:
        """Render the history item."""
        # Format the published date
        try:
            # published_at is already a datetime object from the miniflux library
            pub_date = self.entry.published_at
            date_str = pub_date.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError, TypeError):
            date_str = "Unknown date"

        # Truncate title if too long
        max_width = 100
        title = self.entry.title[:max_width] if len(self.entry.title) > max_width else self.entry.title

        # Build display with feed info if available
        feed_info = f" [{self.entry.feed.title}]" if self.entry.feed and self.entry.feed.title else ""
        status_indicator = "[green]✓[/green]" if self.entry.is_read else "[yellow]○[/yellow]"

        return f"{status_indicator} {date_str} {title}{feed_info}"


class EntryHistoryScreen(Screen):
    """Screen displaying previously read entries."""

    BINDINGS: list[Binding] = [  # noqa: RUF012
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
        Binding("r", "refresh", "Refresh"),
        Binding("u", "restore_entry", "Restore Entry"),
        Binding("enter", "open_entry", "Open Entry"),
    ]

    def __init__(self, **kwargs):
        """Initialize history screen."""
        super().__init__(**kwargs)
        self.history_entries: list[Entry] = []
        self.current_feed_filter: str | None = None
        self.search_query: str = ""
        self._header_widget: Header | None = None
        self._scroll_container: VerticalScroll | None = None
        self._list_view: ListView | None = None
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
            yield Static("[bold cyan]Reading History[/bold cyan]\n", id="title")

            yield Static("[bold yellow]Your Previously Read Entries[/bold yellow]")
            yield Static(id="filter-info")
            yield Static()

            # History entries list
            list_view = ListView(id="history-list")
            self._list_view = list_view
            yield list_view

            yield Static()
            yield Static("[dim]Press u to restore entry, Enter to open, r to refresh, Esc or q to close[/dim]")

        yield footer

    async def on_mount(self) -> None:
        """Called when screen is mounted - load history."""
        await self._load_history()

    async def _load_history(self) -> None:
        """Load reading history from API."""
        if not hasattr(self.app, "client") or not getattr(self.app, "client", None):
            self._update_error_state("API client not available")
            return

        try:
            client = getattr(self.app, "client", None)

            # Get read entries (limit to 200 for performance)
            self.history_entries = await client.get_read_entries(limit=200, offset=0)

            # Update the display
            self._update_display()

        except Exception as e:
            self.app.log(f"Error loading history: {e}")
            self._update_error_state(f"Error: {type(e).__name__}: {e}")

    def _update_error_state(self, error_message: str) -> None:
        """Update display when an error occurs."""
        try:
            filter_info = self.query_one("#filter-info", Static)
            filter_info.update(f"[red]{error_message}[/red]")

            if self._list_view:
                self._list_view.children.clear()
        except Exception as e:
            self.app.log(f"Could not update error state: {e}")

    def _update_display(self) -> None:
        """Update history display."""
        self._update_filter_info()
        self._populate_history_list()

    def _update_filter_info(self) -> None:
        """Update filter information display."""
        try:
            widget = self.query_one("#filter-info", Static)

            # Show total entries and filter status
            total = len(self.history_entries)
            if self.current_feed_filter:
                text = f"  Total read entries: {total}\n  [dim]Filtered by feed: {self.current_feed_filter}[/dim]"
            else:
                text = f"  Total read entries: {total}\n  [dim]Showing all feeds[/dim]"

            widget.update(text)
        except Exception as e:
            self.app.log(f"Could not update filter info: {e}")

    def _populate_history_list(self) -> None:
        """Populate the history list with entries."""
        try:
            if not self._list_view:
                return

            # Clear existing items
            self._list_view.children.clear()

            # Filter entries if needed
            display_entries = self.history_entries
            if self.current_feed_filter:
                display_entries = [e for e in self.history_entries if e.feed and e.feed.title == self.current_feed_filter]

            # Add entries to list
            if not display_entries:
                self._list_view.children.append(ListItem(Static("[dim]No entries found[/dim]")))
            else:
                for entry in display_entries:
                    item = EntryHistoryItem(entry)
                    self._list_view.children.append(item)

        except Exception as e:
            self.app.log(f"Could not populate history list: {e}")

    def action_close(self):
        """Close the history screen."""
        self.app.pop_screen()

    async def action_refresh(self):
        """Refresh the history."""
        try:
            filter_info = self.query_one("#filter-info", Static)
            filter_info.update("[dim]Refreshing...[/dim]")
        except Exception as e:
            self.app.log(f"Could not update refresh message: {e}")

        # Reload history
        await self._load_history()

        # Notify user
        self.app.notify("History refreshed")

    def action_open_entry(self):
        """Open the selected history entry in the entry reader."""
        if not self._list_view or self._list_view.index is None:
            return

        try:
            selected_item = self._list_view.children[self._list_view.index]
            if isinstance(selected_item, EntryHistoryItem):
                entry = selected_item.entry
                # Push to entry reader screen
                if hasattr(self.app, "push_entry_reader"):
                    # For history, we use the filtered/display entries
                    entry_list = self._get_display_entries()
                    try:
                        entry_index = entry_list.index(entry)
                    except ValueError:
                        entry_index = 0
                    self.app.push_entry_reader(entry=entry, entry_list=entry_list, current_index=entry_index)
        except (IndexError, AttributeError) as e:
            self.app.log(f"Could not open entry: {e}")

    async def action_restore_entry(self):
        """Restore a read entry (mark as unread)."""
        if not self._list_view or self._list_view.index is None:
            return

        if not hasattr(self.app, "client") or not getattr(self.app, "client", None):
            self.app.notify("API client not available")
            return

        try:
            selected_item = self._list_view.children[self._list_view.index]
            if isinstance(selected_item, EntryHistoryItem):
                entry = selected_item.entry
                client = getattr(self.app, "client", None)

                # Mark as unread to restore
                await client.mark_as_unread(entry.id)
                self.app.notify(f"Restored: {entry.title[:50]}")

                # Remove from history display
                if entry in self.history_entries:
                    self.history_entries.remove(entry)
                    self._update_display()
        except Exception as e:
            self.app.log(f"Could not restore entry: {e}")
            self.app.notify(f"Error restoring entry: {e}")

    def _get_display_entries(self) -> list[Entry]:
        """Get the currently displayed entries (filtered if needed)."""
        if self.current_feed_filter:
            return [e for e in self.history_entries if e.feed and e.feed.title == self.current_feed_filter]
        return self.history_entries
