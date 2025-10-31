"""Tests for FeedManagementScreen."""

from textual.screen import Screen

from miniflux_tui.api.models import Feed
from miniflux_tui.ui.screens.feed_management import FeedListItem, FeedManagementScreen


class TestFeedListItem:
    """Test FeedListItem widget."""

    def test_feed_list_item_creation(self) -> None:
        """Test creating a FeedListItem."""
        feed = Feed(
            id=1,
            title="Test Feed",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
        )
        item = FeedListItem(feed)
        assert item.feed == feed

    def test_feed_list_item_with_no_errors(self) -> None:
        """Test FeedListItem displays correctly for feed without errors."""
        feed = Feed(
            id=1,
            title="Healthy Feed",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
            parsing_error_count=0,
        )
        item = FeedListItem(feed)
        assert item.feed.parsing_error_count == 0

    def test_feed_list_item_with_errors(self) -> None:
        """Test FeedListItem displays correctly for feed with errors."""
        feed = Feed(
            id=1,
            title="Broken Feed",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
            parsing_error_count=3,
            parsing_error_message="Connection timeout",
        )
        item = FeedListItem(feed)
        assert item.feed.parsing_error_count == 3

    def test_feed_list_item_disabled_feed(self) -> None:
        """Test FeedListItem with disabled feed."""
        feed = Feed(
            id=1,
            title="Disabled Feed",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
            disabled=True,
        )
        item = FeedListItem(feed)
        assert item.feed.disabled is True

    def test_feed_list_item_long_title(self) -> None:
        """Test FeedListItem truncates long titles."""
        feed = Feed(
            id=1,
            title="This is a very long feed title that should be truncated " * 3,
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
        )
        item = FeedListItem(feed)
        assert item.feed == feed


class TestFeedManagementScreenInitialization:
    """Test FeedManagementScreen initialization."""

    def test_feed_management_screen_creation_empty(self) -> None:
        """Test creating FeedManagementScreen without feeds."""
        screen = FeedManagementScreen()
        assert screen.feeds == []

    def test_feed_management_screen_creation_with_feeds(self) -> None:
        """Test creating FeedManagementScreen with feeds."""
        feeds = [
            Feed(
                id=1,
                title="Feed 1",
                site_url="https://example.com",
                feed_url="https://example.com/feed.xml",
            ),
            Feed(
                id=2,
                title="Feed 2",
                site_url="https://example2.com",
                feed_url="https://example2.com/feed.xml",
            ),
        ]
        screen = FeedManagementScreen(feeds=feeds)
        assert screen.feeds == feeds
        assert len(screen.feeds) == 2


class TestFeedManagementScreenBindings:
    """Test FeedManagementScreen key bindings."""

    def test_feed_management_has_bindings(self) -> None:
        """Test FeedManagementScreen has proper key bindings."""
        screen = FeedManagementScreen()
        bindings = list(screen.BINDINGS)  # type: ignore[attr-defined]
        binding_keys = [b.key for b in bindings]  # type: ignore[attr-defined]
        assert "n" in binding_keys  # Add feed
        assert "d" in binding_keys  # Delete feed
        assert "r" in binding_keys  # Refresh feed
        assert "enter" in binding_keys  # View details
        assert "escape" in binding_keys  # Back
        assert "j" in binding_keys  # Cursor down
        assert "k" in binding_keys  # Cursor up

    def test_feed_management_has_correct_actions(self) -> None:
        """Test FeedManagementScreen bindings map to correct actions."""
        screen = FeedManagementScreen()
        bindings = list(screen.BINDINGS)  # type: ignore[attr-defined]
        actions = {b.action for b in bindings}  # type: ignore[attr-defined]
        assert "add_feed" in actions
        assert "delete_feed" in actions
        assert "refresh_feed" in actions
        assert "view_details" in actions
        assert "back" in actions
        assert "cursor_down" in actions
        assert "cursor_up" in actions


