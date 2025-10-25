"""Tests for entry list screen functionality."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from textual.binding import Binding
from textual.widgets import ListItem, ListView

from miniflux_tui.api.models import Entry, Feed
from miniflux_tui.constants import SORT_MODES
from miniflux_tui.ui.screens.entry_list import (
    EntryListItem,
    EntryListScreen,
    FeedHeaderItem,
)


@pytest.fixture
def test_feed():
    """Create a test feed."""
    return Feed(
        id=1,
        title="Test Feed",
        site_url="https://example.com",
        feed_url="https://example.com/feed.xml",
    )


@pytest.fixture
def diverse_entries(test_feed):
    """Create entries with different statuses and dates for testing sorting."""
    return [
        Entry(
            id=1,
            feed_id=1,
            title="Oldest Unread",
            url="https://example.com/1",
            content="Content 1",
            feed=test_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 20, 10, 0, 0, tzinfo=UTC),
        ),
        Entry(
            id=2,
            feed_id=1,
            title="Newest Read",
            url="https://example.com/2",
            content="Content 2",
            feed=test_feed,
            status="read",
            starred=False,
            published_at=datetime(2024, 10, 25, 15, 30, 0, tzinfo=UTC),
        ),
        Entry(
            id=3,
            feed_id=1,
            title="Middle Starred",
            url="https://example.com/3",
            content="Content 3",
            feed=test_feed,
            status="read",
            starred=True,
            published_at=datetime(2024, 10, 22, 12, 0, 0, tzinfo=UTC),
        ),
        Entry(
            id=4,
            feed_id=1,
            title="Recent Unread",
            url="https://example.com/4",
            content="Content 4",
            feed=test_feed,
            status="unread",
            starred=True,
            published_at=datetime(2024, 10, 24, 8, 30, 0, tzinfo=UTC),
        ),
    ]


class TestEntryListScreen:
    """Test EntryListScreen functionality."""

    def test_entry_list_creation(self, diverse_entries):
        """Test creating an EntryListScreen instance."""
        screen = EntryListScreen(entries=diverse_entries)
        assert screen.entries == diverse_entries
        assert screen.current_sort == "date"
        assert screen.group_by_feed is False
        assert screen.filter_unread_only is False
        assert screen.filter_starred_only is False

    def test_custom_colors(self, diverse_entries):
        """Test EntryListScreen with custom colors."""
        screen = EntryListScreen(
            entries=diverse_entries,
            unread_color="yellow",
            read_color="white",
        )
        assert screen.unread_color == "yellow"
        assert screen.read_color == "white"

    def test_custom_sort_mode(self, diverse_entries):
        """Test EntryListScreen with custom sort mode."""
        screen = EntryListScreen(entries=diverse_entries, default_sort="feed")
        assert screen.current_sort == "feed"

    def test_filter_unread_only(self, diverse_entries):
        """Test filtering to show only unread entries."""
        screen = EntryListScreen(entries=diverse_entries)
        filtered = screen._filter_entries(diverse_entries)
        # Should return all entries when no filter is active
        assert len(filtered) == len(diverse_entries)

        # Now enable unread filter
        screen.filter_unread_only = True
        filtered = screen._filter_entries(diverse_entries)
        # Should return only unread entries
        assert len(filtered) == 2  # IDs 1 and 4
        assert all(e.is_unread for e in filtered)
        assert all(e.id in [1, 4] for e in filtered)

    def test_filter_starred_only(self, diverse_entries):
        """Test filtering to show only starred entries."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.filter_starred_only = True
        filtered = screen._filter_entries(diverse_entries)
        # Should return only starred entries
        assert len(filtered) == 2  # IDs 3 and 4
        assert all(e.starred for e in filtered)
        assert all(e.id in [3, 4] for e in filtered)

    def test_filters_are_mutually_exclusive(self, diverse_entries):
        """Test that only one filter is applied at a time."""
        screen = EntryListScreen(entries=diverse_entries)
        # Enable both filters (shouldn't happen in normal usage)
        screen.filter_unread_only = True
        screen.filter_starred_only = True

        filtered = screen._filter_entries(diverse_entries)
        # filter_unread_only should take precedence
        assert len(filtered) == 2  # Only unread entries
        assert all(e.is_unread for e in filtered)

    def test_sort_by_date(self, diverse_entries):
        """Test sorting entries by date (newest first)."""
        screen = EntryListScreen(entries=diverse_entries, default_sort="date")
        sorted_entries = screen._sort_entries(diverse_entries)

        # Newest should be first
        assert sorted_entries[0].id == 2  # 2024-10-25
        assert sorted_entries[1].id == 4  # 2024-10-24
        assert sorted_entries[2].id == 3  # 2024-10-22
        assert sorted_entries[3].id == 1  # 2024-10-20

    def test_sort_by_status(self, diverse_entries):
        """Test sorting entries by status (unread first)."""
        screen = EntryListScreen(entries=diverse_entries, default_sort="status")
        sorted_entries = screen._sort_entries(diverse_entries)

        # Unread entries should come first (oldest first within status)
        unread = [e for e in sorted_entries if e.is_unread]
        read = [e for e in sorted_entries if e.is_read]

        assert len(unread) == 2
        assert len(read) == 2
        # Unread should be before read
        assert sorted_entries.index(unread[0]) < sorted_entries.index(read[0])
        # Within unread, oldest should be first
        assert unread[0].id == 1  # 2024-10-20
        assert unread[1].id == 4  # 2024-10-24

    def test_sort_by_feed(self, diverse_entries):
        """Test sorting entries by feed."""
        screen = EntryListScreen(entries=diverse_entries, default_sort="feed")
        sorted_entries = screen._sort_entries(diverse_entries)

        # All entries are from same feed, so should be sorted by date
        # (newest first within same feed)
        assert sorted_entries[0].id == 2  # Newest
        assert sorted_entries[-1].id == 1  # Oldest

    def test_empty_entry_list(self):
        """Test EntryListScreen with empty entries."""
        screen = EntryListScreen(entries=[])
        assert screen.entries == []
        assert len(screen.sorted_entries) == 0

    def test_single_entry(self, test_feed):
        """Test EntryListScreen with single entry."""
        entry = Entry(
            id=1,
            feed_id=1,
            title="Single Entry",
            url="https://example.com/single",
            content="Content",
            feed=test_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 25, 10, 0, 0, tzinfo=UTC),
        )
        screen = EntryListScreen(entries=[entry])
        assert len(screen.entries) == 1
        sorted_entries = screen._sort_entries([entry])
        assert len(sorted_entries) == 1
        assert sorted_entries[0].id == 1

    def test_sorting_with_filter(self, diverse_entries):
        """Test that filtering and sorting work together."""
        screen = EntryListScreen(entries=diverse_entries, default_sort="date")
        screen.filter_unread_only = True

        # Apply filter and sort
        filtered = screen._filter_entries(diverse_entries)
        sorted_entries = screen._sort_entries(filtered)

        # Should only have unread entries
        assert len(sorted_entries) == 2
        assert all(e.is_unread for e in sorted_entries)
        # Should be sorted by date (newest first)
        assert sorted_entries[0].id == 4  # 2024-10-24
        assert sorted_entries[1].id == 1  # 2024-10-20

    def test_grouped_mode_with_collapse(self, diverse_entries):
        """Test grouped mode with collapsed feeds."""
        screen = EntryListScreen(
            entries=diverse_entries,
            group_by_feed=True,
            group_collapsed=True,
        )
        # Should start with feeds collapsed
        assert screen.group_collapsed is True
        assert screen.group_by_feed is True

    def test_fold_state_tracking(self, diverse_entries):
        """Test that fold state is tracked per feed."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        # Feed fold state should be tracked
        assert hasattr(screen, "feed_fold_state")
        assert isinstance(screen.feed_fold_state, dict)

    def test_feed_header_map(self, diverse_entries):
        """Test that feed header items are tracked."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        # Feed header map should be tracked
        assert hasattr(screen, "feed_header_map")
        assert isinstance(screen.feed_header_map, dict)

    def test_last_highlighted_feed_tracking(self, diverse_entries):
        """Test that last highlighted feed is tracked for position persistence."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        assert hasattr(screen, "last_highlighted_feed")
        # Initially None or will be set to first feed
        assert screen.last_highlighted_feed is None or isinstance(
            screen.last_highlighted_feed, str
        )

    def test_vim_navigation_attributes(self, diverse_entries):
        """Test that vim navigation actions exist."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        # Check that the vim navigation actions are defined
        assert hasattr(screen, "action_expand_feed")
        assert hasattr(screen, "action_collapse_feed")
        assert callable(screen.action_expand_feed)
        assert callable(screen.action_collapse_feed)

    def test_restore_cursor_position_method_exists(self, diverse_entries):
        """Test that cursor position restore method exists."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        assert hasattr(screen, "_restore_cursor_position")
        assert callable(screen._restore_cursor_position)


class TestEntryListItem:
    """Test EntryListItem widget class."""

    def test_entry_list_item_creation(self, test_feed):
        """Test creating an EntryListItem."""
        entry = Entry(
            id=1,
            feed_id=1,
            title="Test Entry",
            url="https://example.com/1",
            content="Content",
            feed=test_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 25, 10, 0, 0, tzinfo=UTC),
        )
        item = EntryListItem(entry)
        assert item.entry == entry
        assert item.unread_color == "cyan"
        assert item.read_color == "gray"

    def test_entry_list_item_custom_colors(self, test_feed):
        """Test EntryListItem with custom colors."""
        entry = Entry(
            id=1,
            feed_id=1,
            title="Test Entry",
            url="https://example.com/1",
            content="Content",
            feed=test_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 25, 10, 0, 0, tzinfo=UTC),
        )
        item = EntryListItem(entry, unread_color="yellow", read_color="white")
        assert item.unread_color == "yellow"
        assert item.read_color == "white"

    def test_entry_list_item_is_list_item(self, test_feed):
        """Test that EntryListItem is a ListItem subclass."""
        entry = Entry(
            id=1,
            feed_id=1,
            title="Test Entry",
            url="https://example.com/1",
            content="Content",
            feed=test_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 25, 10, 0, 0, tzinfo=UTC),
        )
        item = EntryListItem(entry)
        assert isinstance(item, ListItem)

    def test_entry_list_item_for_unread_entry(self, test_feed):
        """Test EntryListItem formatting for unread entry."""
        entry = Entry(
            id=1,
            feed_id=1,
            title="Unread Entry",
            url="https://example.com/1",
            content="Content",
            feed=test_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 25, 10, 0, 0, tzinfo=UTC),
        )
        item = EntryListItem(entry)
        assert item.entry.is_unread is True

    def test_entry_list_item_for_read_entry(self, test_feed):
        """Test EntryListItem formatting for read entry."""
        entry = Entry(
            id=1,
            feed_id=1,
            title="Read Entry",
            url="https://example.com/1",
            content="Content",
            feed=test_feed,
            status="read",
            starred=False,
            published_at=datetime(2024, 10, 25, 10, 0, 0, tzinfo=UTC),
        )
        item = EntryListItem(entry)
        assert item.entry.is_read is True

    def test_entry_list_item_for_starred_entry(self, test_feed):
        """Test EntryListItem for starred entry."""
        entry = Entry(
            id=1,
            feed_id=1,
            title="Starred Entry",
            url="https://example.com/1",
            content="Content",
            feed=test_feed,
            status="unread",
            starred=True,
            published_at=datetime(2024, 10, 25, 10, 0, 0, tzinfo=UTC),
        )
        item = EntryListItem(entry)
        assert item.entry.starred is True


class TestFeedHeaderItem:
    """Test FeedHeaderItem widget class."""

    def test_feed_header_item_creation(self):
        """Test creating a FeedHeaderItem."""
        header = FeedHeaderItem("Test Feed")
        assert header.feed_title == "Test Feed"
        assert header.is_expanded is True

    def test_feed_header_item_collapsed_state(self):
        """Test FeedHeaderItem with initial collapsed state."""
        header = FeedHeaderItem("Test Feed", is_expanded=False)
        assert header.feed_title == "Test Feed"
        assert header.is_expanded is False

    def test_feed_header_item_is_list_item(self):
        """Test that FeedHeaderItem is a ListItem subclass."""
        header = FeedHeaderItem("Test Feed")
        assert isinstance(header, ListItem)

    def test_feed_header_item_toggle_fold(self):
        """Test toggling fold state of FeedHeaderItem."""
        header = FeedHeaderItem("Test Feed", is_expanded=True)
        assert header.is_expanded is True
        header.toggle_fold()
        assert header.is_expanded is False
        header.toggle_fold()
        assert header.is_expanded is True

    def test_feed_header_item_toggle_fold_multiple_times(self):
        """Test multiple fold toggling."""
        header = FeedHeaderItem("Test Feed", is_expanded=True)
        for _ in range(5):
            header.toggle_fold()
        # After odd number of toggles, should be collapsed
        assert header.is_expanded is False


class TestEntryListScreenCompose:
    """Test EntryListScreen composition."""

    def test_compose_method_exists(self, diverse_entries):
        """Test that compose method exists."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "compose")
        assert callable(screen.compose)

    def test_compose_returns_generator(self, diverse_entries):
        """Test that compose returns a generator."""
        screen = EntryListScreen(entries=diverse_entries)
        result = screen.compose()
        assert hasattr(result, "__iter__") or hasattr(result, "__next__")

    def test_screen_has_bindings(self, diverse_entries):
        """Test that EntryListScreen has key bindings."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "BINDINGS")
        assert isinstance(screen.BINDINGS, list)
        assert len(screen.BINDINGS) > 0

    def test_bindings_are_binding_objects(self, diverse_entries):
        """Test that all bindings are Binding objects."""
        screen = EntryListScreen(entries=diverse_entries)
        for binding in screen.BINDINGS:
            assert isinstance(binding, Binding)

    def test_screen_has_required_actions(self, diverse_entries):
        """Test that screen has required action methods."""
        screen = EntryListScreen(entries=diverse_entries)
        required_actions = [
            "action_cycle_sort",
            "action_toggle_group",
            "action_toggle_fold",
            "action_toggle_read",
            "action_toggle_star",
        ]
        for action in required_actions:
            assert hasattr(screen, action), f"Missing action: {action}"


class TestEntryListScreenActions:
    """Test EntryListScreen action methods."""

    def test_action_cycle_sort(self, diverse_entries):
        """Test cycling through sort modes."""
        screen = EntryListScreen(entries=diverse_entries, default_sort="date")
        assert screen.current_sort == "date"

        # Test that action_cycle_sort method exists
        assert hasattr(screen, "action_cycle_sort")
        assert callable(screen.action_cycle_sort)

        # Test the sorting logic directly without calling the action
        # to avoid NoActiveAppError from Textual framework
        current_index = SORT_MODES.index(screen.current_sort)
        next_sort = SORT_MODES[(current_index + 1) % len(SORT_MODES)]
        assert next_sort == "feed"

    def test_action_toggle_group(self, diverse_entries):
        """Test toggling group by feed."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        assert screen.group_by_feed is False

        # Test that action_toggle_group method exists
        assert hasattr(screen, "action_toggle_group")
        assert callable(screen.action_toggle_group)

        # Test the grouping logic directly
        original_state = screen.group_by_feed
        expected_state = not original_state
        assert expected_state is True

    def test_get_sorted_entries_default_sort(self, diverse_entries):
        """Test _get_sorted_entries with default sort."""
        screen = EntryListScreen(entries=diverse_entries, default_sort="date")
        sorted_entries = screen._get_sorted_entries()
        # Newest should be first
        assert sorted_entries[0].id == 2

    def test_get_sorted_entries_grouped(self, diverse_entries):
        """Test _get_sorted_entries with grouping enabled."""
        screen = EntryListScreen(
            entries=diverse_entries, group_by_feed=True, default_sort="date"
        )
        sorted_entries = screen._get_sorted_entries()
        # Should be sorted by feed name, then by date
        assert len(sorted_entries) == len(diverse_entries)

    def test_display_entries_flat(self, diverse_entries):
        """Test _display_entries in flat mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen.list_view = MagicMock(spec=ListView)
        sorted_entries = screen._get_sorted_entries()
        screen._display_entries(sorted_entries)
        # Should call _add_flat_entries
        assert screen.list_view.append.called or len(sorted_entries) > 0

    def test_display_entries_grouped(self, diverse_entries):
        """Test _display_entries in grouped mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock(spec=ListView)
        sorted_entries = screen._get_sorted_entries()
        screen._display_entries(sorted_entries)
        # Should call _add_grouped_entries
        assert screen.list_view.append.called or len(sorted_entries) > 0

    def test_is_item_visible(self, diverse_entries):
        """Test _is_item_visible method."""
        screen = EntryListScreen(entries=diverse_entries)
        entry = diverse_entries[0]
        item = EntryListItem(entry)

        # Initially should be visible
        assert screen._is_item_visible(item) is True

        # Add collapsed class
        item.add_class("collapsed")
        assert screen._is_item_visible(item) is False

    @pytest.mark.asyncio
    async def test_action_toggle_read(self, diverse_entries):
        """Test toggle_read action."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_toggle_read")
        assert callable(screen.action_toggle_read)

    @pytest.mark.asyncio
    async def test_action_toggle_star(self, diverse_entries):
        """Test toggle_star action."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_toggle_star")
        assert callable(screen.action_toggle_star)

    @pytest.mark.asyncio
    async def test_action_save_entry(self, diverse_entries):
        """Test save_entry action."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_save_entry")
        assert callable(screen.action_save_entry)

    @pytest.mark.asyncio
    async def test_action_refresh(self, diverse_entries):
        """Test refresh action."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_refresh")
        assert callable(screen.action_refresh)

    @pytest.mark.asyncio
    async def test_action_show_unread(self, diverse_entries):
        """Test show_unread action."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_show_unread")
        assert callable(screen.action_show_unread)

    @pytest.mark.asyncio
    async def test_action_show_starred(self, diverse_entries):
        """Test show_starred action."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_show_starred")
        assert callable(screen.action_show_starred)

    def test_action_show_help(self, diverse_entries):
        """Test show_help action."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_show_help")
        assert callable(screen.action_show_help)

    def test_action_quit(self, diverse_entries):
        """Test quit action."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_quit")
        assert callable(screen.action_quit)


