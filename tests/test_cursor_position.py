# SPDX-License-Identifier: MIT
"""Comprehensive cursor position tests for entry list navigation.

Tests verify cursor behavior in:
- Standard mode (no grouping)
- Group by feed mode
- Group by category mode
- Expand/collapse operations
- Navigation to entry reader and back
"""

from datetime import UTC, datetime, timedelta

import pytest
from textual.app import App, ComposeResult

from miniflux_tui.api.models import Category, Entry, Feed
from miniflux_tui.ui.screens.entry_list import EntryListScreen


class CursorTestApp(App):
    """Test app for cursor position testing."""

    def __init__(self, entries=None, categories=None, **kwargs):
        super().__init__(**kwargs)
        self.entries = entries or []
        self.categories = categories or []
        self.entry_list_screen = None

    def compose(self) -> ComposeResult:
        """Compose the app with entry list screen."""
        self.entry_list_screen = EntryListScreen(
            entries=self.entries,
            categories=self.categories,
            unread_color="cyan",
            read_color="gray",
            default_sort="date",
            group_by_feed=False,
            group_collapsed=False,
        )
        yield self.entry_list_screen


@pytest.fixture
def cursor_test_categories():
    """Create 4 categories for cursor tests."""
    return [
        Category(id=1, title="Category A"),
        Category(id=2, title="Category B"),
        Category(id=3, title="Category C"),
        Category(id=4, title="Category D"),
    ]


@pytest.fixture
def cursor_test_feeds(cursor_test_categories):
    """Create feeds across categories."""
    return [
        # Category A (2 feeds)
        Feed(id=1, title="Feed A1", site_url="https://a1.com", feed_url="https://a1.com/feed", category_id=1),
        Feed(id=2, title="Feed A2", site_url="https://a2.com", feed_url="https://a2.com/feed", category_id=1),
        # Category B (2 feeds)
        Feed(id=3, title="Feed B1", site_url="https://b1.com", feed_url="https://b1.com/feed", category_id=2),
        Feed(id=4, title="Feed B2", site_url="https://b2.com", feed_url="https://b2.com/feed", category_id=2),
        # Category C (2 feeds)
        Feed(id=5, title="Feed C1", site_url="https://c1.com", feed_url="https://c1.com/feed", category_id=3),
        Feed(id=6, title="Feed C2", site_url="https://c2.com", feed_url="https://c2.com/feed", category_id=3),
        # Category D (2 feeds)
        Feed(id=7, title="Feed D1", site_url="https://d1.com", feed_url="https://d1.com/feed", category_id=4),
        Feed(id=8, title="Feed D2", site_url="https://d2.com", feed_url="https://d2.com/feed", category_id=4),
    ]


@pytest.fixture
def cursor_test_entries(cursor_test_feeds):
    """Create entries for cursor position tests.

    Distribution: 2 entries per feed (16 total entries)
    All entries are unread for testing purposes.
    """
    entries = []
    entry_id = 1
    base_date = datetime(2024, 11, 6, 12, 0, 0, tzinfo=UTC)

    for feed in cursor_test_feeds:
        for i in range(2):
            entries.append(
                Entry(
                    id=entry_id,
                    feed_id=feed.id,
                    title=f"{feed.title} Entry {i + 1}",
                    url=f"https://example.com/entry-{entry_id}",
                    content=f"<p>Content for {feed.title} entry {i + 1}</p>",
                    feed=feed,
                    status="unread",
                    starred=False,
                    published_at=base_date - timedelta(hours=entry_id),
                )
            )
            entry_id += 1

    return entries


class TestCursorPositionStandardMode:
    """Test cursor position in standard mode (no grouping)."""

    async def test_cursor_starts_at_position_0(self, cursor_test_entries):
        """Test cursor starts at position 0 in standard mode."""
        app = CursorTestApp(entries=cursor_test_entries)

        async with app.run_test():
            screen = app.entry_list_screen

            # Verify cursor is at position 0
            assert screen.list_view.index == 0

            # Verify first item is the first entry (newest by date)
            first_child = screen.list_view.children[0]
            assert hasattr(first_child, "entry")
            assert first_child.entry.title == "Feed A1 Entry 1"

    async def test_cursor_navigation_in_standard_mode(self, cursor_test_entries):
        """Test cursor moves correctly with j/k in standard mode."""
        app = CursorTestApp(entries=cursor_test_entries)

        async with app.run_test() as pilot:
            screen = app.entry_list_screen

            # Start at position 0
            assert screen.list_view.index == 0

            # Press j three times
            await pilot.press("j", "j", "j")

            # Should be at position 3
            assert screen.list_view.index == 3


