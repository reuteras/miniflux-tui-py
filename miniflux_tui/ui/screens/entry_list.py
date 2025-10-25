"""Entry list screen with feed sorting capabilities."""

from contextlib import suppress
from typing import TYPE_CHECKING, cast

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from miniflux_tui.api.models import Entry
from miniflux_tui.constants import (
    FOLD_COLLAPSED,
    FOLD_EXPANDED,
    SORT_MODES,
)
from miniflux_tui.performance import ScreenRefreshOptimizer
from miniflux_tui.utils import get_star_icon, get_status_icon

if TYPE_CHECKING:
    from miniflux_tui.ui.app import MinifluxTUI


class EntryListItem(ListItem):
    """Custom list item for displaying a feed entry."""

    def __init__(self, entry: Entry, unread_color: str = "cyan", read_color: str = "gray"):
        self.entry = entry
        self.unread_color = unread_color
        self.read_color = read_color

        # Format the entry display
        status_icon = get_status_icon(entry.is_unread)
        star_icon = get_star_icon(entry.starred)

        # Determine color based on read status
        color = unread_color if entry.is_unread else read_color

        # Create the label text with color markup
        label_text = f"[{color}]{status_icon} {star_icon} {entry.feed.title} | {entry.title}[/{color}]"

        # Initialize with the label
        super().__init__(Label(label_text))


class FeedHeaderItem(ListItem):
    """Custom list item for feed header with fold/unfold capability."""

    def __init__(self, feed_title: str, is_expanded: bool = True):
        self.feed_title = feed_title
        self.is_expanded = is_expanded

        # Format header with fold indicator
        fold_icon = FOLD_EXPANDED if is_expanded else FOLD_COLLAPSED
        header_text = f"[bold]{fold_icon} {feed_title}[/bold]"
        label = Label(header_text, classes="feed-header")

        # Initialize with the label
        super().__init__(label)

    def toggle_fold(self) -> None:
        """Toggle the fold state and update display."""
        self.is_expanded = not self.is_expanded
        fold_icon = FOLD_EXPANDED if self.is_expanded else FOLD_COLLAPSED
        header_text = f"[bold]{fold_icon} {self.feed_title}[/bold]"
        # Update the label
        if self.children:
            cast(Label, self.children[0]).update(header_text)


