"""Pytest configuration and fixtures."""

from datetime import UTC, datetime

import pytest

from miniflux_tui.api.models import Entry, Feed


@pytest.fixture
def sample_feed():
    """Create a sample feed for testing."""
    return Feed(
        id=1,
        title="Example Feed",
        site_url="https://example.com",
        feed_url="https://example.com/feed.xml",
    )


@pytest.fixture
def sample_entry(sample_feed):
    """Create a sample entry for testing."""
    return Entry(
        id=1,
        feed_id=1,
        title="Sample Entry Title",
        url="https://example.com/article",
        content="<p>This is HTML content</p>",
        feed=sample_feed,
        status="unread",
        starred=False,
        published_at=datetime(2024, 10, 24, 12, 30, 0, tzinfo=UTC),
    )


@pytest.fixture
def sample_entries(sample_feed):
    """Create multiple sample entries for testing."""
    return [
        Entry(
            id=1,
            feed_id=1,
            title="Unread Entry 1",
            url="https://example.com/article1",
            content="<p>Content 1</p>",
            feed=sample_feed,
            status="unread",
            starred=False,
            published_at=datetime(2024, 10, 24, 12, 30, 0, tzinfo=UTC),
        ),
        Entry(
            id=2,
            feed_id=1,
            title="Read Entry 2",
            url="https://example.com/article2",
            content="<p>Content 2</p>",
            feed=sample_feed,
            status="read",
            starred=False,
            published_at=datetime(2024, 10, 23, 10, 15, 0, tzinfo=UTC),
        ),
        Entry(
            id=3,
            feed_id=1,
            title="Starred Unread Entry 3",
            url="https://example.com/article3",
            content="<p>Content 3</p>",
            feed=sample_feed,
            status="unread",
            starred=True,
            published_at=datetime(2024, 10, 22, 15, 45, 0, tzinfo=UTC),
        ),
        Entry(
            id=4,
            feed_id=1,
            title="Starred Read Entry 4",
            url="https://example.com/article4",
            content="<p>Content 4</p>",
            feed=sample_feed,
            status="read",
            starred=True,
            published_at=datetime(2024, 10, 21, 9, 0, 0, tzinfo=UTC),
        ),
    ]


@pytest.fixture
def valid_config_dict():
    """Create a valid configuration dictionary."""
    return {
        "server_url": "https://miniflux.example.com",
        "api_key": "1234567890abcdef",
        "allow_invalid_certs": False,
        "theme": {
            "unread_color": "cyan",
            "read_color": "gray",
        },
        "sorting": {
            "default_sort": "date",
            "default_group_by_feed": False,
            "group_collapsed": False,
        },
    }
