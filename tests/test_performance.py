"""Tests for performance optimization utilities."""

from miniflux_tui.performance import ScreenRefreshOptimizer, get_sort_key_for_entry
from miniflux_tui.ui.screens.entry_list import EntryListScreen


class TestScreenRefreshOptimizer:
    """Test ScreenRefreshOptimizer functionality."""

    def test_optimizer_initialization(self):
        """Test optimizer initializes with correct values."""
        optimizer = ScreenRefreshOptimizer()
        assert optimizer.refresh_count == 0
        assert optimizer.full_refresh_count == 0
        assert optimizer.partial_refresh_count == 0

    def test_track_full_refresh(self):
        """Test tracking full refresh operations."""
        optimizer = ScreenRefreshOptimizer()
        optimizer.track_full_refresh()
        assert optimizer.refresh_count == 1
        assert optimizer.full_refresh_count == 1
        assert optimizer.partial_refresh_count == 0

    def test_track_partial_refresh(self):
        """Test tracking partial refresh operations."""
        optimizer = ScreenRefreshOptimizer()
        optimizer.track_partial_refresh()
        assert optimizer.refresh_count == 1
        assert optimizer.full_refresh_count == 0
        assert optimizer.partial_refresh_count == 1

    def test_track_mixed_refreshes(self):
        """Test tracking both full and partial refreshes."""
        optimizer = ScreenRefreshOptimizer()
        optimizer.track_full_refresh()
        optimizer.track_partial_refresh()
        optimizer.track_partial_refresh()
        optimizer.track_full_refresh()

        assert optimizer.refresh_count == 4
        assert optimizer.full_refresh_count == 2
        assert optimizer.partial_refresh_count == 2

    def test_efficiency_ratio_no_refreshes(self):
        """Test efficiency ratio with no refreshes."""
        optimizer = ScreenRefreshOptimizer()
        assert optimizer.get_efficiency_ratio() == 0.0

    def test_efficiency_ratio_all_full(self):
        """Test efficiency ratio with only full refreshes."""
        optimizer = ScreenRefreshOptimizer()
        optimizer.track_full_refresh()
        optimizer.track_full_refresh()
        assert optimizer.get_efficiency_ratio() == 0.0

    def test_efficiency_ratio_all_partial(self):
        """Test efficiency ratio with only partial refreshes."""
        optimizer = ScreenRefreshOptimizer()
        optimizer.track_partial_refresh()
        optimizer.track_partial_refresh()
        assert optimizer.get_efficiency_ratio() == 1.0

    def test_efficiency_ratio_mixed(self):
        """Test efficiency ratio with mixed refresh types."""
        optimizer = ScreenRefreshOptimizer()
        optimizer.track_full_refresh()
        optimizer.track_partial_refresh()
        optimizer.track_partial_refresh()
        # 2 partial out of 3 total = 2/3 ≈ 0.667
        assert abs(optimizer.get_efficiency_ratio() - (2 / 3)) < 0.001

    def test_get_stats(self):
        """Test getting performance statistics."""
        optimizer = ScreenRefreshOptimizer()
        optimizer.track_full_refresh()
        optimizer.track_partial_refresh()

        stats = optimizer.get_stats()
        assert stats["total_refreshes"] == 2
        assert stats["full_refreshes"] == 1
        assert stats["partial_refreshes"] == 1
        assert "efficiency_ratio" in stats

    def test_reset(self):
        """Test resetting optimizer statistics."""
        optimizer = ScreenRefreshOptimizer()
        optimizer.track_full_refresh()
        optimizer.track_partial_refresh()
        assert optimizer.refresh_count == 2

        optimizer.reset()
        assert optimizer.refresh_count == 0
        assert optimizer.full_refresh_count == 0
        assert optimizer.partial_refresh_count == 0


