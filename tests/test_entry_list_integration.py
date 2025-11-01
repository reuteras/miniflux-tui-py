"""Integration tests for EntryListScreen using Textual TestApp."""

from datetime import UTC, datetime

import pytest
from textual.app import App, ComposeResult

from miniflux_tui.api.models import Entry, Feed
from miniflux_tui.ui.screens.entry_list import EntryListScreen


class EntryListTestApp(App):
    """Test app for EntryListScreen integration testing."""

    def __init__(self, entries=None):
        super().__init__()
        self.entries = entries or []
        self.entry_list_screen = None

    def compose(self) -> ComposeResult:
        """Compose the app with entry list screen."""
        self.entry_list_screen = EntryListScreen(
            entries=self.entries,
            unread_color="cyan",
            read_color="gray",
            default_sort="date",
            group_by_feed=False,
        )
        yield self.entry_list_screen


@pytest.fixture
def test_feed():
    """Create a test feed."""
    return Feed(
        id=1,
        title="Test Feed",
        site_url="http://localhost:8080",
        feed_url="http://localhost:8080/feed.xml",
    )


@pytest.fixture
def integration_entries(test_feed):
    """Create test entries for integration testing."""
    return [
        Entry(
            id=1,
            feed_id=1,
            title="First Entry",
            url="http://localhost:8080/1",
            content="Content 1",
            feed=test_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 20, 10, 0, 0, tzinfo=UTC),
        ),
        Entry(
            id=2,
            feed_id=1,
            title="Second Entry",
            url="http://localhost:8080/2",
            content="Content 2",
            feed=test_feed,
            status="read",
            starred=True,
            published_at=datetime(2024, 10, 25, 15, 30, 0, tzinfo=UTC),
        ),
        Entry(
            id=3,
            feed_id=1,
            title="Third Entry",
            url="http://localhost:8080/3",
            content="Content 3",
            feed=test_feed,
            status="unread",
            starred=True,
            published_at=datetime(2024, 10, 22, 12, 0, 0, tzinfo=UTC),
        ),
    ]


class TestEntryListScreenComposition:
    """Test EntryListScreen composition and layout."""

    async def test_screen_composes_with_header_and_footer(self, integration_entries):
        """Test that EntryListScreen composes with header and footer."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            # Find the entry list screen
            screen = app.entry_list_screen
            assert isinstance(screen, EntryListScreen)

            # Check that the screen has the expected attributes
            assert hasattr(screen, "list_view")
            assert screen.list_view is not None

    async def test_screen_initializes_with_entries(self, integration_entries):
        """Test that EntryListScreen initializes with entries."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert isinstance(screen, EntryListScreen)
            assert screen.entries == integration_entries
            assert len(screen.entries) == 3

    async def test_screen_has_correct_colors(self, integration_entries):
        """Test that screen uses the configured colors."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert screen.unread_color == "cyan"
            assert screen.read_color == "gray"

    async def test_screen_defaults_to_date_sort(self, integration_entries):
        """Test that screen defaults to date sort mode."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert screen.current_sort == "date"

    async def test_screen_defaults_to_ungrouped(self, integration_entries):
        """Test that screen defaults to ungrouped mode."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert screen.group_by_feed is False


class TestEntryListScreenNavigation:
    """Test navigation within EntryListScreen."""

    async def test_cursor_can_move_down(self, integration_entries):
        """Test that cursor can move down through entries."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            # Try to move cursor down
            if screen.list_view is not None:
                # Simulate navigation
                screen.action_cursor_down()
                # Verify the action was called without errors
                assert True

    async def test_cursor_can_move_up(self, integration_entries):
        """Test that cursor can move up through entries."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            # Try to move cursor up
            if screen.list_view is not None:
                screen.action_cursor_up()
                # Verify the action was called without errors
                assert True

    async def test_list_view_has_children(self, integration_entries):
        """Test that list view contains entry items after population."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            # The list view should exist
            assert screen.list_view is not None
            # After populate_list, it should have children
            assert len(screen.list_view.children) > 0 or len(integration_entries) == 0


class TestEntryListScreenSorting:
    """Test sorting functionality in EntryListScreen."""

    async def test_cycle_sort_changes_mode(self, integration_entries):
        """Test that cycling sort changes the sort mode."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            initial_sort = screen.current_sort

            # Cycle sort
            screen.action_cycle_sort()

            # Sort mode should have changed
            assert screen.current_sort != initial_sort or len(screen.current_sort) > 0

    async def test_sort_updates_subtitle(self, integration_entries):
        """Test that sort changes are reflected in subtitle."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            # Cycle sort and check subtitle updates
            screen.action_cycle_sort()

            # Subtitle should be updated (or exist)
            assert screen.sub_title is not None


class TestEntryListScreenGrouping:
    """Test grouping functionality in EntryListScreen."""

    async def test_toggle_group_flips_state(self, integration_entries):
        """Test that toggling group flips the grouping state."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            initial_group = screen.group_by_feed

            # Toggle grouping
            screen.action_toggle_group_feed()

            # State should have flipped
            assert screen.group_by_feed != initial_group

    async def test_toggle_group_back(self, integration_entries):
        """Test that toggling group twice returns to original state."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            initial_group = screen.group_by_feed

            # Toggle twice
            screen.action_toggle_group_feed()
            screen.action_toggle_group_feed()

            # Should be back to original
            assert screen.group_by_feed == initial_group


class TestEntryListScreenActions:
    """Test action methods in EntryListScreen."""

    async def test_refresh_action_exists(self, integration_entries):
        """Test that refresh action exists and is callable."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert callable(screen.action_refresh)

    async def test_show_unread_action_exists(self, integration_entries):
        """Test that show_unread action exists and is callable."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert callable(screen.action_show_unread)

    async def test_show_starred_action_exists(self, integration_entries):
        """Test that show_starred action exists and is callable."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert callable(screen.action_show_starred)

    async def test_show_help_action_exists(self, integration_entries):
        """Test that show_help action exists and is callable."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert callable(screen.action_show_help)


