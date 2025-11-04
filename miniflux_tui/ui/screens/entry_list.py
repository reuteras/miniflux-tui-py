"""Entry list screen with feed sorting capabilities."""

from contextlib import suppress
from typing import TYPE_CHECKING, Any, cast

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from miniflux_tui.api.models import Category, Entry
from miniflux_tui.constants import (
    FOLD_COLLAPSED,
    FOLD_EXPANDED,
    SORT_MODES,
)
from miniflux_tui.performance import ScreenRefreshOptimizer
from miniflux_tui.utils import api_call, get_star_icon, get_status_icon

if TYPE_CHECKING:
    MinifluxTuiApp = Any


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

    def __init__(
        self,
        feed_title: str,
        is_expanded: bool = True,
        category_title: str | None = None,
        has_errors: bool = False,
        feed_disabled: bool = False,
    ):
        self.feed_title = feed_title
        self.is_expanded = is_expanded
        self.category_title = category_title
        self.has_errors = has_errors
        self.feed_disabled = feed_disabled

        # Format header with fold indicator, category, and error indicators
        fold_icon = FOLD_EXPANDED if is_expanded else FOLD_COLLAPSED
        error_indicators = []

        if feed_disabled:
            error_indicators.append("[red]⊘ DISABLED[/red]")
        elif has_errors:
            error_indicators.append("[yellow]⚠ ERRORS[/yellow]")

        error_text = " ".join(error_indicators)

        if category_title:
            if error_text:
                header_text = f"[bold]{fold_icon} {feed_title}[/bold] [dim]({category_title})[/dim] {error_text}"
            else:
                header_text = f"[bold]{fold_icon} {feed_title}[/bold] [dim]({category_title})[/dim]"
        elif error_text:
            header_text = f"[bold]{fold_icon} {feed_title}[/bold] {error_text}"
        else:
            header_text = f"[bold]{fold_icon} {feed_title}[/bold]"

        label = Label(header_text, classes="feed-header")

        # Initialize with the label
        super().__init__(label)

    def toggle_fold(self) -> None:
        """Toggle the fold state and update display."""
        self.is_expanded = not self.is_expanded
        fold_icon = FOLD_EXPANDED if self.is_expanded else FOLD_COLLAPSED

        error_indicators = []
        if self.feed_disabled:
            error_indicators.append("[red]⊘ DISABLED[/red]")
        elif self.has_errors:
            error_indicators.append("[yellow]⚠ ERRORS[/yellow]")

        error_text = " ".join(error_indicators)

        if self.category_title:
            if error_text:
                header_text = f"[bold]{fold_icon} {self.feed_title}[/bold] [dim]({self.category_title})[/dim] {error_text}"
            else:
                header_text = f"[bold]{fold_icon} {self.feed_title}[/bold] [dim]({self.category_title})[/dim]"
        elif error_text:
            header_text = f"[bold]{fold_icon} {self.feed_title}[/bold] {error_text}"
        else:
            header_text = f"[bold]{fold_icon} {self.feed_title}[/bold]"

        # Update the label
        if self.children:
            cast(Label, self.children[0]).update(header_text)


class CategoryHeaderItem(ListItem):
    """Custom list item for category header with fold/unfold capability."""

    def __init__(self, category_title: str, is_expanded: bool = True):
        self.category_title = category_title
        self.is_expanded = is_expanded

        # Format header with fold indicator
        fold_icon = FOLD_EXPANDED if is_expanded else FOLD_COLLAPSED
        header_text = f"[bold cyan]{fold_icon} [CATEGORY] {category_title}[/bold cyan]"
        label = Label(header_text, classes="category-header")

        # Initialize with the label
        super().__init__(label)

    def toggle_fold(self) -> None:
        """Toggle the fold state and update display."""
        self.is_expanded = not self.is_expanded
        fold_icon = FOLD_EXPANDED if self.is_expanded else FOLD_COLLAPSED
        header_text = f"[bold cyan]{fold_icon} [CATEGORY] {self.category_title}[/bold cyan]"
        # Update the label
        if self.children:
            cast(Label, self.children[0]).update(header_text)