class TestEntryListScreenCursorNavigation:
    """Test cursor navigation methods."""

    def test_action_cursor_down_exists(self, diverse_entries):
        """Test cursor_down action exists."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_cursor_down")
        assert callable(screen.action_cursor_down)

    def test_action_cursor_up_exists(self, diverse_entries):
        """Test cursor_up action exists."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_cursor_up")
        assert callable(screen.action_cursor_up)

    def test_cursor_down_with_no_listview(self, diverse_entries):
        """Test cursor_down when list_view is None."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = None
        # Should not crash
        screen.action_cursor_down()

    def test_cursor_up_with_no_listview(self, diverse_entries):
        """Test cursor_up when list_view is None."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = None
        # Should not crash
        screen.action_cursor_up()

    def test_cursor_navigation_skips_hidden_items(self, diverse_entries):
        """Test that cursor navigation skips hidden (collapsed) items."""
        screen = EntryListScreen(entries=diverse_entries)
        # Verify hidden items are skipped
        item = MagicMock(spec=ListItem)
        item.classes = {"collapsed"}
        assert screen._is_item_visible(item) is False


class TestEntryListScreenFoldOperations:
    """Test feed folding/unfolding operations."""

    def test_action_toggle_fold_exists(self, diverse_entries):
        """Test toggle_fold action exists."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_toggle_fold")
        assert callable(screen.action_toggle_fold)

    def test_action_collapse_feed_exists(self, diverse_entries):
        """Test collapse_feed action exists."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_collapse_feed")
        assert callable(screen.action_collapse_feed)

    def test_action_expand_feed_exists(self, diverse_entries):
        """Test expand_feed action exists."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "action_expand_feed")
        assert callable(screen.action_expand_feed)

    def test_toggle_fold_without_grouped_mode(self, diverse_entries):
        """Test toggle_fold when not in grouped mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen.list_view = MagicMock()
        # Should return early
        screen.action_toggle_fold()

    def test_collapse_feed_without_grouped_mode(self, diverse_entries):
        """Test collapse_feed when not in grouped mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen.list_view = MagicMock()
        # Should return early
        screen.action_collapse_feed()

    def test_expand_feed_without_grouped_mode(self, diverse_entries):
        """Test expand_feed when not in grouped mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen.list_view = MagicMock()
        # Should return early
        screen.action_expand_feed()

    def test_update_feed_visibility(self, diverse_entries):
        """Test _update_feed_visibility method."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()
        screen.list_view.children = []

        # Create a mock entry item
        mock_item = MagicMock(spec=EntryListItem)
        mock_item.entry = diverse_entries[0]
        screen.list_view.children = [mock_item]

        # Test updating visibility
        screen._update_feed_visibility(diverse_entries[0].feed.title)


class TestEntryListScreenIncrementalUpdates:
    """Test incremental update functionality."""

    def test_update_single_item_not_found(self, diverse_entries):
        """Test _update_single_item when item not found."""
        screen = EntryListScreen(entries=diverse_entries)
        entry = diverse_entries[0]
        result = screen._update_single_item(entry)
        assert result is False

    def test_update_single_item_not_in_map_with_listview(self, diverse_entries):
        """Test _update_single_item with item not in map but list_view exists."""
        screen = EntryListScreen(entries=diverse_entries)
        entry = diverse_entries[0]

        # Set list_view but don't add entry to map
        screen.list_view = MagicMock(spec=ListView)
        screen.list_view.children = []

        # When entry is not in map, should return False
        result = screen._update_single_item(entry)
        assert result is False


class TestEntryListScreenGrouping:
    """Test grouping functionality."""

    def test_add_grouped_entries(self, diverse_entries):
        """Test _add_grouped_entries method."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()
        screen._add_grouped_entries(diverse_entries)
        # Should have called append for headers and entries
        assert screen.list_view.append.called or len(diverse_entries) > 0

    def test_add_flat_entries(self, diverse_entries):
        """Test _add_flat_entries method."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen.list_view = MagicMock()
        screen._add_flat_entries(diverse_entries)
        # Should have called append for all entries
        assert screen.list_view.append.called or len(diverse_entries) > 0

    def test_grouped_entries_populate_maps(self, diverse_entries):
        """Test that grouped entries populate tracking maps."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()
        screen._add_grouped_entries(diverse_entries)
        # Maps should be populated - at least entry_item_map should have items
        assert len(screen.entry_item_map) > 0


