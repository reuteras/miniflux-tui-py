"""Tests for API data models."""

from datetime import UTC, datetime

from miniflux_tui.api.models import Entry, Feed


class TestFeed:
    """Test Feed model."""

    def test_feed_creation(self):
        """Test creating a Feed instance."""
        feed = Feed(
            id=1,
            title="Test Feed",
            site_url="https://example.com",
            feed_url="https://example.com/feed.xml",
        )
        assert feed.id == 1
        assert feed.title == "Test Feed"
        assert feed.site_url == "https://example.com"
        assert feed.feed_url == "https://example.com/feed.xml"

    def test_feed_from_dict(self):
        """Test creating a Feed from dictionary."""
        data = {
            "id": 2,
            "title": "Another Feed",
            "site_url": "https://blog.example.com",
            "feed_url": "https://blog.example.com/rss",
        }
        feed = Feed.from_dict(data)
        assert feed.id == 2
        assert feed.title == "Another Feed"


class TestEntry:
    """Test Entry model."""

    def test_entry_creation(self, sample_feed):
        """Test creating an Entry instance."""
        entry = Entry(
            id=1,
            feed_id=1,
            title="Test Entry",
            url="https://example.com/article",
            content="<p>Content</p>",
            feed=sample_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 24, 12, 0, 0, tzinfo=UTC),
        )
        assert entry.id == 1
        assert entry.title == "Test Entry"
        assert entry.status == "unread"
        assert entry.starred is False

    def test_entry_is_unread(self, sample_entry):
        """Test is_unread property."""
        sample_entry.status = "unread"
        assert sample_entry.is_unread is True

        sample_entry.status = "read"
        assert sample_entry.is_unread is False

    def test_entry_is_read(self, sample_entry):
        """Test is_read property."""
        sample_entry.status = "read"
        assert sample_entry.is_read is True

        sample_entry.status = "unread"
        assert sample_entry.is_read is False

    def test_entry_from_dict(self):
        """Test creating an Entry from dictionary."""
        data = {
            "id": 5,
            "feed_id": 1,
            "title": "From Dict Entry",
            "url": "https://example.com/test",
            "content": "<p>Test</p>",
            "feed": {
                "id": 1,
                "title": "Test Feed",
                "site_url": "https://example.com",
                "feed_url": "https://example.com/feed.xml",
            },
            "status": "read",
            "starred": True,
            "published_at": "2024-10-24T12:30:00Z",
            "original_content": None,
        }
        entry = Entry.from_dict(data)
        assert entry.id == 5
        assert entry.title == "From Dict Entry"
        assert entry.status == "read"
        assert entry.starred is True
        assert entry.is_read is True
        assert entry.is_unread is False

    def test_entry_starred_property(self, sample_entry):
        """Test starred status of entry."""
        sample_entry.starred = True
        assert sample_entry.starred is True

        sample_entry.starred = False
        assert sample_entry.starred is False

    def test_entry_with_optional_content(self, sample_feed):
        """Test Entry with optional original_content."""
        entry = Entry(
            id=10,
            feed_id=1,
            title="Entry with Original",
            url="https://example.com/original",
            content="<p>Excerpt</p>",
            feed=sample_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 24, 12, 0, 0, tzinfo=UTC),
            original_content="<p>Full original content</p>",
        )
        assert entry.original_content == "<p>Full original content</p>"