class EntryListScreen(Screen):
    """Screen for displaying a list of feed entries with sorting."""

    BINDINGS = [  # noqa: RUF012
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "select_entry", "Open Entry"),
        Binding("m", "toggle_read", "Mark Read/Unread"),
        Binding("asterisk", "toggle_star", "Toggle Star"),
        Binding("e", "save_entry", "Save Entry"),
        Binding("s", "cycle_sort", "Cycle Sort"),
        Binding("g", "toggle_group", "Group by Feed"),
        Binding("o", "toggle_fold", "Fold/Unfold Feed"),
        Binding("h", "collapse_feed", "Collapse Feed"),
        Binding("l", "expand_feed", "Expand Feed"),
        Binding("left", "collapse_feed", "Collapse Feed", show=False),
        Binding("right", "expand_feed", "Expand Feed", show=False),
        Binding("r", "refresh", "Refresh"),
        Binding("comma", "refresh", "Refresh", show=False),
        Binding("u", "show_unread", "Unread"),
        Binding("t", "show_starred", "Starred"),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        entries: list[Entry],
        unread_color: str = "cyan",
        read_color: str = "gray",
        default_sort: str = "date",
        group_by_feed: bool = False,
        group_collapsed: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entries = entries
        self.sorted_entries = entries.copy()  # Store sorted entries for navigation
        self.unread_color = unread_color
        self.read_color = read_color
        self.current_sort = default_sort
        self.group_by_feed = group_by_feed
        self.group_collapsed = group_collapsed  # Start feeds collapsed in grouped mode
        self.filter_unread_only = False  # Filter to show only unread entries
        self.filter_starred_only = False  # Filter to show only starred entries
        self.list_view: ListView | None = None
        self.displayed_items: list[ListItem] = []  # Track items in display order
        self.refresh_optimizer = ScreenRefreshOptimizer()  # Track refresh performance
        self.entry_item_map: dict[int, EntryListItem] = {}  # Map entry IDs to list items
        self.feed_header_map: dict[str, FeedHeaderItem] = {}  # Map feed names to header items
        self.feed_fold_state: dict[str, bool] = {}  # Track fold state per feed (True = expanded)
        self.last_highlighted_feed: str | None = None  # Track last highlighted feed for position persistence

    @property
    def app(self) -> "MinifluxTUI":
        """Get the app instance with proper type hints."""
        return cast("MinifluxTUI", super().app)

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield ListView()
        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Get reference to the ListView after it's mounted
        self.list_view = self.query_one(ListView)
        self.log(f"on_mount: list_view is now {self.list_view}")

        # Only populate if we have entries
        if self.entries:
            self.log(f"on_mount: Populating with {len(self.entries)} entries")
            self._populate_list()
            # Restore position to last highlighted feed in grouped mode
            if self.group_by_feed:
                self._restore_cursor_position()
        else:
            self.log("on_mount: No entries yet, skipping initial population")

    def on_screen_resume(self) -> None:
        """Called when screen is resumed (e.g., after returning from entry reader)."""
        # Refresh the list to reflect any status changes
        if self.entries and self.list_view:
            self._populate_list()
            # Restore cursor position to last highlighted feed in grouped mode
            if self.group_by_feed:
                self._restore_cursor_position()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle ListView selection (Enter key)."""
        # Get the selected item
        if event.item and isinstance(event.item, EntryListItem):
            # Save the feed of the current entry for position restoration
            self.last_highlighted_feed = event.item.entry.feed.title

            # Find the index of this entry in the sorted entry list
            entry_index = 0
            for i, entry in enumerate(self.sorted_entries):
                if entry.id == event.item.entry.id:
                    entry_index = i
                    break

            # Open entry reader screen with navigation context
            if isinstance(self.app, self.app.__class__) and hasattr(self.app, "push_entry_reader"):
                self.app.push_entry_reader(entry=event.item.entry, entry_list=self.sorted_entries, current_index=entry_index)

    def _populate_list(self):
        """Populate the list with sorted and filtered entries."""
        if not self._ensure_list_view():
            return

        self.list_view.clear()
        sorted_entries = self._get_sorted_entries()
        self.sorted_entries = sorted_entries
        self._display_entries(sorted_entries)
        self.refresh_optimizer.track_full_refresh()

        # Set initial index to 0 to highlight the first item
        if len(self.list_view.children) > 0:
            with suppress(IndexError, ValueError):
                self.list_view.index = 0

    def _restore_cursor_position(self) -> None:
        """Restore cursor position to the last highlighted feed header.

        Used after rebuilding the list to restore user's position.
        """
        if not self.list_view or not self.last_highlighted_feed:
            return

        # Try to find the feed header in the new list
        if self.last_highlighted_feed in self.feed_header_map:
            feed_header = self.feed_header_map[self.last_highlighted_feed]
            # Find its index in the list view
            for i, child in enumerate(self.list_view.children):
                if child is feed_header:
                    with suppress(Exception):
                        self.list_view.index = i
                        return

        # If not found, just go to first item
        with suppress(Exception):
            self.list_view.index = 0


    def _ensure_list_view(self) -> bool:
        """Ensure list_view is available. Returns False if unavailable."""
        if not self.list_view:
            try:
                self.list_view = self.query_one(ListView)
            except Exception as e:
                self.log(f"Failed to get list_view: {e}")
                return False
        return True

    def _get_sorted_entries(self) -> list[Entry]:
        """Get entries sorted/grouped according to current settings."""
        entries = self._filter_entries(self.entries)

        if self.group_by_feed:
            # When grouping by feed, sort by feed name then by date
            return sorted(
                entries,
                key=lambda e: (e.feed.title.lower(), e.published_at),
                reverse=False,
            )
        return self._sort_entries(entries)

    def _display_entries(self, entries: list[Entry]):
        """Display entries in list view based on grouping setting."""
        if self.group_by_feed:
            self._add_grouped_entries(entries)
        else:
            self._add_flat_entries(entries)

    def _sort_entries(self, entries: list[Entry]) -> list[Entry]:
        """Sort entries based on current sort mode.

        Sort modes:
        - "feed": Alphabetically by feed name, then newest entries first
        - "date": Newest entries first (most recent publication date)
        - "status": Unread entries first, then by date (oldest first)
        """
        if self.current_sort == "feed":
            # Sort by feed name (A-Z), then by date (newest first within each feed)
            # reverse=True moves newest to top when combined with negative key
            return sorted(
                entries,
                key=lambda e: (e.feed.title.lower(), e.published_at),
                reverse=True,
            )
        if self.current_sort == "date":
            # Sort by published date (newest entries first)
            # reverse=True puts most recent at top
            return sorted(entries, key=lambda e: e.published_at, reverse=True)
        if self.current_sort == "status":
            # Sort by read status (unread first), then by date (oldest first)
            # is_read sorts False (unread) before True (read)
            # reverse=False keeps oldest first within each status group
            return sorted(
                entries,
                key=lambda e: (e.is_read, e.published_at),
                reverse=False,
            )
        return entries

    def _filter_entries(self, entries: list[Entry]) -> list[Entry]:
        """Apply active filters to entries.

        Filters are mutually exclusive - only one can be active at a time.
        - filter_unread_only: Show only entries with status="unread"
        - filter_starred_only: Show only entries with starred=True
        - Neither active: Show all entries passed in

        Args:
            entries: List of entries to filter

        Returns:
            Filtered list of entries
        """
        if self.filter_unread_only:
            # Show only unread entries
            return [e for e in entries if e.is_unread]
        if self.filter_starred_only:
            # Show only starred entries
            return [e for e in entries if e.starred]
        # No filters active, return all entries
        return entries

    def _add_grouped_entries(self, entries: list[Entry]):
        """Add entries grouped by feed with optional collapsible headers.

        All entries are added to the list, but entries in collapsed feeds
        are hidden via CSS class. This preserves cursor position during expand/collapse.
        """
        current_feed = None
        first_feed = None
        self.displayed_items = []
        self.entry_item_map.clear()
        self.feed_header_map.clear()

        for entry in entries:
            # Add feed header if this is a new feed
            if current_feed != entry.feed.title:
                current_feed = entry.feed.title
                if first_feed is None:
                    first_feed = current_feed
                    # Set default position to first feed if not already set
                    if not self.last_highlighted_feed:
                        self.last_highlighted_feed = first_feed

                # Initialize fold state for this feed if needed
                if current_feed not in self.feed_fold_state:
                    # Default: expanded if not set, unless group_collapsed is True
                    self.feed_fold_state[current_feed] = not self.group_collapsed

                # Create and add a fold-aware header item
                is_expanded = self.feed_fold_state[current_feed]
                header = FeedHeaderItem(current_feed, is_expanded=is_expanded)
                self.feed_header_map[current_feed] = header
                self.list_view.append(header)

            # Always add the entry, but apply "collapsed" CSS class if feed is collapsed
            item = EntryListItem(entry, self.unread_color, self.read_color)
            self.displayed_items.append(item)
            self.entry_item_map[entry.id] = item

            # Apply "collapsed" class if this feed is collapsed
            # current_feed is guaranteed to be set here (see line 316)
            if current_feed and not self.feed_fold_state[current_feed]:
                item.add_class("collapsed")

            self.list_view.append(item)

    def _add_flat_entries(self, entries: list[Entry]):
        """Add entries as a flat list."""
        self.displayed_items = []
        self.entry_item_map.clear()
        for entry in entries:
            item = EntryListItem(entry, self.unread_color, self.read_color)
            self.displayed_items.append(item)
            self.entry_item_map[entry.id] = item
            self.list_view.append(item)

    def _update_single_item(self, entry: Entry) -> bool:
        """Update a single entry item in the list (incremental refresh).

        This avoids rebuilding the entire list when only one entry changes.

        Args:
            entry: The entry to update

        Returns:
            True if item was updated, False if item not found or refresh needed
        """
        # Check if item is in the current view
        if entry.id not in self.entry_item_map:
            return False

        old_item = self.entry_item_map[entry.id]

        # Create new item with updated data
        new_item = EntryListItem(entry, self.unread_color, self.read_color)
        self.entry_item_map[entry.id] = new_item

        # Find the index of the old item in the list view
        try:
            children_list = list(self.list_view.children)
            index = children_list.index(old_item)
            # Remove the old item
            old_item.remove()
            # Get the item that's now at that position (if exists)
            current_children = list(self.list_view.children)
            # Mount new item before the item that's now at that index
            if index < len(current_children):
                self.list_view.mount(new_item, before=current_children[index])
            else:
                self.list_view.mount(new_item)
            # Update displayed_items if it's in there
            if old_item in self.displayed_items:
                item_index = self.displayed_items.index(old_item)
                self.displayed_items[item_index] = new_item
            self.refresh_optimizer.track_partial_refresh()
            return True
        except (ValueError, IndexError):
            return False

    def _is_item_visible(self, item: ListItem) -> bool:
        """Check if an item is visible (not hidden by CSS class)."""
        return "collapsed" not in item.classes

    def action_cursor_down(self):
        """Move cursor down to next visible entry item, skipping collapsed entries."""
        if not self.list_view or len(self.list_view.children) == 0:
            return

        try:
            current_index = self.list_view.index
            # If index is None, start searching from -1 so range(0, ...) includes index 0
            if current_index is None:
                current_index = -1

            # Move to next item and skip hidden ones
            for i in range(current_index + 1, len(self.list_view.children)):
                widget = self.list_view.children[i]
                if isinstance(widget, ListItem) and self._is_item_visible(widget):
                    self.list_view.index = i
                    return

            # If no visible item found below, stay at current position
        except (IndexError, ValueError, TypeError):
            pass

    def action_cursor_up(self):
        """Move cursor up to previous visible entry item, skipping collapsed entries."""
        if not self.list_view or len(self.list_view.children) == 0:
            return

        try:
            current_index = self.list_view.index
            # If index is None, start from len so we search backwards from end
            if current_index is None:
                current_index = len(self.list_view.children)

            # Move to previous item and skip hidden ones
            for i in range(current_index - 1, -1, -1):
                widget = self.list_view.children[i]
                if isinstance(widget, ListItem) and self._is_item_visible(widget):
                    self.list_view.index = i
                    return

            # If no visible item found above, stay at current position
        except (IndexError, ValueError, TypeError):
            pass

    async def action_toggle_read(self):
        """Toggle read/unread status of current entry."""
        if not self.list_view:
            return

        highlighted = self.list_view.highlighted_child
        if highlighted and isinstance(highlighted, EntryListItem) and hasattr(self.app, "client") and self.app.client:
            try:
                # Determine new status
                new_status = "read" if highlighted.entry.is_unread else "unread"

                # Call API to persist change
                await self.app.client.change_entry_status(highlighted.entry.id, new_status)

                # Update local state
                highlighted.entry.status = new_status

                # Try incremental update first; fall back to full refresh if needed
                if not self._update_single_item(highlighted.entry):
                    # Fall back to full refresh if incremental update fails
                    self._populate_list()

                # Notify user
                self.notify(f"Entry marked as {new_status}")
            except Exception as e:
                self.notify(f"Error updating status: {e}", severity="error")

    async def action_toggle_star(self):
        """Toggle star status of current entry."""
        if not self.list_view:
            return

        highlighted = self.list_view.highlighted_child
        if highlighted and isinstance(highlighted, EntryListItem) and hasattr(self.app, "client") and self.app.client:
            try:
                # Call API to toggle star
                await self.app.client.toggle_starred(highlighted.entry.id)

                # Update local state
                highlighted.entry.starred = not highlighted.entry.starred

                # Try incremental update first; fall back to full refresh if needed
                if not self._update_single_item(highlighted.entry):
                    # Fall back to full refresh if incremental update fails
                    self._populate_list()

                # Notify user
                status = "starred" if highlighted.entry.starred else "unstarred"
                self.notify(f"Entry {status}")
            except Exception as e:
                self.notify(f"Error toggling star: {e}", severity="error")

    async def action_save_entry(self):
        """Save entry to third-party service."""
        if not self.list_view:
            return

        highlighted = self.list_view.highlighted_child
        if highlighted and isinstance(highlighted, EntryListItem) and hasattr(self.app, "client") and self.app.client:
            try:
                await self.app.client.save_entry(highlighted.entry.id)
                self.notify(f"Entry saved: {highlighted.entry.title}")
            except Exception as e:
                self.notify(f"Failed to save entry: {e}", severity="error")

    def action_cycle_sort(self):
        """Cycle through sort modes."""
        current_index = SORT_MODES.index(self.current_sort)
        self.current_sort = SORT_MODES[(current_index + 1) % len(SORT_MODES)]

        # Update title to show current sort
        self.sub_title = f"Sort: {self.current_sort.title()}"

        # Re-populate list
        self._populate_list()

    def action_toggle_group(self):
        """Toggle grouping by feed."""
        self.group_by_feed = not self.group_by_feed
        self._populate_list()

    def action_toggle_fold(self):
        """Toggle fold state of highlighted feed (only works in grouped mode)."""
        if not self.list_view or not self.group_by_feed:
            return

        highlighted = self.list_view.highlighted_child
        if highlighted and isinstance(highlighted, FeedHeaderItem):
            feed_title = highlighted.feed_title
            # Save current position
            self.last_highlighted_feed = feed_title
            # Toggle the fold state
            self.feed_fold_state[feed_title] = not self.feed_fold_state[feed_title]
            highlighted.toggle_fold()

            # Update CSS class for entries: toggle "collapsed" class
            self._update_feed_visibility(feed_title)

    def _update_feed_visibility(self, feed_title: str) -> None:
        """Update CSS visibility for all entries of a feed based on fold state.

        If feed is collapsed, adds 'collapsed' class to hide entries.
        If feed is expanded, removes 'collapsed' class to show entries.
        """
        is_expanded = self.feed_fold_state.get(feed_title, True)

        # Find all entries for this feed and update their CSS class
        for item in self.list_view.children:
            if isinstance(item, EntryListItem) and item.entry.feed.title == feed_title:
                if is_expanded:
                    item.remove_class("collapsed")
                else:
                    item.add_class("collapsed")

    def action_collapse_feed(self):
        """Collapse the highlighted feed (h or left arrow)."""
        if not self.list_view or not self.group_by_feed:
            return

        highlighted = self.list_view.highlighted_child
        if not highlighted:
            return

        feed_title = None

        # Get feed title from header or entry
        if isinstance(highlighted, FeedHeaderItem):
            feed_title = highlighted.feed_title
        elif isinstance(highlighted, EntryListItem):
            feed_title = highlighted.entry.feed.title
        else:
            return

        if not feed_title:
            return

        # Save position for return from entry reader
        self.last_highlighted_feed = feed_title

        # Ensure fold state exists
        if feed_title not in self.feed_fold_state:
            self.feed_fold_state[feed_title] = not self.group_collapsed

        # Only collapse if currently expanded
        is_currently_expanded = self.feed_fold_state[feed_title]
        if is_currently_expanded:
            self.feed_fold_state[feed_title] = False
            # Update the header's visual fold icon
            if feed_title in self.feed_header_map:
                self.feed_header_map[feed_title].toggle_fold()
            # Update CSS visibility for entries
            self._update_feed_visibility(feed_title)

    def action_expand_feed(self):
        """Expand the highlighted feed (l or right arrow)."""
        if not self.list_view or not self.group_by_feed:
            return

        highlighted = self.list_view.highlighted_child
        if not highlighted:
            return

        feed_title = None

        # Get feed title from header or entry
        if isinstance(highlighted, FeedHeaderItem):
            feed_title = highlighted.feed_title
        elif isinstance(highlighted, EntryListItem):
            feed_title = highlighted.entry.feed.title
        else:
            return

        if not feed_title:
            return

        # Save position for return from entry reader
        self.last_highlighted_feed = feed_title

        # Ensure fold state exists
        if feed_title not in self.feed_fold_state:
            self.feed_fold_state[feed_title] = not self.group_collapsed

        # Only expand if currently collapsed
        is_currently_collapsed = not self.feed_fold_state[feed_title]
        if is_currently_collapsed:
            self.feed_fold_state[feed_title] = True
            # Update the header's visual fold icon
            if feed_title in self.feed_header_map:
                self.feed_header_map[feed_title].toggle_fold()
            # Update CSS visibility for entries
            self._update_feed_visibility(feed_title)

    async def action_refresh(self):
        """Refresh the entry list from API."""
        if hasattr(self.app, "load_entries"):
            self.notify("Refreshing entries...")
            # Reload entries from API (this will fetch only unread entries)
            await self.app.load_entries(self.app.current_view)
            self.notify("Entries refreshed")

    async def action_show_unread(self):
        """Load and show only unread entries."""
        if hasattr(self.app, "load_entries"):
            await self.app.load_entries("unread")
            self.filter_unread_only = False
            self.filter_starred_only = False
            self._populate_list()

    async def action_show_starred(self):
        """Load and show only starred entries."""
        if hasattr(self.app, "load_entries"):
            await self.app.load_entries("starred")
            self.filter_unread_only = False
            self.filter_starred_only = False
            self._populate_list()

    def action_show_help(self):
        """Show keyboard help."""
        self.app.push_screen("help")

    def action_quit(self):
        """Quit the application."""
        self.app.exit()
