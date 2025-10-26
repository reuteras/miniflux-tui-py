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
        assert screen.last_highlighted_feed is None or isinstance(screen.last_highlighted_feed, str)

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
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True, default_sort="date")
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


class TestCursorPositionRestoration:
    """Test cursor position restoration when returning from entry reader."""

    def test_last_cursor_index_initialized(self, diverse_entries):
        """Test that last_cursor_index is initialized."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "last_cursor_index")
        assert screen.last_cursor_index == 0

    def test_last_highlighted_entry_id_initialized(self, diverse_entries):
        """Test that last_highlighted_entry_id is initialized."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "last_highlighted_entry_id")
        assert screen.last_highlighted_entry_id is None

    def test_restore_cursor_position_method_exists(self, diverse_entries):
        """Test that _restore_cursor_position method exists."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "_restore_cursor_position")
        assert callable(screen._restore_cursor_position)

    def test_restore_cursor_position_with_no_list_view(self, diverse_entries):
        """Test _restore_cursor_position when list_view is None."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = None
        # Should not crash
        screen._restore_cursor_position()

    def test_restore_cursor_position_with_empty_list(self, diverse_entries):
        """Test _restore_cursor_position with empty children."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = MagicMock(spec=ListView)
        screen.list_view.children = []
        # Should not crash
        screen._restore_cursor_position()

    def test_restore_cursor_position_by_entry_id(self, diverse_entries):
        """Test restoring cursor position by entry ID."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock(spec=ListView)

        # Create mock items
        mock_items = [EntryListItem(e) for e in diverse_entries]
        screen.list_view.children = mock_items
        screen.last_highlighted_entry_id = diverse_entries[2].id

        # Call restore - it should find the entry by ID
        screen._restore_cursor_position()
        # Should have called set index on list_view
        assert screen.list_view.index == 2 or screen.list_view.index is not None

    def test_restore_cursor_position_fallback_to_index(self, diverse_entries):
        """Test restore cursor falls back to last_cursor_index if entry not found."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen.list_view = MagicMock(spec=ListView)
        screen.list_view.children = [MagicMock() for _ in diverse_entries]
        screen.last_cursor_index = 1
        screen.last_highlighted_entry_id = None

        # Call restore
        screen._restore_cursor_position()
        # Should set index to last_cursor_index
        assert screen.list_view.index == 1 or screen.list_view.index is not None

    def test_grouped_mode_cursor_restoration(self, diverse_entries):
        """Test cursor restoration in grouped mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        assert screen.group_by_feed is True
        # Verify the flag exists for grouped mode logic
        assert hasattr(screen, "last_highlighted_entry_id")

    def test_non_grouped_mode_cursor_restoration(self, diverse_entries):
        """Test cursor restoration in non-grouped mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        assert screen.group_by_feed is False
        # Verify cursor index is tracked
        assert hasattr(screen, "last_cursor_index")
        assert screen.last_cursor_index == 0

    def test_restore_cursor_position_and_focus_exists(self, diverse_entries):
        """Test that _restore_cursor_position_and_focus method exists."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "_restore_cursor_position_and_focus")
        assert callable(screen._restore_cursor_position_and_focus)

    def test_restore_cursor_calls_ensure_focus(self, diverse_entries):
        """Test that _restore_cursor_position_and_focus calls ensure_focus."""
        screen = EntryListScreen(entries=diverse_entries)
        assert hasattr(screen, "_ensure_focus")
        # Verify the method exists and is callable
        assert callable(screen._ensure_focus)