class EntryListScreen(Screen):
    """Screen for displaying a list of feed entries with sorting."""

    BINDINGS = [  # noqa: RUF012
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("enter", "select_entry", "Open Entry"),
        Binding("m", "toggle_read", "Mark Read/Unread"),
        Binding("asterisk", "toggle_star", "Toggle Star"),
        Binding("e", "save_entry", "Save Entry"),
        Binding("s", "cycle_sort", "Cycle Sort"),
        Binding("X", "scraping_helper", "Scraping Helper"),
        Binding("g", "toggle_group_feed", "Group by Feed"),
        Binding("c", "toggle_group_category", "Group by Category"),
        Binding("M", "manage_categories", "Manage Categories"),
        Binding("G", "expand_all", "Expand All"),
        Binding("Z", "collapse_all", "Collapse All"),
        Binding("o", "toggle_fold", "Fold/Unfold Feed/Category"),
        Binding("h", "collapse_fold", "Collapse Feed/Category"),
        Binding("l", "expand_fold", "Expand Feed/Category"),
        Binding("left", "collapse_fold", "Collapse Feed/Category", show=False),
        Binding("right", "expand_fold", "Expand Feed/Category", show=False),
        Binding("r", "refresh", "Refresh Current Feed"),
        Binding("comma", "sync_entries", "Sync Entries", show=False),
        Binding("R", "refresh_all_feeds", "Refresh All Feeds"),
        Binding("u", "show_unread", "Unread"),
        Binding("t", "show_starred", "Starred"),
        Binding("slash", "search", "Search"),
        Binding("question_mark", "show_help", "Help"),
        Binding("i", "show_status", "Status"),
        Binding("S", "show_settings", "Settings"),
        Binding("H", "show_history", "History"),
        Binding("q", "quit", "Quit"),
    ]

    app: "MinifluxTuiApp"

    def __init__(
        self,
        entries: list[Entry],
        categories: list[Category] | None = None,
        *,
        unread_color: str = "cyan",
        read_color: str = "gray",
        default_sort: str = "date",
        group_by_feed: bool = False,
        group_collapsed: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entries = entries
        self.categories = categories or []
        self.sorted_entries = entries.copy()  # Store sorted entries for navigation
        self.unread_color = unread_color
        self.read_color = read_color
        self.current_sort = default_sort
        self.group_by_feed = group_by_feed
        self.group_by_category = False  # Option to group by category instead of feed
        self.group_collapsed = group_collapsed  # Start feeds collapsed in grouped mode
        self.filter_unread_only = False  # Filter to show only unread entries
        self.filter_starred_only = False  # Filter to show only starred entries
        self.filter_category_id: int | None = None  # Filter to show entries from selected category only
        self.search_active = False  # Flag to indicate search is active
        self.search_term = ""  # Current search term
        self.list_view: ListView | None = None
        self.displayed_items: list[ListItem] = []  # Track items in display order
        self.refresh_optimizer = ScreenRefreshOptimizer()  # Track refresh performance
        self.entry_item_map: dict[int, EntryListItem] = {}  # Map entry IDs to list items
        self.feed_header_map: dict[str, FeedHeaderItem] = {}  # Map feed names to header items
        self.category_header_map: dict[str, CategoryHeaderItem] = {}  # Map category names to header items
        self.feed_fold_state: dict[str, bool] = {}  # Track fold state per feed (True = expanded)
        self.category_fold_state: dict[str, bool] = {}  # Track fold state per category (True = expanded)
        self.last_highlighted_feed: str | None = None  # Track last highlighted feed for position persistence
        self.last_highlighted_category: str | None = None  # Track last highlighted category for position persistence
        self.last_highlighted_entry_id: int | None = None  # Track last highlighted entry ID for position
        self.last_cursor_index: int = 0  # Track cursor position for non-grouped mode
        self._header_widget: Header | None = None
        self._footer_widget: Footer | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        header = Header()
        list_view = ListView()
        footer = Footer()

        # Store references for later use (e.g. focus management)
        self._header_widget = header
        self.list_view = list_view
        self._footer_widget = footer

        yield header
        yield list_view
        yield footer

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Get reference to the ListView after it's mounted
        self.list_view = self.query_one(ListView)
        self.log(f"on_mount: list_view is now {self.list_view}")

        # Only populate if we have entries
        if self.entries:
            self.log(f"on_mount: Populating with {len(self.entries)} entries")
            self._populate_list()
            # Use call_later to defer focus and cursor restoration until ListView has updated
            if self.group_by_feed:
                self.call_later(self._restore_cursor_position_and_focus)
            else:
                self.call_later(self._ensure_focus)
        else:
            self.log("on_mount: No entries yet, skipping initial population")

    def on_screen_resume(self) -> None:
        """Called when screen is resumed (e.g., after returning from entry reader)."""
        # Refresh the list to reflect any status changes
        if self.entries and self.list_view:
            self._populate_list()
            # Use call_later to defer focus and cursor restoration until ListView has updated
            # Always restore cursor position to maintain user's navigation context
            self.call_later(self._restore_cursor_position_and_focus)
        elif self.list_view and len(self.list_view.children) > 0:
            # If no entries, just ensure focus
            self.call_later(self._ensure_focus)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle ListView selection (Enter key)."""
        if event.item and isinstance(event.item, FeedHeaderItem):
            # Open first entry in the selected feed
            self._open_first_entry_by_feed(event.item.feed_title)
        elif event.item and isinstance(event.item, CategoryHeaderItem):
            # Open first entry in the selected category
            self._open_first_entry_by_category(event.item.category_title)
        elif event.item and isinstance(event.item, EntryListItem):
            # Open the selected entry directly
            self._open_entry(event.item.entry)

    def _open_first_entry_by_feed(self, feed_title: str) -> None:
        """Find and open the first entry in a feed."""
        for entry in self.sorted_entries:
            if entry.feed.title == feed_title:
                self._open_entry(entry)
                return

    def _open_first_entry_by_category(self, category_title: str) -> None:
        """Find and open the first entry in a category."""
        for entry in self.sorted_entries:
            if self._get_category_title(entry.feed.category_id) == category_title:
                self._open_entry(entry)
                return

    def _open_entry(self, entry: Entry) -> None:
        """Open an entry in the entry reader screen."""
        # Save the entry for position restoration
        self.last_highlighted_feed = entry.feed.title
        self.last_highlighted_entry_id = entry.id

        # Save the cursor index in the list view
        if self.list_view and self.list_view.index is not None:
            self.last_cursor_index = self.list_view.index

        # Find the index of this entry in the sorted entry list
        entry_index = 0
        for i, e in enumerate(self.sorted_entries):
            if e.id == entry.id:
                entry_index = i
                break

        # Open entry reader screen with navigation context
        if isinstance(self.app, self.app.__class__) and hasattr(self.app, "push_entry_reader"):
            self.app.push_entry_reader(entry=entry, entry_list=self.sorted_entries, current_index=entry_index)

    def _populate_list(self):
        """Populate the list with sorted and filtered entries."""
        if not self._ensure_list_view():
            return

        self.list_view.clear()
        sorted_entries = self._get_sorted_entries()
        self.sorted_entries = sorted_entries
        self._display_entries(sorted_entries)
        self.refresh_optimizer.track_full_refresh()

        # Don't set initial index here - let _restore_cursor_position handle it
        # This prevents overwriting the cursor position when returning from entry reader

    def _find_entry_index_by_id(self, entry_id: int | None) -> int | None:
        """Find the index of an entry by its ID.

        Searches the list view for an EntryListItem with matching entry ID.
        Returns None if not found or if entry_id is not set.

        Args:
            entry_id: ID of the entry to find

        Returns:
            Index of the entry in list view, or None if not found
        """
        if not entry_id:
            return None

        for i, child in enumerate(self.list_view.children):
            if isinstance(child, EntryListItem) and child.entry.id == entry_id:
                return i

        return None

    def _find_feed_header_index(self, feed_title: str | None) -> int | None:
        """Find the index of a feed header by title.

        Searches the list view for a FeedHeaderItem with matching feed title.
        Returns None if not found or feed not in map.

        Args:
            feed_title: Title of the feed to find

        Returns:
            Index of the feed header in list view, or None if not found
        """
        if not feed_title or not self.group_by_feed or feed_title not in self.feed_header_map:
            return None

        feed_header = self.feed_header_map[feed_title]
        for i, child in enumerate(self.list_view.children):
            if child is feed_header:
                return i

        return None

    def _set_cursor_to_index(self, index: int) -> bool:
        """Safely set cursor to a specific index.

        Handles boundary checking and suppresses exceptions.

        Args:
            index: Target index

        Returns:
            True if successful, False otherwise
        """
        max_index = len(self.list_view.children) - 1
        if index > max_index:
            return False

        with suppress(Exception):
            self.list_view.index = index
            return True

        return False

    def _restore_cursor_position(self) -> None:
        """Restore cursor position based on mode.

        Attempts restoration in this order:
        1. Restore to the last highlighted entry by ID (all modes)
        2. Restore to the last highlighted feed header (grouped mode only)
        3. Restore to the last cursor index (fallback)

        Used after rebuilding the list to restore user's position.
        On initial mount, defaults to first item.
        """
        if not self.list_view or len(self.list_view.children) == 0:
            return

        # Try to restore to last highlighted entry by ID
        entry_index = self._find_entry_index_by_id(self.last_highlighted_entry_id)
        if entry_index is not None and self._set_cursor_to_index(entry_index):
            self.log(f"Restoring cursor to entry {self.last_highlighted_entry_id} at index {entry_index}")
            return

        # In grouped mode, try to restore to feed header
        feed_index = self._find_feed_header_index(self.last_highlighted_feed)
        if feed_index is not None and self._set_cursor_to_index(feed_index):
            self.log(f"Restoring cursor to feed header '{self.last_highlighted_feed}' at index {feed_index}")
            return

        # Fallback: restore to last cursor index
        max_index = len(self.list_view.children) - 1
        cursor_index = min(self.last_cursor_index, max_index)
        if self._set_cursor_to_index(cursor_index):
            self.log(f"Restoring cursor to last index {cursor_index}")

    def _restore_cursor_position_and_focus(self) -> None:
        """Restore cursor position and ensure focus (called after ListView update)."""
        self._restore_cursor_position()
        self._ensure_focus()

    def _ensure_focus(self) -> None:
        """Ensure ListView has focus for keyboard input."""
        if self.list_view and len(self.list_view.children) > 0:
            with suppress(Exception):
                self.list_view.focus()

    def _ensure_list_view(self) -> bool:
        """Ensure list_view is available. Returns False if unavailable."""
        if not self.list_view:
            try:
                self.list_view = self.query_one(ListView)
            except Exception as e:
                self.log(f"Failed to get list_view: {e}")
                return False
        return True

    def _get_highlighted_feed_title(self) -> str | None:
        """Extract feed title from currently highlighted list item.

        Returns the feed title from either a FeedHeaderItem or EntryListItem.
        This eliminates the repeated pattern of checking item type and
        extracting feed title across multiple methods.

        Returns:
            Feed title if found, None otherwise
        """
        if not self.list_view:
            return None

        highlighted = self.list_view.highlighted_child
        if not highlighted:
            return None

        if isinstance(highlighted, FeedHeaderItem):
            return highlighted.feed_title
        if isinstance(highlighted, EntryListItem):
            return highlighted.entry.feed.title
        return None

    def _set_feed_fold_state(self, feed_title: str, is_expanded: bool) -> None:
        """Set fold state for a feed and update UI.

        Updates the feed's fold state, toggles the header visual indicator,
        and updates the CSS visibility of feed entries. This eliminates the
        repeated pattern of state management across collapse/expand methods.

        Args:
            feed_title: Title of the feed to update
            is_expanded: True to expand feed, False to collapse
        """
        # Ensure fold state entry exists
        if feed_title not in self.feed_fold_state:
            self.feed_fold_state[feed_title] = not self.group_collapsed

        # Update fold state
        self.feed_fold_state[feed_title] = is_expanded

        # Update header visual indicator
        if feed_title in self.feed_header_map:
            self.feed_header_map[feed_title].toggle_fold()

        # Update CSS visibility
        self._update_feed_visibility(feed_title)

    def _set_category_fold_state(self, category_title: str, is_expanded: bool) -> None:
        """Set fold state for a category and update UI.

        Updates the category's fold state, toggles the header visual indicator,
        and updates the CSS visibility of category entries.

        Args:
            category_title: Title of the category to update
            is_expanded: True to expand category, False to collapse
        """
        # Ensure fold state entry exists
        if category_title not in self.category_fold_state:
            self.category_fold_state[category_title] = not self.group_collapsed

        # Update fold state
        self.category_fold_state[category_title] = is_expanded

        # Update header visual indicator
        if category_title in self.category_header_map:
            self.category_header_map[category_title].toggle_fold()

        # Update CSS visibility
        self._update_category_visibility(category_title)

    def _ensure_list_view_and_grouped(self) -> bool:
        """Ensure list view is available and we're in grouped mode.

        Consolidates the common check: list_view exists and group_by_feed is True.
        This eliminates repeated `if not self.list_view or not self.group_by_feed` checks.

        Returns:
            True if list_view is available and grouped mode is enabled, False otherwise
        """
        return self._ensure_list_view() and self.group_by_feed

    def _list_view_has_items(self) -> bool:
        """Check if list view exists and has children.

        Consolidates the common check for both list view availability and
        checking if it has items. Used to determine if there are entries to work with.

        Returns:
            True if list_view exists and has children, False otherwise
        """
        return self.list_view is not None and len(self.list_view.children) > 0

    def _get_sorted_entries(self) -> list[Entry]:
        """Get entries sorted/grouped according to current settings."""
        entries = self._filter_entries(self.entries)

        if self.group_by_category:
            # When grouping by category, sort by category title then by date
            # Get category title from entry's feed's category_id
            return sorted(
                entries,
                key=lambda e: (self._get_category_title(e.feed.category_id).lower(), e.published_at),
                reverse=False,
            )
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
        if self.group_by_category:
            self._add_grouped_entries_by_category(entries)
        elif self.group_by_feed:
            self._add_grouped_entries(entries)
        else:
            self._add_flat_entries(entries)

    def _sort_entries(self, entries: list[Entry]) -> list[Entry]:
        """Sort entries based on current sort mode.

        Sort modes:
        - "feed": Alphabetically by feed name (A-Z), then newest entries first within each feed
        - "date": Newest entries first (most recent publication date)
        - "status": Unread entries first, then by date (oldest first)
        """
        if self.current_sort == "feed":
            # Sort by feed name (A-Z), then by date (newest first within each feed)
            # Use a tuple key with negative date for newest-first within each feed
            return sorted(
                entries,
                key=lambda e: (e.feed.title.lower(), -e.published_at.timestamp()),
                reverse=False,
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

        Filters are applied in order:
        1. Category filter (if set)
        2. Search filter (if active)
        3. Status filters (unread/starred - mutually exclusive)

        Args:
            entries: List of entries to filter

        Returns:
            Filtered list of entries
        """
        # Apply category filter first if set
        if self.filter_category_id is not None:
            entries = [e for e in entries if e.feed.category_id == self.filter_category_id]

        # Apply search filter if active
        if self.search_active and self.search_term:
            entries = self._filter_search(entries)

        # Apply status filters (mutually exclusive - only one can be active at a time)
        if self.filter_unread_only:
            # Show only unread entries
            return [e for e in entries if e.is_unread]
        if self.filter_starred_only:
            # Show only starred entries
            return [e for e in entries if e.starred]
        # No status filters active, return all entries (after other filters if applied)
        return entries

    def _filter_search(self, entries: list[Entry]) -> list[Entry]:
        """Filter entries by search term in title and content.

        Searches across both entry titles and HTML content. Search is case-insensitive.

        Args:
            entries: List of entries to search

        Returns:
            Filtered list of matching entries
        """
        search_lower = self.search_term.lower()
        return [e for e in entries if search_lower in e.title.lower() or search_lower in e.content.lower()]

    def _add_feed_header_if_needed(self, current_feed: str, first_feed_ref: list, entry: Entry | None = None) -> None:
        """Add a feed header if transitioning to a new feed.

        Initializes fold state and creates a FeedHeaderItem for the new feed.

        Args:
            current_feed: Title of the current feed
            first_feed_ref: List with one element to track first feed (mutable ref pattern)
            entry: Entry object to extract category information from
        """
        # Track first feed for default positioning
        if first_feed_ref[0] is None:
            first_feed_ref[0] = current_feed
            # Set default position to first feed if not already set
            if not self.last_highlighted_feed:
                self.last_highlighted_feed = first_feed_ref[0]

        # Initialize fold state for this feed if needed
        if current_feed not in self.feed_fold_state:
            # Default: expanded if not set, unless group_collapsed is True
            self.feed_fold_state[current_feed] = not self.group_collapsed

        # Get category title and error status if entry is provided
        category_title = None
        has_errors = False
        feed_disabled = False
        if entry is not None:
            category_title = self._get_category_title(entry.feed.category_id)
            has_errors = entry.feed.has_errors
            feed_disabled = entry.feed.disabled

        # Create and add a fold-aware header item
        is_expanded = self.feed_fold_state[current_feed]
        header = FeedHeaderItem(
            current_feed,
            is_expanded=is_expanded,
            category_title=category_title,
            has_errors=has_errors,
            feed_disabled=feed_disabled,
        )
        self.feed_header_map[current_feed] = header
        self.list_view.append(header)

    def _add_entry_with_visibility(self, entry: Entry) -> None:
        """Add an entry item with appropriate visibility based on feed state.

        Applies "collapsed" CSS class if the entry's feed is collapsed.

        Args:
            entry: The entry to add
        """
        item = EntryListItem(entry, self.unread_color, self.read_color)
        self.displayed_items.append(item)
        self.entry_item_map[entry.id] = item

        # Apply "collapsed" class if this feed is collapsed
        # We can safely access feed_fold_state since headers are created first
        if not self.feed_fold_state.get(entry.feed.title, not self.group_collapsed):
            item.add_class("collapsed")

        self.list_view.append(item)

    def _add_grouped_entries(self, entries: list[Entry]):
        """Add entries grouped by feed with optional collapsible headers.

        All entries are added to the list, but entries in collapsed feeds
        are hidden via CSS class. This preserves cursor position during expand/collapse.
        """
        current_feed = None
        first_feed = [None]  # Use list as mutable reference for tracking first feed
        self.displayed_items = []
        self.entry_item_map.clear()
        self.feed_header_map.clear()

        for entry in entries:
            # Add feed header if this is a new feed
            if current_feed != entry.feed.title:
                current_feed = entry.feed.title
                self._add_feed_header_if_needed(current_feed, first_feed, entry)

            # Add the entry with appropriate visibility
            self._add_entry_with_visibility(entry)

    def _add_flat_entries(self, entries: list[Entry]):
        """Add entries as a flat list."""
        self.displayed_items = []
        self.entry_item_map.clear()
        for entry in entries:
            item = EntryListItem(entry, self.unread_color, self.read_color)
            self.displayed_items.append(item)
            self.entry_item_map[entry.id] = item
            self.list_view.append(item)

    def _get_category_title(self, category_id: int | None) -> str:
        """Get category title from category ID.

        Args:
            category_id: The category ID to lookup

        Returns:
            Category title, or "Uncategorized" if not found
        """
        if category_id is None:
            return "Uncategorized"

        if not self.categories:
            return f"Category {category_id}"

        for category in self.categories:
            if category.id == category_id:
                return category.title

        return f"Category {category_id}"

    def _add_category_header_if_needed(self, category_title: str, first_category_ref: list) -> None:
        """Add a category header if transitioning to a new category.

        Initializes fold state and creates a CategoryHeaderItem for the new category.

        Args:
            category_title: Title of the current category
            first_category_ref: List with one element to track first category (mutable ref pattern)
        """
        # Track first category for default positioning
        if first_category_ref[0] is None:
            first_category_ref[0] = category_title
            # Set default position to first category if not already set
            if not self.last_highlighted_category:
                self.last_highlighted_category = first_category_ref[0]

        # Initialize fold state for this category if needed
        if category_title not in self.category_fold_state:
            # Default: expanded if not set, unless group_collapsed is True
            self.category_fold_state[category_title] = not self.group_collapsed

        # Create and add a fold-aware header item
        is_expanded = self.category_fold_state[category_title]
        header = CategoryHeaderItem(category_title, is_expanded=is_expanded)
        self.category_header_map[category_title] = header
        self.list_view.append(header)

    def _add_entry_with_category_visibility(self, entry: Entry, category_title: str) -> None:
        """Add an entry item with appropriate visibility based on category state.

        Applies "collapsed" CSS class if the entry's category is collapsed.

        Args:
            entry: The entry to add
            category_title: Title of the category this entry belongs to
        """
        item = EntryListItem(entry, self.unread_color, self.read_color)
        self.displayed_items.append(item)
        self.entry_item_map[entry.id] = item

        # Apply "collapsed" class if this category is collapsed
        if not self.category_fold_state.get(category_title, not self.group_collapsed):
            item.add_class("collapsed")

        self.list_view.append(item)

    def _add_grouped_entries_by_category(self, entries: list[Entry]):
        """Add entries grouped by category with optional collapsible headers.

        All entries are added to the list, but entries in collapsed categories
        are hidden via CSS class. This preserves cursor position during expand/collapse.
        """
        current_category = None
        first_category = [None]  # Use list as mutable reference for tracking first category
        self.displayed_items = []
        self.entry_item_map.clear()
        self.category_header_map.clear()

        for entry in entries:
            # Get category title for this entry
            category_title = self._get_category_title(entry.feed.category_id)

            # Add category header if this is a new category
            if current_category != category_title:
                current_category = category_title
                self._add_category_header_if_needed(current_category, first_category)

            # Add the entry with appropriate visibility
            self._add_entry_with_category_visibility(entry, category_title)

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

    @staticmethod
    def _is_item_visible(item: ListItem) -> bool:
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
            # Silently ignore index errors when navigating beyond list bounds
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
            # Silently ignore index errors when navigating beyond list bounds
            pass

    async def action_toggle_read(self):
        """Toggle read/unread status of current entry."""
        if not self.list_view:
            return

        highlighted = self.list_view.highlighted_child
        if highlighted and isinstance(highlighted, EntryListItem):
            # Determine new status
            new_status = "read" if highlighted.entry.is_unread else "unread"

            # Use consistent error handling context
            with api_call(self, f"marking entry as {new_status}") as client:
                if client is None:
                    return

                # Call API to persist change
                await client.change_entry_status(highlighted.entry.id, new_status)

                # Update local state
                highlighted.entry.status = new_status

                # Try incremental update first; fall back to full refresh if needed
                if not self._update_single_item(highlighted.entry):
                    # Fall back to full refresh if incremental update fails
                    self._populate_list()

                # Notify user of success
                self.notify(f"Entry marked as {new_status}")

    async def action_toggle_star(self):
        """Toggle star status of current entry."""
        if not self.list_view:
            return

        highlighted = self.list_view.highlighted_child
        if highlighted and isinstance(highlighted, EntryListItem):
            # Use consistent error handling context
            with api_call(self, "toggling star status") as client:
                if client is None:
                    return

                # Call API to toggle star
                await client.toggle_starred(highlighted.entry.id)

                # Update local state
                highlighted.entry.starred = not highlighted.entry.starred

                # Try incremental update first; fall back to full refresh if needed
                if not self._update_single_item(highlighted.entry):
                    # Fall back to full refresh if incremental update fails
                    self._populate_list()

                # Notify user of success
                status = "starred" if highlighted.entry.starred else "unstarred"
                self.notify(f"Entry {status}")

    async def action_save_entry(self):
        """Save entry to third-party service."""
        if not self.list_view:
            return

        highlighted = self.list_view.highlighted_child
        if highlighted and isinstance(highlighted, EntryListItem):
            # Use consistent error handling context
            with api_call(self, "saving entry") as client:
                if client is None:
                    return

                await client.save_entry(highlighted.entry.id)
                self.notify(f"Entry saved: {highlighted.entry.title}")

    def action_cycle_sort(self):
        """Cycle through sort modes."""
        current_index = SORT_MODES.index(self.current_sort)
        self.current_sort = SORT_MODES[(current_index + 1) % len(SORT_MODES)]

        # Update title to show current sort
        self.sub_title = f"Sort: {self.current_sort.title()}"

        # Re-populate list
        self._populate_list()

    def action_toggle_group_feed(self):
        """Toggle grouping by feed (g key)."""
        # Disable category grouping when enabling feed grouping
        if not self.group_by_feed and self.group_by_category:
            self.group_by_category = False

        self.group_by_feed = not self.group_by_feed

        if self.group_by_feed:
            # Start with groups collapsed when enabling
            self.group_collapsed = True
            # Clear existing fold states so new groups start collapsed
            self.feed_fold_state.clear()
            self.notify("Grouping by feed (use h/l to collapse/expand)")
        else:
            self.notify("Feed grouping disabled")

        self._populate_list()

    def action_toggle_group_category(self):
        """Toggle grouping by category (c key - Issue #54 - Category support)."""
        if not self.categories:
            self.notify("No categories available", severity="warning")
            return

        # Disable feed grouping when enabling category grouping
        if not self.group_by_category and self.group_by_feed:
            self.group_by_feed = False

        # Toggle category grouping
        self.group_by_category = not self.group_by_category

        if self.group_by_category:
            # Start with groups collapsed when enabling
            self.group_collapsed = True
            # Clear existing fold states so new groups start collapsed
            self.category_fold_state.clear()
            self.notify("Grouping by category (use h/l to collapse/expand)")
        else:
            self.notify("Category grouping disabled")

        self._populate_list()

    def action_toggle_fold(self):
        """Toggle fold state of highlighted feed or category (o key)."""
        if not self.list_view or (not self.group_by_feed and not self.group_by_category):
            return

        highlighted = self.list_view.highlighted_child

        # Handle feed grouping mode
        if self.group_by_feed and isinstance(highlighted, FeedHeaderItem):
            feed_title = highlighted.feed_title
            self.last_highlighted_feed = feed_title
            self.feed_fold_state[feed_title] = not self.feed_fold_state[feed_title]
            highlighted.toggle_fold()
            self._update_feed_visibility(feed_title)

        # Handle category grouping mode
        elif self.group_by_category and isinstance(highlighted, CategoryHeaderItem):
            category_title = highlighted.category_title
            self.last_highlighted_category = category_title
            self.category_fold_state[category_title] = not self.category_fold_state[category_title]
            highlighted.toggle_fold()
            self._update_category_visibility(category_title)

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

    def _update_category_visibility(self, category_title: str) -> None:
        """Update CSS visibility for all entries of a category based on fold state.

        If category is collapsed, adds 'collapsed' class to hide entries.
        If category is expanded, removes 'collapsed' class to show entries.
        """
        is_expanded = self.category_fold_state.get(category_title, True)

        # Find all entries for this category and update their CSS class
        for item in self.list_view.children:
            if isinstance(item, EntryListItem) and self._get_category_title(item.entry.feed.category_id) == category_title:
                if is_expanded:
                    item.remove_class("collapsed")
                else:
                    item.add_class("collapsed")

    def action_collapse_fold(self):
        """Collapse the highlighted feed or category (h or left arrow)."""
        if not self.list_view or (not self.group_by_feed and not self.group_by_category):
            return

        highlighted = self.list_view.highlighted_child

        # Handle feed grouping mode
        if self.group_by_feed and isinstance(highlighted, FeedHeaderItem):
            feed_title = highlighted.feed_title
            self.last_highlighted_feed = feed_title
            is_currently_expanded = self.feed_fold_state.get(feed_title, not self.group_collapsed)
            if is_currently_expanded:
                self._set_feed_fold_state(feed_title, False)

        # Handle category grouping mode
        elif self.group_by_category and isinstance(highlighted, CategoryHeaderItem):
            category_title = highlighted.category_title
            self.last_highlighted_category = category_title
            is_currently_expanded = self.category_fold_state.get(category_title, not self.group_collapsed)
            if is_currently_expanded:
                self._set_category_fold_state(category_title, False)

        # Fallback for entry items: collapse their parent feed/category
        elif isinstance(highlighted, EntryListItem):
            if self.group_by_feed:
                feed_title = highlighted.entry.feed.title
                self.last_highlighted_feed = feed_title
                is_currently_expanded = self.feed_fold_state.get(feed_title, not self.group_collapsed)
                if is_currently_expanded:
                    self._set_feed_fold_state(feed_title, False)
            elif self.group_by_category:
                category_title = self._get_category_title(highlighted.entry.feed.category_id)
                self.last_highlighted_category = category_title
                is_currently_expanded = self.category_fold_state.get(category_title, not self.group_collapsed)
                if is_currently_expanded:
                    self._set_category_fold_state(category_title, False)

    def action_expand_fold(self):
        """Expand the highlighted feed or category (l or right arrow)."""
        if not self.list_view or (not self.group_by_feed and not self.group_by_category):
            return

        highlighted = self.list_view.highlighted_child

        # Handle feed grouping mode
        if self.group_by_feed and isinstance(highlighted, FeedHeaderItem):
            feed_title = highlighted.feed_title
            self.last_highlighted_feed = feed_title
            is_currently_collapsed = not self.feed_fold_state.get(feed_title, not self.group_collapsed)
            if is_currently_collapsed:
                self._set_feed_fold_state(feed_title, True)

        # Handle category grouping mode
        elif self.group_by_category and isinstance(highlighted, CategoryHeaderItem):
            category_title = highlighted.category_title
            self.last_highlighted_category = category_title
            is_currently_collapsed = not self.category_fold_state.get(category_title, not self.group_collapsed)
            if is_currently_collapsed:
                self._set_category_fold_state(category_title, True)

        # Fallback for entry items: expand their parent feed/category
        elif isinstance(highlighted, EntryListItem):
            if self.group_by_feed:
                feed_title = highlighted.entry.feed.title
                self.last_highlighted_feed = feed_title
                is_currently_collapsed = not self.feed_fold_state.get(feed_title, not self.group_collapsed)
                if is_currently_collapsed:
                    self._set_feed_fold_state(feed_title, True)
            elif self.group_by_category:
                category_title = self._get_category_title(highlighted.entry.feed.category_id)
                self.last_highlighted_category = category_title
                is_currently_collapsed = not self.category_fold_state.get(category_title, not self.group_collapsed)
                if is_currently_collapsed:
                    self._set_category_fold_state(category_title, True)

    def action_expand_all(self):
        """Expand all feeds or categories (Shift+G).

        If not in grouped mode, enable feed grouping first.
        Then expand all collapsed items.
        """
        if not self.list_view:
            return

        # If not in grouped mode, enable feed grouping first
        if not self.group_by_feed and not self.group_by_category:
            self.action_toggle_group_feed()
            return

        # Expand all feeds that are currently collapsed
        if self.group_by_feed:
            for feed_title in self.feed_fold_state:
                if not self.feed_fold_state[feed_title]:
                    self._set_feed_fold_state(feed_title, True)
            self.notify("All feeds expanded")

        # Expand all categories that are currently collapsed
        elif self.group_by_category:
            for category_title in self.category_fold_state:
                if not self.category_fold_state[category_title]:
                    self._set_category_fold_state(category_title, True)
            self.notify("All categories expanded")

    def action_collapse_all(self):
        """Collapse all feeds or categories (Shift+Z)."""
        if not self.list_view or (not self.group_by_feed and not self.group_by_category):
            return

        # Collapse all feeds that are currently expanded
        if self.group_by_feed:
            for feed_title in self.feed_fold_state:
                if self.feed_fold_state[feed_title]:
                    self._set_feed_fold_state(feed_title, False)
            self.notify("All feeds collapsed")

        # Collapse all categories that are currently expanded
        elif self.group_by_category:
            for category_title in self.category_fold_state:
                if self.category_fold_state[category_title]:
                    self._set_category_fold_state(category_title, False)
            self.notify("All categories collapsed")

    async def action_refresh(self):
        """Refresh the current feed on the server (Issue #55 - Feed operations)."""
        if not hasattr(self.app, "client") or not self.app.client:
            self.notify("API client not initialized", severity="error")
            return

        # Get the currently highlighted entry to determine which feed to refresh
        if not self.list_view or self.list_view.index is None:
            self.notify("No entry selected", severity="warning")
            return

        highlighted = self.list_view.highlighted_child
        if not isinstance(highlighted, EntryListItem):
            self.notify("No entry selected", severity="warning")
            return

        try:
            feed_title = highlighted.entry.feed.title
            feed_id = highlighted.entry.feed_id

            self.notify(f"Refreshing feed: {feed_title}...")
            await self.app.client.refresh_feed(feed_id)
            self.notify(f"Feed '{feed_title}' refreshed on server")

            # Reload entries after refreshing the feed
            if hasattr(self.app, "load_entries"):
                self.notify("Reloading entries...")
                await self.app.load_entries(self.app.current_view)
                self.notify("Entries reloaded")
        except (ConnectionError, TimeoutError) as e:
            self.notify(f"Network error refreshing feed: {e}", severity="error")
        except Exception as e:
            self.notify(f"Error refreshing feed: {e}", severity="error")

    async def action_refresh_all_feeds(self):
        """Refresh all feeds on the server (Issue #55 - Feed operations)."""
        if not hasattr(self.app, "client") or not self.app.client:
            self.notify("API client not initialized", severity="error")
            return

        try:
            self.notify("Refreshing all feeds...")
            await self.app.client.refresh_all_feeds()
            self.notify("All feeds refreshed on server")

            # Reload entries after refreshing all feeds
            if hasattr(self.app, "load_entries"):
                self.notify("Reloading entries...")
                await self.app.load_entries(self.app.current_view)
                self.notify("Entries reloaded")
        except (ConnectionError, TimeoutError) as e:
            self.notify(f"Network error refreshing feeds: {e}", severity="error")
        except Exception as e:
            self.notify(f"Error refreshing all feeds: {e}", severity="error")

    async def action_sync_entries(self):
        """Sync/reload entries from server without refreshing feeds.

        This fetches the latest entries that already exist on the Miniflux server
        without telling the server to fetch new content from RSS feeds.
        Use this to get entries that were added elsewhere or by another client.
        """
        if not hasattr(self.app, "load_entries"):
            self.notify("Cannot sync entries", severity="error")
            return

        try:
            self.notify("Syncing entries from server...")
            # Rebuild category mapping for fresh data
            if hasattr(self.app, "_build_entry_category_mapping"):
                self.app.entry_category_map = await self.app._build_entry_category_mapping()
            # Reload entries without refreshing feeds
            await self.app.load_entries(self.app.current_view)
            self.notify("Entries synced")
        except (ConnectionError, TimeoutError) as e:
            self.notify(f"Network error syncing entries: {e}", severity="error")
        except Exception as e:
            self.notify(f"Error syncing entries: {e}", severity="error")

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

    def action_clear_filters(self) -> None:
        """Clear all active filters and show all entries.

        Clears category, search, unread, and starred filters.
        """
        self.filter_category_id = None
        self.filter_unread_only = False
        self.filter_starred_only = False
        self.search_active = False
        self.search_term = ""
        self._populate_list()
        self.notify("All filters cleared")

    def set_category_filter(self, category_id: int | None) -> None:
        """Set category filter to show entries from a specific category.

        Args:
            category_id: ID of the category to filter by, or None to show all entries
        """
        self.filter_category_id = category_id
        self.filter_unread_only = False
        self.filter_starred_only = False
        self.search_active = False
        self.search_term = ""
        self._populate_list()

        # Find category name for notification
        category_name = "All entries"
        if category_id is not None:
            for cat in self.categories:
                if cat.id == category_id:
                    category_name = cat.title
                    break

        self.notify(f"Filtered to: {category_name}")

    def action_search(self):
        """Clear current search filter.

        Toggles search mode off and refreshes the display to show all entries.
        """
        # Clear any active search
        if self.search_active or self.search_term:
            self.search_active = False
            self.search_term = ""
            self._populate_list()
            self.notify("Search cleared")
        else:
            # Notify that search feature is available
            self.notify("Search: Use set_search_term() method to filter entries")

    def set_search_term(self, search_term: str) -> None:
        """Set search term and filter entries.

        Args:
            search_term: The search term to filter entries by (title or content)
        """
        self.search_term = search_term.strip()
        self.search_active = bool(self.search_term)
        self._populate_list()

        # Notify user of search results
        if self.search_active:
            result_count = len(self._filter_entries(self.entries))
            self.notify(f"Search: {result_count} entries match '{self.search_term}'")

    async def action_manage_categories(self) -> None:
        """Open the category management screen."""
        await self.app.push_category_management_screen()

    def action_show_help(self):
        """Show keyboard help."""
        self.app.push_screen("help")

    def action_show_status(self):
        """Show system status and feed health."""
        self.app.push_screen("status")

    def action_show_settings(self):
        """Show user settings and integrations."""
        self.app.push_screen("settings")

    def action_show_history(self):
        """Show reading history."""
        self.app.log("action_show_history called - pushing history screen")
        try:
            self.app.push_screen("history")
            self.app.log("Successfully pushed history screen")
        except Exception as e:
            self.app.log(f"Error pushing history screen: {type(e).__name__}: {e}")
            self.app.notify(f"Failed to show history: {e}", severity="error")

    async def action_scraping_helper(self) -> None:
        """Open scraping helper for selected entry."""
        # Import here to avoid circular dependency
        from miniflux_tui.ui.screens.scraping_helper import (  # noqa: PLC0415
            ScrapingHelperScreen,
        )

        # Get the currently selected item
        if not self.list_view or not self.list_view.highlighted_child:
            self.notify("No entry selected", severity="warning")
            return

        # Get entry from selected item
        selected_item = self.list_view.highlighted_child
        if not isinstance(selected_item, EntryListItem):
            self.notify("Please select an entry first", severity="warning")
            return

        entry = selected_item.entry

        # Create callback for saving scraper rules
        async def save_scraper_rule(feed_id: int, selector: str) -> None:
            """Save scraper rule to feed settings."""
            if not self.app.client:
                msg = "API client not available"
                raise RuntimeError(msg)

            # Update feed with scraper rules
            await self.app.client.update_feed(
                feed_id,
                scraper_rules=selector,
            )

            self.notify(
                f"Scraper rule saved for feed: {entry.feed.title}",
                severity="information",
            )

        # Push scraping helper screen
        screen = ScrapingHelperScreen(
            entry_url=entry.url,
            feed_id=entry.feed_id,
            feed_title=entry.feed.title,
            on_save_callback=save_scraper_rule,
        )

        self.app.push_screen(screen)

    def action_quit(self):
        """Quit the application."""
        self.app.exit()