class TestCursorPositionGroupByFeed:
    """Test cursor position in group by feed mode."""

    async def test_cursor_starts_at_position_0_grouped(self, cursor_test_entries):
        """Test cursor starts at position 0 when grouped by feed."""
        app = CursorTestApp(entries=cursor_test_entries)

        async with app.run_test() as pilot:
            screen = app.entry_list_screen

            # Enable group by feed
            screen.group_by_feed = True
            screen._populate_list()
            await pilot.pause()

            # Verify cursor is at position 0
            assert screen.list_view.index == 0

            # First item should be a FeedHeaderItem
            from miniflux_tui.ui.screens.entry_list import FeedHeaderItem

            first_child = screen.list_view.children[0]
            assert isinstance(first_child, FeedHeaderItem)

    async def test_navigation_through_collapsed_feed_groups(self, cursor_test_entries):
        """Test that 3x j moves to the 3rd feed header when feeds are collapsed."""
        app = CursorTestApp(entries=cursor_test_entries)

        async with app.run_test() as pilot:
            screen = app.entry_list_screen

            # Enable group by feed with all groups collapsed
            screen.group_by_feed = True
            screen.group_collapsed = True
            screen._populate_list()
            await pilot.pause()

            # Start at position 0 (Feed A1 header)
            assert screen.list_view.index == 0

            # Press j three times (should move through collapsed feed headers)
            await pilot.press("j", "j", "j")

            # Should be at the 4th visible item (index 3)
            assert screen.list_view.index == 3

            # Verify we're on a feed header (not an entry)
            from miniflux_tui.ui.screens.entry_list import FeedHeaderItem

            highlighted = screen.list_view.highlighted_child
            assert isinstance(highlighted, FeedHeaderItem)

    async def test_expand_collapse_maintains_position(self, cursor_test_entries):
        """Test that expanding/collapsing with l/h maintains cursor position."""
        app = CursorTestApp(entries=cursor_test_entries)

        async with app.run_test() as pilot:
            screen = app.entry_list_screen

            # Enable group by feed with collapsed groups
            screen.group_by_feed = True
            screen.group_collapsed = True
            screen._populate_list()
            await pilot.pause()

            # Move to second feed header
            await pilot.press("j")

            # Remember position
            position_before = screen.list_view.index
            assert position_before == 1

            # Expand with 'l'
            await pilot.press("l")

            # Position should still be 1 (on the same header)
            assert screen.list_view.index == position_before

            # Collapse with 'h'
            await pilot.press("h")

            # Position should still be 1
            assert screen.list_view.index == position_before


class TestCursorPositionGroupByCategory:
    """Test cursor position in group by category mode."""

    async def test_cursor_starts_at_position_0_category_grouped(self, cursor_test_entries, cursor_test_categories):
        """Test cursor starts at position 0 when grouped by category."""
        app = CursorTestApp(entries=cursor_test_entries, categories=cursor_test_categories)

        async with app.run_test() as pilot:
            screen = app.entry_list_screen

            # Enable group by category
            screen.group_by_category = True
            screen._populate_list()
            await pilot.pause()

            # Verify cursor is at position 0
            assert screen.list_view.index == 0

            # First item should be a CategoryHeaderItem
            from miniflux_tui.ui.screens.entry_list import CategoryHeaderItem

            first_child = screen.list_view.children[0]
            assert isinstance(first_child, CategoryHeaderItem)

    async def test_navigation_through_collapsed_category_groups(self, cursor_test_entries, cursor_test_categories):
        """Test that 3x j moves to the 3rd category header when categories are collapsed."""
        app = CursorTestApp(entries=cursor_test_entries, categories=cursor_test_categories)

        async with app.run_test() as pilot:
            screen = app.entry_list_screen

            # Enable group by category with all groups collapsed
            screen.group_by_category = True
            screen.group_collapsed = True
            screen._populate_list()
            await pilot.pause()

            # Start at position 0 (Category A header)
            assert screen.list_view.index == 0

            # Press j three times
            await pilot.press("j", "j", "j")

            # Should be at position 3 (Category D header)
            assert screen.list_view.index == 3

            # Verify we're on a category header
            from miniflux_tui.ui.screens.entry_list import CategoryHeaderItem

            highlighted = screen.list_view.highlighted_child
            assert isinstance(highlighted, CategoryHeaderItem)

    async def test_expand_collapse_category_maintains_position(self, cursor_test_entries, cursor_test_categories):
        """Test that expanding/collapsing categories with l/h maintains cursor position."""
        app = CursorTestApp(entries=cursor_test_entries, categories=cursor_test_categories)

        async with app.run_test() as pilot:
            screen = app.entry_list_screen

            # Enable group by category with collapsed groups
            screen.group_by_category = True
            screen.group_collapsed = True
            screen._populate_list()
            await pilot.pause()

            # Move to second category header
            await pilot.press("j")

            position_before = screen.list_view.index
            assert position_before == 1

            # Expand with 'l'
            await pilot.press("l")

            # Position should be maintained
            assert screen.list_view.index == position_before

            # Collapse with 'h'
            await pilot.press("h")

            # Position should still be maintained
            assert screen.list_view.index == position_before


class TestCursorPositionEdgeCases:
    """Test cursor position edge cases."""

    async def test_cursor_at_last_position(self, cursor_test_entries):
        """Test cursor can navigate to the last entry."""
        app = CursorTestApp(entries=cursor_test_entries)

        async with app.run_test() as pilot:
            screen = app.entry_list_screen

            # Get total number of visible items
            total_items = len(screen.list_view.children)

            # Navigate to the end (press j more times than needed to ensure we reach the end)
            for _ in range(total_items + 5):
                await pilot.press("j")

            # Should be at the last position
            final_position = screen.list_view.index
            assert final_position == total_items - 1