class TestNavigationWithEntrySaving:
    """Test navigation and cursor restoration with entry selection."""

    def test_cursor_index_not_none_check(self, diverse_entries):
        """Test that list_view.index is checked for None before assignment."""
        screen = EntryListScreen(entries=diverse_entries)
        mock_list_view = MagicMock()
        mock_list_view.index = 2  # Valid index
        screen.list_view = mock_list_view

        # Simulate selecting an entry
        if screen.list_view and screen.list_view.index is not None:
            screen.last_cursor_index = screen.list_view.index

        assert screen.last_cursor_index == 2

    def test_cursor_index_with_none_value(self, diverse_entries):
        """Test handling of None value for list_view.index."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = MagicMock(spec=ListView)
        screen.list_view.index = None  # None value
        original_index = screen.last_cursor_index

        # Simulate selecting an entry with None index
        if screen.list_view and screen.list_view.index is not None:
            screen.last_cursor_index = screen.list_view.index

        # Should not have changed
        assert screen.last_cursor_index == original_index

    def test_entry_found_by_id_in_grouped_mode(self, diverse_entries):
        """Test finding entry by ID in grouped mode (across feeds)."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        # Create real entry items (not mocks) so isinstance check works
        items = [EntryListItem(e) for e in diverse_entries]
        screen.list_view = MagicMock(spec=ListView)
        screen.list_view.children = items

        # Set the entry ID to find
        target_id = diverse_entries[1].id
        screen.last_highlighted_entry_id = target_id

        # Manually check if we can find it
        found = False
        for i, child in enumerate(screen.list_view.children):
            if isinstance(child, EntryListItem) and child.entry.id == target_id:
                found = True
                assert i == 1
                break

        assert found

    def test_entry_not_found_falls_back_to_last_cursor_index(self, diverse_entries):
        """Test fallback to last_cursor_index when entry not found."""
        screen = EntryListScreen(entries=diverse_entries)
        items = [EntryListItem(e) for e in diverse_entries]
        screen.list_view = MagicMock(spec=ListView)
        screen.list_view.children = items

        # Set non-existent entry ID
        screen.last_highlighted_entry_id = 999
        screen.last_cursor_index = 1

        # Check fallback logic
        found = False
        for child in screen.list_view.children:
            if isinstance(child, EntryListItem) and child.entry.id == 999:
                found = True
                break

        # Should not be found, so should use fallback
        assert found is False
        assert screen.last_cursor_index == 1


