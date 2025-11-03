"""Entry history screen showing previously read entries."""

# pylint: disable=no-member

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from miniflux_tui.api.models import Entry
from miniflux_tui.ui.base_screen import BaseScreen


class EntryHistoryItem(ListItem):
    """List item for a history entry."""

    def __init__(self, entry: Entry, **kwargs):
        """Initialize history item."""
        self.entry = entry
        
        # Format the display text
        try:
            # Format the published date
            try:
                pub_date = entry.published_at
                date_str = pub_date.strftime("%Y-%m-%d %H:%M")
            except (ValueError, AttributeError, TypeError):
                date_str = "Unknown date"

            # Truncate title if too long
            max_width = 80
            title = entry.title[:max_width] if len(entry.title) > max_width else entry.title

            # Build display with feed info if available
            feed_info = f" [{entry.feed.title[:30]}]" if entry.feed and entry.feed.title else ""
            status_indicator = "✓" if entry.is_read else "○"

            label_text = f"{status_indicator} {date_str} {title}{feed_info}"
        except Exception as e:
            # Fallback if formatting fails
            label_text = f"Error: {str(e)[:50]}"
        
        # Initialize with a Static widget (simpler than Label)
        super().__init__(Static(label_text), **kwargs)


class EntryHistoryScreen(BaseScreen):
    """Screen displaying previously read entries."""

    CSS = """
    EntryHistoryScreen {
        background: $surface;
    }
    
    #history-list {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }
    
    #filter-info {
        height: auto;
        margin-bottom: 1;
    }
    
    #title {
        height: auto;
    }
    
    #help-text {
        height: auto;
        margin-top: 1;
    }
    """

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
            yield Static(id="filter-info")

            # History entries list - give it more prominence
            list_view = ListView(id="history-list")
            self._list_view = list_view
            yield list_view

            yield Static()
            yield Static("[dim]Press Enter to open entry, r to refresh, Esc or q to close[/dim]", id="help-text")

        yield footer

    async def on_mount(self) -> None:
        """Called when screen is mounted - load history."""
        self.app.log("EntryHistoryScreen.on_mount called")
        await self._load_history()

    async def _load_history(self) -> None:
        """Load reading history from API."""
        if not hasattr(self.app, "client") or not getattr(self.app, "client", None):
            self._update_error_state("API client not available")
            return

        try:
            # Show loading indicator
            self.app.notify("Loading history...")
            
            client = getattr(self.app, "client", None)

            # Get read entries (limit to 200 for performance)
            self.history_entries = await client.get_read_entries(limit=200, offset=0)

            # Log result for debugging
            self.app.log(f"Loaded {len(self.history_entries)} history entries")
            
            # Update the display
            self._update_display()
            
            # Notify user with result
            if not self.history_entries:
                self.app.notify("No read entries found. Read some articles first!", severity="information")
            else:
                self.app.notify(f"Loaded {len(self.history_entries)} entries - check if they appear in the list below", severity="information")

        except Exception as e:
            error_msg = f"Error loading history: {type(e).__name__}: {e}"
            self.app.log(error_msg)
            self._update_error_state(error_msg)
            self.app.notify("Failed to load history. Check logs for details.", severity="error")

    def _update_error_state(self, error_message: str) -> None:
        """Update display when an error occurs."""
        try:
            filter_info = self.query_one("#filter-info", Static)
            filter_info.update(f"[red]{error_message}[/red]")

            if self._list_view:
                # Clear existing items using ListView's clear method
                self._list_view.clear()
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

            # Show total entries count
            total = len(self.history_entries)
            if self.current_feed_filter:
                text = f"[dim]Showing {total} entries from {self.current_feed_filter}[/dim]\n"
            else:
                text = f"[dim]Last {total} read entries[/dim]\n"

            widget.update(text)
        except Exception as e:
            self.app.log(f"Could not update filter info: {e}")

    def _populate_history_list(self) -> None:
        """Populate the history list with entries."""
        try:
            self.app.log(f"_populate_history_list called with {len(self.history_entries)} entries")
            
            if not self._list_view:
                self.app.log("ERROR: _list_view is None!")
                return

            # Clear existing items using ListView's clear method
            self._list_view.clear()
            self.app.log("Cleared list view")

            # TEST: Add a simple static test item first
            test_item = ListItem(Static("TEST ITEM - If you see this, ListView works!"))
            self._list_view.append(test_item)
            self.app.log("Added test item")

            # Filter entries if needed
            display_entries = self.history_entries
            if self.current_feed_filter:
                display_entries = [e for e in self.history_entries if e.feed and e.feed.title == self.current_feed_filter]

            self.app.log(f"Display entries count: {len(display_entries)}")

            # Add entries to list using ListView's append method
            if not display_entries:
                # Show friendly empty state message
                if self.current_feed_filter:
                    msg = f"[dim]No entries found for feed: {self.current_feed_filter}[/dim]"
                else:
                    msg = "[dim]No read entries found.\nRead some articles first by pressing Enter on entries![/dim]"
                self._list_view.append(ListItem(Static(msg)))
                self.app.log("Added empty state message")
            else:
                self.app.log(f"About to add {len(display_entries)} items to ListView")
                
                # Add a separator
                self._list_view.append(ListItem(Static("--- History Entries Below ---")))
                
                for i, entry in enumerate(display_entries):
                    # Create simple text without any Entry object complexity
                    simple_text = f"{i+1}. {entry.title[:60]}"
                    simple_item = ListItem(Static(simple_text))
                    self._list_view.append(simple_item)
                    
                    if i < 3:  # Log first 3 for debugging
                        self.app.log(f"Added entry {i}: {entry.title[:50]}")
                        
                    # Stop after 10 for testing
                    if i >= 9:
                        break
                        
                self.app.log(f"Successfully added test items to list")
                
                # Force a refresh
                self._list_view.refresh()
                self.app.log("Called refresh on ListView")

        except Exception as e:
            self.app.log(f"ERROR in _populate_history_list: {type(e).__name__}: {e}")
            import traceback
            self.app.log(f"Traceback: {traceback.format_exc()}")
            self.app.notify(f"Error displaying history: {e}", severity="error")

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
