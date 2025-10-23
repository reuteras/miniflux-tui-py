"""Entry list screen with feed sorting capabilities."""

from typing import List, Optional
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, ListItem, ListView
from textual.binding import Binding

from ...api.models import Entry


class EntryListItem(ListItem):
    """Custom list item for displaying a feed entry."""

    def __init__(self, entry: Entry, unread_color: str = "cyan", read_color: str = "gray"):
        super().__init__()
        self.entry = entry
        self.unread_color = unread_color
        self.read_color = read_color

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        # Format the entry display
        status_icon = "●" if self.entry.is_unread else "○"
        star_icon = "★" if self.entry.starred else "☆"

        # Determine color based on read status
        color = self.unread_color if self.entry.is_unread else self.read_color

        # Format: [status] [star] Feed Name | Entry Title
        label = f"[{color}]{status_icon} {star_icon} {self.entry.feed.title} | {self.entry.title}[/{color}]"

        yield Static(label)


class EntryListScreen(Screen):
    """Screen for displaying a list of feed entries with sorting."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "select_entry", "Open Entry"),
        Binding("m", "toggle_read", "Mark Read/Unread"),
        Binding("asterisk", "toggle_star", "Toggle Star"),
        Binding("s", "cycle_sort", "Cycle Sort"),
        Binding("g", "toggle_group", "Group by Feed"),
        Binding("r", "refresh", "Refresh"),
        Binding("u", "show_unread", "Unread"),
        Binding("t", "show_starred", "Starred"),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        entries: List[Entry],
        unread_color: str = "cyan",
        read_color: str = "gray",
        default_sort: str = "date",
        group_by_feed: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entries = entries
        self.unread_color = unread_color
        self.read_color = read_color
        self.current_sort = default_sort
        self.group_by_feed = group_by_feed
        self.list_view: Optional[ListView] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        # Create the list view
        self.list_view = ListView()
        yield self.list_view
        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Populate the list after the widgets are mounted
        self._populate_list()

    def _populate_list(self):
        """Populate the list with sorted entries."""
        if not self.list_view:
            return

        # Clear existing items
        self.list_view.clear()

        # Sort entries
        sorted_entries = self._sort_entries(self.entries)

        # Add entries to list
        if self.group_by_feed:
            self._add_grouped_entries(sorted_entries)
        else:
            self._add_flat_entries(sorted_entries)

    def _sort_entries(self, entries: List[Entry]) -> List[Entry]:
        """Sort entries based on current sort mode."""
        if self.current_sort == "feed":
            # Sort by feed name, then by date
            return sorted(
                entries,
                key=lambda e: (e.feed.title.lower(), e.published_at),
                reverse=True,
            )
        elif self.current_sort == "date":
            # Sort by published date
            return sorted(entries, key=lambda e: e.published_at, reverse=True)
        elif self.current_sort == "status":
            # Sort by status (unread first), then by date
            return sorted(
                entries,
                key=lambda e: (e.is_read, e.published_at),
                reverse=False,
            )
        else:
            return entries

    def _add_flat_entries(self, entries: List[Entry]):
        """Add entries as a flat list."""
        for entry in entries:
            item = EntryListItem(entry, self.unread_color, self.read_color)
            self.list_view.append(item)

    def _add_grouped_entries(self, entries: List[Entry]):
        """Add entries grouped by feed."""
        current_feed = None

        for entry in entries:
            # Add feed header if this is a new feed
            if current_feed != entry.feed.title:
                current_feed = entry.feed.title
                # Add a header item
                header = ListItem()
                header_static = Static(f"[bold cyan]━━ {current_feed} ━━[/bold cyan]")
                header.mount(header_static)
                self.list_view.append(header)

            # Add the entry
            item = EntryListItem(entry, self.unread_color, self.read_color)
            self.list_view.append(item)

    def action_cursor_down(self):
        """Move cursor down."""
        if self.list_view:
            self.list_view.action_cursor_down()

    def action_cursor_up(self):
        """Move cursor up."""
        if self.list_view:
            self.list_view.action_cursor_up()

    def action_select_entry(self):
        """Select and open the current entry."""
        if not self.list_view or self.list_view.index is None:
            return

        item = self.list_view.children[self.list_view.index]
        if isinstance(item, EntryListItem):
            # Open entry reader screen
            from ..app import MinifluxTUI
            if isinstance(self.app, MinifluxTUI):
                self.app.push_entry_reader(item.entry)

    def action_toggle_read(self):
        """Toggle read/unread status of current entry."""
        if not self.list_view or self.list_view.index is None:
            return

        item = self.list_view.children[self.list_view.index]
        if isinstance(item, EntryListItem):
            # Toggle the status
            new_status = "read" if item.entry.is_unread else "unread"
            item.entry.status = new_status
            # TODO: Call API to update status
            # Refresh display
            self._populate_list()

    def action_toggle_star(self):
        """Toggle star status of current entry."""
        if not self.list_view or self.list_view.index is None:
            return

        item = self.list_view.children[self.list_view.index]
        if isinstance(item, EntryListItem):
            # Toggle the star
            item.entry.starred = not item.entry.starred
            # TODO: Call API to update star status
            # Refresh display
            self._populate_list()

    def action_cycle_sort(self):
        """Cycle through sort modes."""
        sort_modes = ["date", "feed", "status"]
        current_index = sort_modes.index(self.current_sort)
        self.current_sort = sort_modes[(current_index + 1) % len(sort_modes)]

        # Update title to show current sort
        self.sub_title = f"Sort: {self.current_sort.title()}"

        # Re-populate list
        self._populate_list()

    def action_toggle_group(self):
        """Toggle grouping by feed."""
        self.group_by_feed = not self.group_by_feed
        self._populate_list()

    def action_refresh(self):
        """Refresh the entry list."""
        # TODO: Call API to refresh entries
        self.notify("Refreshing entries...")

    def action_show_unread(self):
        """Show only unread entries."""
        # TODO: Filter to show only unread
        pass

    def action_show_starred(self):
        """Show only starred entries."""
        # TODO: Filter to show only starred
        pass

    def action_show_help(self):
        """Show keyboard help."""
        # TODO: Push help screen
        self.app.push_screen("help")

    def action_quit(self):
        """Quit the application."""
        self.app.exit()
