"""Tests for entry list screen functionality."""

from datetime import UTC, datetime

import pytest

from miniflux_tui.api.models import Entry, Feed
from miniflux_tui.ui.screens.entry_list import EntryListScreen


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