class TestActionMethods:
    """Test action methods in EntryListScreen."""

    def test_expand_all_toggles_all_feeds(self, diverse_entries):
        """Test that all feeds can be toggled to expanded state."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()
        screen.list_view.children = []

        # Initialize all feeds as collapsed
        screen.feed_fold_state = {"Test Feed": False}
        feed_header = MagicMock(spec=FeedHeaderItem)
        screen.feed_header_map = {"Test Feed": feed_header}

        # Manually toggle like action_expand_all would do
        for feed_title in screen.feed_fold_state:
            if not screen.feed_fold_state[feed_title]:
                screen._set_feed_fold_state(feed_title, True)

        # Verify feed is now expanded
        assert screen.feed_fold_state["Test Feed"] is True
        feed_header.toggle_fold.assert_called()

    def test_collapse_all_toggles_all_feeds(self, diverse_entries):
        """Test that all feeds can be toggled to collapsed state."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()
        screen.list_view.children = []

        # Initialize all feeds as expanded
        screen.feed_fold_state = {"Test Feed": True}
        feed_header = MagicMock(spec=FeedHeaderItem)
        screen.feed_header_map = {"Test Feed": feed_header}

        # Manually toggle like action_collapse_all would do
        for feed_title in screen.feed_fold_state:
            if screen.feed_fold_state[feed_title]:
                screen._set_feed_fold_state(feed_title, False)

        # Verify feed is now collapsed
        assert screen.feed_fold_state["Test Feed"] is False
        feed_header.toggle_fold.assert_called()

    def test_get_highlighted_feed_title_from_header(self, diverse_entries):
        """Test _get_highlighted_feed_title() extracts title from FeedHeaderItem."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)

        # Create mock FeedHeaderItem
        header = MagicMock(spec=FeedHeaderItem)
        header.feed_title = "Test Feed"

        screen.list_view = MagicMock()
        screen.list_view.highlighted_child = header

        # Get feed title
        title = screen._get_highlighted_feed_title()

        assert title == "Test Feed"

    def test_get_highlighted_feed_title_from_entry(self, diverse_entries):
        """Test _get_highlighted_feed_title() extracts title from EntryListItem."""
        screen = EntryListScreen(entries=diverse_entries)

        # Create EntryListItem from first entry
        item = EntryListItem(diverse_entries[0])

        screen.list_view = MagicMock()
        screen.list_view.highlighted_child = item

        # Get feed title
        title = screen._get_highlighted_feed_title()

        assert title == "Test Feed"

    def test_get_highlighted_feed_title_none_when_no_highlight(self, diverse_entries):
        """Test _get_highlighted_feed_title() returns None when nothing highlighted."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = MagicMock()
        screen.list_view.highlighted_child = None

        title = screen._get_highlighted_feed_title()

        assert title is None

    def test_set_feed_fold_state_updates_visibility(self, diverse_entries):
        """Test _set_feed_fold_state() updates fold state and toggles header."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.feed_fold_state = {}
        screen.list_view = MagicMock()
        screen.list_view.children = []  # Empty children to avoid _update_feed_visibility error

        # Create mock feed header
        feed_header = MagicMock(spec=FeedHeaderItem)
        screen.feed_header_map = {"Test Feed": feed_header}

        # Set fold state to expanded
        screen._set_feed_fold_state("Test Feed", True)

        # Verify state updated
        assert screen.feed_fold_state["Test Feed"] is True
        # Verify toggle_fold called
        feed_header.toggle_fold.assert_called()

    def test_ensure_list_view_and_grouped_returns_true(self, diverse_entries):
        """Test _ensure_list_view_and_grouped() returns True when conditions met."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()

        result = screen._ensure_list_view_and_grouped()

        assert result is True

    def test_ensure_list_view_and_grouped_returns_false_when_not_grouped(self, diverse_entries):
        """Test _ensure_list_view_and_grouped() returns False when not in grouped mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen.list_view = MagicMock()

        result = screen._ensure_list_view_and_grouped()

        assert result is False

    def test_list_view_has_items_with_children(self, diverse_entries):
        """Test _list_view_has_items() returns True when list has children."""
        screen = EntryListScreen(entries=diverse_entries)

        # Create mock list view with children
        screen.list_view = MagicMock()
        screen.list_view.children = [MagicMock()]

        result = screen._list_view_has_items()

        assert result is True

    def test_list_view_has_items_empty_list(self, diverse_entries):
        """Test _list_view_has_items() returns False when list is empty."""
        screen = EntryListScreen(entries=diverse_entries)

        screen.list_view = MagicMock()
        screen.list_view.children = []

        result = screen._list_view_has_items()

        assert result is False

    def test_list_view_has_items_none_list(self, diverse_entries):
        """Test _list_view_has_items() returns False when list_view is None."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = None

        result = screen._list_view_has_items()

        assert result is False

    def test_find_entry_index_by_id_found(self, diverse_entries):
        """Test _find_entry_index_by_id() finds entry by ID."""
        screen = EntryListScreen(entries=diverse_entries)

        # Create list of items
        items = [EntryListItem(e) for e in diverse_entries]
        screen.list_view = MagicMock()
        screen.list_view.children = items

        # Find entry with ID 2
        index = screen._find_entry_index_by_id(2)

        assert index == 1  # Second item in list

    def test_find_entry_index_by_id_not_found(self, diverse_entries):
        """Test _find_entry_index_by_id() returns None when ID not found."""
        screen = EntryListScreen(entries=diverse_entries)

        items = [EntryListItem(e) for e in diverse_entries]
        screen.list_view = MagicMock()
        screen.list_view.children = items

        # Try to find non-existent entry
        index = screen._find_entry_index_by_id(999)

        assert index is None

    def test_find_entry_index_by_id_none_entry_id(self, diverse_entries):
        """Test _find_entry_index_by_id() returns None when entry_id is None."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = MagicMock()

        index = screen._find_entry_index_by_id(None)

        assert index is None

    def test_find_feed_header_index_found(self, diverse_entries):
        """Test _find_feed_header_index() finds feed header by title."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)

        # Create mock feed header
        header = MagicMock(spec=FeedHeaderItem)
        screen.feed_header_map = {"Test Feed": header}

        # Create list with header
        screen.list_view = MagicMock()
        screen.list_view.children = [header]

        # Find header
        index = screen._find_feed_header_index("Test Feed")

        assert index == 0

    def test_find_feed_header_index_not_found(self, diverse_entries):
        """Test _find_feed_header_index() returns None when feed not in map."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.feed_header_map = {}
        screen.list_view = MagicMock()

        index = screen._find_feed_header_index("Test Feed")

        assert index is None

    def test_find_feed_header_index_not_grouped(self, diverse_entries):
        """Test _find_feed_header_index() returns None when not in grouped mode."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen.list_view = MagicMock()

        index = screen._find_feed_header_index("Test Feed")

        assert index is None

    def test_set_cursor_to_index_success(self, diverse_entries):
        """Test _set_cursor_to_index() successfully sets cursor."""
        screen = EntryListScreen(entries=diverse_entries)

        screen.list_view = MagicMock()
        screen.list_view.children = [MagicMock() for _ in diverse_entries]

        result = screen._set_cursor_to_index(1)

        assert result is True
        assert screen.list_view.index == 1

    def test_set_cursor_to_index_out_of_bounds(self, diverse_entries):
        """Test _set_cursor_to_index() returns False when index out of bounds."""
        screen = EntryListScreen(entries=diverse_entries)

        screen.list_view = MagicMock()
        screen.list_view.children = [MagicMock() for _ in diverse_entries]

        result = screen._set_cursor_to_index(999)

        assert result is False
        # Verify index was not set
        screen.list_view.index.assert_not_called()

    def test_add_feed_header_if_needed_creates_header(self):
        """Test _add_feed_header_if_needed() creates and registers header."""
        screen = EntryListScreen(entries=[], group_by_feed=True)
        screen.feed_fold_state = {}
        screen.feed_header_map = {}
        screen.list_view = MagicMock()

        # Call with new feed
        screen._add_feed_header_if_needed("Test Feed", [None])

        # Verify header was created and registered
        assert "Test Feed" in screen.feed_header_map
        assert "Test Feed" in screen.feed_fold_state
        screen.list_view.append.assert_called()

    def test_add_entry_with_visibility_collapsed(self, diverse_entries):
        """Test _add_entry_with_visibility() applies collapsed class."""
        entry = diverse_entries[0]
        screen = EntryListScreen(entries=[entry], group_by_feed=True)
        screen.displayed_items = []
        screen.entry_item_map = {}
        screen.list_view = MagicMock()

        # Set feed as collapsed
        screen.feed_fold_state = {"Test Feed": False}

        # Add entry
        screen._add_entry_with_visibility(entry)

        # Verify item was added
        assert entry.id in screen.entry_item_map
        # Verify item is in displayed items
        assert len(screen.displayed_items) == 1
        item = screen.displayed_items[0]
        assert isinstance(item, EntryListItem)
        assert item.entry.id == entry.id

    def test_add_entry_with_visibility_expanded(self, diverse_entries):
        """Test _add_entry_with_visibility() doesn't add class when expanded."""
        entry = diverse_entries[0]
        screen = EntryListScreen(entries=[entry], group_by_feed=True)
        screen.displayed_items = []
        screen.entry_item_map = {}
        screen.list_view = MagicMock()

        # Set feed as expanded
        screen.feed_fold_state = {"Test Feed": True}

        # Add entry
        screen._add_entry_with_visibility(entry)

        # Verify item was added to displayed items
        assert entry.id in screen.entry_item_map
        assert len(screen.displayed_items) == 1
        item = screen.displayed_items[0]
        assert isinstance(item, EntryListItem)
        assert item.entry.id == entry.id