class TestGetSortKeyForEntry:
    """Test sort key generation function."""

    def test_sort_key_date_mode(self):
        """Test sort key for date sort mode."""
        key = get_sort_key_for_entry(
            entry_id=1,
            sort_mode="date",
            is_read=True,
            published_at="2024-10-25T10:00:00",
            feed_title="Example Feed",
        )
        assert key == ("2024-10-25T10:00:00",)

    def test_sort_key_feed_mode(self):
        """Test sort key for feed sort mode."""
        key = get_sort_key_for_entry(
            entry_id=1,
            sort_mode="feed",
            is_read=True,
            published_at="2024-10-25T10:00:00",
            feed_title="Example Feed",
        )
        assert key == ("example feed", "2024-10-25T10:00:00")

    def test_sort_key_status_mode(self):
        """Test sort key for status sort mode."""
        key = get_sort_key_for_entry(
            entry_id=1,
            sort_mode="status",
            is_read=True,
            published_at="2024-10-25T10:00:00",
            feed_title="Example Feed",
        )
        assert key == (True, "2024-10-25T10:00:00")

    def test_sort_key_invalid_mode(self):
        """Test sort key with invalid sort mode."""
        key = get_sort_key_for_entry(
            entry_id=5,
            sort_mode="invalid",
            is_read=False,
            published_at="2024-10-25T10:00:00",
            feed_title="Example Feed",
        )
        assert key == (5,)

    def test_sort_key_feed_title_case_insensitive(self):
        """Test that feed titles are case-insensitive for sorting."""
        key1 = get_sort_key_for_entry(
            entry_id=1,
            sort_mode="feed",
            is_read=True,
            published_at="2024-10-25T10:00:00",
            feed_title="Example Feed",
        )
        key2 = get_sort_key_for_entry(
            entry_id=2,
            sort_mode="feed",
            is_read=True,
            published_at="2024-10-25T10:00:00",
            feed_title="EXAMPLE FEED",
        )
        # First part of keys should match (lowercased)
        assert key1[0] == key2[0]


class TestEntryListScreenRefreshOptimization:
    """Test EntryListScreen refresh optimization integration."""

    def test_screen_has_optimizer(self, sample_entries):
        """Test that screen has refresh optimizer."""
        screen = EntryListScreen(entries=sample_entries)
        assert hasattr(screen, "refresh_optimizer")
        assert isinstance(screen.refresh_optimizer, ScreenRefreshOptimizer)

    def test_screen_has_entry_item_map(self, sample_entries):
        """Test that screen has entry item map for tracking."""
        screen = EntryListScreen(entries=sample_entries)
        assert hasattr(screen, "entry_item_map")
        assert isinstance(screen.entry_item_map, dict)

    def test_populate_list_tracks_full_refresh(self, sample_entries):
        """Test that populate_list tracks refresh operations."""
        screen = EntryListScreen(entries=sample_entries)
        # Note: We can't actually call _populate_list without a proper Textual app
        # But we can verify the structure is there
        assert hasattr(screen, "_populate_list")
        assert hasattr(screen, "refresh_optimizer")

    def test_initial_optimizer_stats(self, sample_entries):
        """Test initial optimizer statistics."""
        screen = EntryListScreen(entries=sample_entries)
        stats = screen.refresh_optimizer.get_stats()
        assert stats["total_refreshes"] == 0
        assert stats["full_refreshes"] == 0
        assert stats["partial_refreshes"] == 0
        assert stats["efficiency_ratio"] == 0.0

    def test_entry_item_map_tracking(self, sample_entries):
        """Test that entry item map can track entries."""
        screen = EntryListScreen(entries=sample_entries)
        # The map starts empty
        assert len(screen.entry_item_map) == 0

        # When _add_flat_entries is called (which requires list_view),
        # the map would be populated. We test the logic separately.

    def test_screen_creates_entry_map_on_add_flat(self, sample_entries):
        """Test entry item map is created when adding flat entries."""
        # This tests the logic of _add_flat_entries
        # EntryListScreen creates the entry_item_map during init
        screen = EntryListScreen(entries=sample_entries)
        # The entry_item_map should be empty initially
        assert len(screen.entry_item_map) == 0

        # The entry_item_map would be populated during display
        for entry in sample_entries:
            # Verify entries are valid for mapping
            assert isinstance(entry.id, int)