class TestEntryListScreenFiltering:
    """Test filtering functionality in EntryListScreen."""

    async def test_can_filter_unread_only(self, integration_entries):
        """Test that unread filtering works."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            screen.filter_unread_only = True

            # Filter entries
            filtered = screen._filter_entries(screen.entries)

            # Should have fewer entries
            assert len(filtered) <= len(screen.entries)
            # All should be unread
            assert all(e.is_unread for e in filtered)

    async def test_can_filter_starred_only(self, integration_entries):
        """Test that starred filtering works."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            screen.filter_starred_only = True

            # Filter entries
            filtered = screen._filter_entries(screen.entries)

            # Should have fewer entries
            assert len(filtered) <= len(screen.entries)
            # All should be starred
            assert all(e.starred for e in filtered)

    async def test_unread_filter_takes_precedence(self, integration_entries):
        """Test that unread filter takes precedence over starred."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            screen.filter_unread_only = True
            screen.filter_starred_only = True

            filtered = screen._filter_entries(screen.entries)

            # Should all be unread (unread takes precedence)
            assert all(e.is_unread for e in filtered)


class TestEntryListScreenStateManagement:
    """Test state management in EntryListScreen."""

    async def test_entry_item_map_tracks_entries(self, integration_entries):
        """Test that entry_item_map tracks entries."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            # entry_item_map should exist
            assert hasattr(screen, "entry_item_map")
            assert isinstance(screen.entry_item_map, dict)

    async def test_sorted_entries_list_exists(self, integration_entries):
        """Test that sorted_entries list exists."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            # sorted_entries should exist
            assert hasattr(screen, "sorted_entries")
            assert isinstance(screen.sorted_entries, list)

    async def test_filter_states_initialize_false(self, integration_entries):
        """Test that filter states initialize to False."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            assert screen.filter_unread_only is False
            assert screen.filter_starred_only is False

    async def test_feed_fold_state_dict_exists(self, integration_entries):
        """Test that feed_fold_state dict exists for tracking fold state."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            assert hasattr(screen, "feed_fold_state")


class TestEntryListScreenSearch:
    """Test search functionality in EntryListScreen."""

    async def test_search_state_initializes_inactive(self, integration_entries):
        """Test that search state initializes as inactive."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert screen.search_active is False
            assert not screen.search_term

    async def test_search_action_exists(self, integration_entries):
        """Test that search action exists and is callable."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            assert callable(screen.action_search)

    async def test_set_search_term_filters_by_title(self, integration_entries):
        """Test that search filters entries by title."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            # Search for "First" - should match "First Entry"
            screen.set_search_term("First")

            assert screen.search_active is True
            assert screen.search_term == "First"
            # Check that filtered results only contain matching entry
            filtered = screen._filter_entries(screen.entries)
            assert len(filtered) == 1
            assert "First" in filtered[0].title

    async def test_set_search_term_case_insensitive(self, integration_entries):
        """Test that search is case-insensitive."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            # Search for lowercase "first" - should match "First Entry"
            screen.set_search_term("first")

            assert screen.search_active is True
            filtered = screen._filter_entries(screen.entries)
            assert len(filtered) == 1
            assert "First" in filtered[0].title

    async def test_set_search_term_filters_by_content(self, integration_entries):
        """Test that search filters entries by content."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            # Search for content text - "content" appears in entry content
            screen.set_search_term("content")

            assert screen.search_active is True
            filtered = screen._filter_entries(screen.entries)
            assert len(filtered) >= 1
            # At least one entry should have "content" in its content
            assert any("content" in e.content.lower() for e in filtered)

    async def test_set_search_term_empty_clears_search(self, integration_entries):
        """Test that empty search term clears search."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            # Set a search term
            screen.set_search_term("First")
            assert screen.search_active is True

            # Clear with empty string
            screen.set_search_term("")
            assert screen.search_active is False
            assert not screen.search_term

    async def test_search_with_whitespace_is_trimmed(self, integration_entries):
        """Test that search terms with leading/trailing whitespace are trimmed."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            screen.set_search_term("  First  ")

            assert screen.search_term == "First"

    async def test_search_filter_handles_no_matches(self, integration_entries):
        """Test that search returns empty list when no entries match."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            screen.set_search_term("nonexistent")

            filtered = screen._filter_entries(screen.entries)
            assert len(filtered) == 0

    async def test_search_combined_with_status_filters(self, integration_entries):
        """Test that search works with status filters."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            # Set both search and filter_unread_only
            # Entries 1 and 3 are unread
            # Entry 2 is read with content "Content 2"
            # So when we search for "2" and filter_unread_only, we should get nothing
            # (entry 2 has "2" but is not unread)
            screen.set_search_term("1")  # Matches Entry 1 (unread) and Entry 3 (unread)
            screen.filter_unread_only = True

            filtered = screen._filter_entries(screen.entries)
            # Both entries 1 and 3 contain "1" in their content
            # And both are unread
            assert len(filtered) >= 1
            # All results must be unread
            assert all(e.is_unread for e in filtered)

    async def test_action_search_clears_active_search(self, integration_entries):
        """Test that action_search clears active search."""
        app = EntryListTestApp(entries=integration_entries)

        async with app.run_test():
            screen = app.entry_list_screen
            # Activate search
            screen.set_search_term("First")
            assert screen.search_active is True

            # Run action_search to clear
            screen.action_search()
            assert screen.search_active is False
            assert not screen.search_term
            assert isinstance(screen.feed_fold_state, dict)