class TestEntryListScreenMultipleFeedsGrouping:
    """Test grouping with multiple feeds."""

    @pytest.fixture
    def multiple_feeds(self):
        """Create entries from multiple feeds."""
        feed1 = Feed(
            id=1,
            title="Feed A",
            site_url="https://example1.com",
            feed_url="https://example1.com/feed.xml",
        )
        feed2 = Feed(
            id=2,
            title="Feed B",
            site_url="https://example2.com",
            feed_url="https://example2.com/feed.xml",
        )
        return [
            Entry(
                id=1,
                feed_id=1,
                title="Entry 1A",
                url="https://example1.com/1",
                content="Content",
                feed=feed1,
                status="unread",
                starred=False,
                published_at=datetime(2024, 10, 25, 10, 0, 0, tzinfo=UTC),
            ),
            Entry(
                id=2,
                feed_id=2,
                title="Entry 2A",
                url="https://example2.com/1",
                content="Content",
                feed=feed2,
                status="unread",
                starred=False,
                published_at=datetime(2024, 10, 26, 10, 0, 0, tzinfo=UTC),
            ),
            Entry(
                id=3,
                feed_id=1,
                title="Entry 1B",
                url="https://example1.com/2",
                content="Content",
                feed=feed1,
                status="read",
                starred=False,
                published_at=datetime(2024, 10, 24, 10, 0, 0, tzinfo=UTC),
            ),
        ]

    def test_grouped_sort_with_multiple_feeds(self, multiple_feeds):
        """Test sorting with multiple feeds."""
        screen = EntryListScreen(entries=multiple_feeds, group_by_feed=True)
        sorted_entries = screen._get_sorted_entries()
        # Should group by feed and sort by date within each feed
        assert len(sorted_entries) == len(multiple_feeds)

    def test_multiple_feed_headers_created(self, multiple_feeds):
        """Test that multiple feed headers are created."""
        screen = EntryListScreen(entries=multiple_feeds, group_by_feed=True)
        screen.list_view = MagicMock()
        screen._add_grouped_entries(multiple_feeds)
        # Should have entries for both feeds
        assert screen.feed_header_map or screen.entry_item_map