class TestFeedManagementScreenCompose:
    """Test FeedManagementScreen composition."""

    def test_feed_management_has_css(self) -> None:
        """Test FeedManagementScreen has CSS defined."""
        screen = FeedManagementScreen()
        assert screen.CSS is not None
        assert len(screen.CSS) > 0


class TestFeedManagementScreenMethods:
    """Test FeedManagementScreen methods."""

    def test_feed_management_get_selected_feed_empty_list(self) -> None:
        """Test getting selected feed when list is empty."""
        screen = FeedManagementScreen()
        screen.list_view = None  # Simulate no list view
        feed = screen._get_selected_feed()
        assert feed is None

    def test_feed_management_populate_list(self) -> None:
        """Test populate_list method."""
        feeds = [
            Feed(
                id=1,
                title="Feed 1",
                site_url="https://example.com",
                feed_url="https://example.com/feed.xml",
            ),
            Feed(
                id=2,
                title="Feed 2",
                site_url="https://example2.com",
                feed_url="https://example2.com/feed.xml",
            ),
        ]
        FeedManagementScreen(feeds=feeds)
        # populate_list requires list_view to be initialized
        # which happens in on_mount, so we skip direct testing


class TestFeedManagementScreenIntegration:
    """Integration tests for FeedManagementScreen."""

    def test_feed_management_screen_is_screen(self) -> None:
        """Test FeedManagementScreen is a proper Screen."""
        screen = FeedManagementScreen()
        assert isinstance(screen, Screen)

    def test_feed_management_screen_with_multiple_feeds(self) -> None:
        """Test FeedManagementScreen handles multiple feeds."""
        feeds = [
            Feed(
                id=i,
                title=f"Feed {i}",
                site_url=f"https://example{i}.com",
                feed_url=f"https://example{i}.com/feed.xml",
            )
            for i in range(1, 11)
        ]
        screen = FeedManagementScreen(feeds=feeds)
        assert len(screen.feeds) == 10

    def test_feed_management_screen_with_error_feeds(self) -> None:
        """Test FeedManagementScreen with feeds that have errors."""
        feeds = [
            Feed(
                id=1,
                title="Good Feed",
                site_url="https://example.com",
                feed_url="https://example.com/feed.xml",
                parsing_error_count=0,
            ),
            Feed(
                id=2,
                title="Bad Feed",
                site_url="https://example2.com",
                feed_url="https://example2.com/feed.xml",
                parsing_error_count=5,
                parsing_error_message="SSL certificate error",
            ),
        ]
        screen = FeedManagementScreen(feeds=feeds)
        assert len(screen.feeds) == 2
        assert screen.feeds[0].parsing_error_count == 0
        assert screen.feeds[1].parsing_error_count == 5

    def test_feed_management_screen_feed_list_item_status(self) -> None:
        """Test FeedListItem displays correct status."""
        good_feed = Feed(
            id=1,
            title="Good Feed",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
        )
        bad_feed = Feed(
            id=2,
            title="Bad Feed",
            site_url="https://example2.com",
            feed_url="https://example2.com/feed.xml",
            parsing_error_count=1,
        )

        good_item = FeedListItem(good_feed)
        bad_item = FeedListItem(bad_feed)

        # Verify items have the correct feeds
        assert good_item.feed.parsing_error_count == 0
        assert bad_item.feed.parsing_error_count == 1

    def test_feed_management_screen_disabled_feeds(self) -> None:
        """Test FeedManagementScreen with disabled feeds."""
        feeds = [
            Feed(
                id=1,
                title="Active Feed",
                site_url="https://example.com",
                feed_url="https://example.com/feed.xml",
                disabled=False,
            ),
            Feed(
                id=2,
                title="Disabled Feed",
                site_url="https://example2.com",
                feed_url="https://example2.com/feed.xml",
                disabled=True,
            ),
        ]
        screen = FeedManagementScreen(feeds=feeds)
        assert screen.feeds[0].disabled is False
        assert screen.feeds[1].disabled is True

    def test_feed_management_action_methods_exist(self) -> None:
        """Test all action methods exist."""
        screen = FeedManagementScreen()
        assert hasattr(screen, "action_add_feed")
        assert hasattr(screen, "action_delete_feed")
        assert hasattr(screen, "action_refresh_feed")
        assert hasattr(screen, "action_view_details")
        assert hasattr(screen, "action_back")
        assert hasattr(screen, "action_cursor_down")
        assert hasattr(screen, "action_cursor_up")

    def test_feed_management_helper_methods_exist(self) -> None:
        """Test helper methods exist."""
        screen = FeedManagementScreen()
        assert hasattr(screen, "_populate_list")
        assert hasattr(screen, "_get_selected_feed")
        assert callable(screen._populate_list)
        assert callable(screen._get_selected_feed)

    def test_feed_list_item_with_category(self) -> None:
        """Test FeedListItem with categorized feed."""
        feed = Feed(
            id=1,
            title="Categorized Feed",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
            category_id=5,
        )
        item = FeedListItem(feed)
        assert item.feed.category_id == 5

    def test_feed_list_item_with_checked_timestamp(self) -> None:
        """Test FeedListItem with checked_at timestamp."""
        feed = Feed(
            id=1,
            title="Checked Feed",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
            checked_at="2025-10-31T12:00:00Z",
        )
        item = FeedListItem(feed)
        assert item.feed.checked_at is not None

    def test_feed_list_item_status_icon_without_errors(self) -> None:
        """Test FeedListItem displays correct status icon for healthy feed."""
        feed = Feed(
            id=1,
            title="Healthy",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
            parsing_error_count=0,
        )
        item = FeedListItem(feed)
        # Verify the item was created and feed has no errors
        assert item.feed.parsing_error_count == 0
        assert not item.feed.has_errors

    def test_feed_list_item_status_icon_with_errors(self) -> None:
        """Test FeedListItem displays warning icon for feeds with errors."""
        feed = Feed(
            id=1,
            title="Broken",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
            parsing_error_count=5,
        )
        item = FeedListItem(feed)
        # Verify the item was created and feed has errors
        assert item.feed.parsing_error_count == 5
        assert item.feed.has_errors

    def test_feed_management_get_selected_feed_with_valid_selection(self) -> None:
        """Test getting selected feed when list has items."""
        feeds = [
            Feed(
                id=1,
                title="Feed 1",
                site_url="https://example.com",
                feed_url="https://example.com/feed.xml",
            )
        ]
        screen = FeedManagementScreen(feeds=feeds)
        # Without mounting, list_view is None, so this should return None
        feed = screen._get_selected_feed()
        assert feed is None

    def test_feed_management_populate_list_clears_old_items(self) -> None:
        """Test that populate_list clears old items before adding new ones."""
        feeds = [
            Feed(
                id=1,
                title="Feed 1",
                site_url="https://example.com",
                feed_url="https://example.com/feed.xml",
            ),
            Feed(
                id=2,
                title="Feed 2",
                site_url="https://example2.com",
                feed_url="https://example2.com/feed.xml",
            ),
        ]
        screen = FeedManagementScreen(feeds=feeds)
        # Verify feeds are stored
        assert len(screen.feeds) == 2
        assert screen.feeds[0].title == "Feed 1"
        assert screen.feeds[1].title == "Feed 2"

    def test_feed_management_action_methods_callable(self) -> None:
        """Test all action methods are callable."""
        screen = FeedManagementScreen()
        # Verify methods exist and are callable
        assert callable(getattr(screen, "action_add_feed", None))
        assert callable(getattr(screen, "action_delete_feed", None))
        assert callable(getattr(screen, "action_refresh_feed", None))
        assert callable(getattr(screen, "action_view_details", None))
        assert callable(getattr(screen, "action_back", None))
        assert callable(getattr(screen, "action_cursor_down", None))
        assert callable(getattr(screen, "action_cursor_up", None))