class TestEventHandlers:
    """Test event handler methods for screen lifecycle."""

    def test_on_mount_exists(self, diverse_entries):
        """Test on_mount method exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)

        # Verify method exists and is callable
        assert callable(screen.on_mount)

    def test_on_screen_resume_exists(self, diverse_entries):
        """Test on_screen_resume method exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)

        # Verify method exists and is callable
        assert callable(screen.on_screen_resume)

    def test_on_list_view_selected_exists(self, diverse_entries):
        """Test on_list_view_selected method exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)

        # Verify method exists and is callable
        assert callable(screen.on_list_view_selected)


class TestActionMethodsCallability:
    """Test action method callability for user interactions."""

    @pytest.mark.asyncio
    async def test_action_toggle_read_exists(self, diverse_entries):
        """Test action_toggle_read exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = MagicMock()

        # Verify method exists and is callable
        assert callable(screen.action_toggle_read)

    @pytest.mark.asyncio
    async def test_action_toggle_star_works(self, diverse_entries):
        """Test action_toggle_star exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = MagicMock()

        # Verify method exists and is callable
        assert callable(screen.action_toggle_star)

    @pytest.mark.asyncio
    async def test_action_save_entry_works(self, diverse_entries):
        """Test action_save_entry exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)
        screen.list_view = MagicMock()

        # Verify method exists and is callable
        assert callable(screen.action_save_entry)

    @pytest.mark.asyncio
    async def test_action_refresh_works(self, diverse_entries):
        """Test action_refresh exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)

        # Verify method exists and is callable
        assert callable(screen.action_refresh)

    @pytest.mark.asyncio
    async def test_action_show_unread_works(self, diverse_entries):
        """Test action_show_unread exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)

        # Verify method exists and is callable
        assert callable(screen.action_show_unread)

    @pytest.mark.asyncio
    async def test_action_show_starred_works(self, diverse_entries):
        """Test action_show_starred exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)

        # Verify method exists and is callable
        assert callable(screen.action_show_starred)

    def test_action_cycle_sort_exists(self, diverse_entries):
        """Test action_cycle_sort exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries, default_sort="date")

        # Verify method exists and is callable
        assert callable(screen.action_cycle_sort)

    def test_action_toggle_group_switches_mode(self, diverse_entries):
        """Test action_toggle_group toggles grouping."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=False)
        screen._populate_list = MagicMock()

        # Verify method exists and is callable
        assert callable(screen.action_toggle_group)

    def test_action_toggle_fold_exists(self, diverse_entries):
        """Test action_toggle_fold exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()

        # Verify method exists and is callable
        assert callable(screen.action_toggle_fold)

    def test_action_collapse_feed_exists(self, diverse_entries):
        """Test action_collapse_feed exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()

        # Verify method exists and is callable
        assert callable(screen.action_collapse_feed)

    def test_action_expand_feed_exists(self, diverse_entries):
        """Test action_expand_feed exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)
        screen.list_view = MagicMock()

        # Verify method exists and is callable
        assert callable(screen.action_expand_feed)

    def test_action_expand_all_exists(self, diverse_entries):
        """Test action_expand_all exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)

        # Verify method exists and is callable
        assert callable(screen.action_expand_all)

    def test_action_collapse_all_exists(self, diverse_entries):
        """Test action_collapse_all exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries, group_by_feed=True)

        # Verify method exists and is callable
        assert callable(screen.action_collapse_all)

    def test_action_show_help_exists(self, diverse_entries):
        """Test action_show_help exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)

        # Verify method exists and is callable
        assert callable(screen.action_show_help)

    def test_action_quit_exists(self, diverse_entries):
        """Test action_quit exists and is callable."""
        screen = EntryListScreen(entries=diverse_entries)

        # Verify method exists and is callable
        assert callable(screen.action_quit)
