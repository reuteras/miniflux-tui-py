"""Tests for Miniflux API client wrapper."""

from unittest.mock import MagicMock, patch

import pytest

from miniflux_tui.api.client import MinifluxClient


class TestMinifluxClientInit:
    """Test MinifluxClient initialization."""

    def test_init_basic(self):
        """Test basic client initialization."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base:
            client = MinifluxClient("http://localhost:8080", "test-key")
            assert client.base_url == "http://localhost:8080"
            assert client.allow_invalid_certs is False
            assert client.timeout == 30.0
            mock_base.assert_called_once_with("http://localhost:8080", api_key="test-key")

    def test_init_with_trailing_slash(self):
        """Test that trailing slash is removed from base_url."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080/", "test-key")
            assert client.base_url == "http://localhost:8080"

    def test_init_with_invalid_certs(self):
        """Test initialization with allow_invalid_certs."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key", allow_invalid_certs=True)
            assert client.allow_invalid_certs is True

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key", timeout=60.0)
            assert client.timeout == 60.0


class TestMinifluxClientContextManager:
    """Test MinifluxClient context manager functionality."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager entry and exit."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            async with MinifluxClient("http://localhost:8080", "test-key") as client:
                assert isinstance(client, MinifluxClient)

    @pytest.mark.asyncio
    async def test_close_method(self):
        """Test close method."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key")
            # Should not raise any exception
            await client.close()


class TestMinifluxClientRunSync:
    """Test _run_sync method."""

    @pytest.mark.asyncio
    async def test_run_sync_with_args(self):
        """Test _run_sync with positional arguments."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key")

            def sample_func(a, b):
                return a + b

            result = await client._run_sync(sample_func, 1, 2)
            assert result == 3

    @pytest.mark.asyncio
    async def test_run_sync_with_kwargs(self):
        """Test _run_sync with keyword arguments."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key")

            def sample_func(a=0, b=0):
                return a * b

            result = await client._run_sync(sample_func, a=3, b=4)
            assert result == 12


class TestMinifluxClientRetryLogic:
    """Test _call_with_retry method."""

    @pytest.mark.asyncio
    async def test_successful_call_on_first_try(self):
        """Test successful call without needing retries."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key")

            def success_func():
                return "success"

            result = await client._call_with_retry(success_func)
            assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """Test retry logic on connection error."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key")

            call_count = 0

            def failing_func():
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    error_msg = "Network error"
                    raise ConnectionError(error_msg)
                return "recovered"

            result = await client._call_with_retry(failing_func, max_retries=3, backoff_factor=0.01)
            assert result == "recovered"
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self):
        """Test that exception is raised after max retries."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key")

            def always_failing():
                error_msg = "Network error"
                raise ConnectionError(error_msg)

            with pytest.raises(ConnectionError, match="Network error"):
                await client._call_with_retry(always_failing, max_retries=2, backoff_factor=0.01)

    @pytest.mark.asyncio
    async def test_non_network_error_no_retry(self):
        """Test that non-network errors are not retried."""
        with patch("miniflux_tui.api.client.MinifluxClientBase"):
            client = MinifluxClient("http://localhost:8080", "test-key")

            call_count = 0

            def value_error_func():
                nonlocal call_count
                call_count += 1
                error_msg = "Invalid value"
                raise ValueError(error_msg)

            with pytest.raises(ValueError, match="Invalid value"):
                await client._call_with_retry(value_error_func, max_retries=3)

            # Should only be called once (no retries for non-network errors)
            assert call_count == 1


class TestMinifluxClientGetEntries:
    """Test entry retrieval methods."""

    @pytest.mark.asyncio
    async def test_get_unread_entries(self):
        """Test getting unread entries."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client

            # Mock the response
            mock_client.get_entries.return_value = {"entries": []}

            client = MinifluxClient("http://localhost:8080", "test-key")
            result = await client.get_unread_entries(limit=50, offset=0)

            assert result == []
            mock_client.get_entries.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_starred_entries(self):
        """Test getting starred entries."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client
            mock_client.get_entries.return_value = {"entries": []}

            client = MinifluxClient("http://localhost:8080", "test-key")
            result = await client.get_starred_entries(limit=30, offset=0)

            assert result == []
            mock_client.get_entries.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_entries_parsing(self):
        """Test entry parsing from API response."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client

            # Mock a real API response structure
            mock_client.get_entries.return_value = {
                "entries": [
                    {
                        "id": 1,
                        "feed_id": 1,
                        "title": "Test Entry",
                        "content": "Test content",
                        "url": "http://localhost:8080/entry",
                        "author": "Test Author",
                        "published_at": "2023-01-01T00:00:00Z",
                        "starred": False,
                        "status": "unread",
                        "feed": {
                            "id": 1,
                            "title": "Test Feed",
                            "site_url": "http://localhost:8080",
                            "feed_url": "http://localhost:8080/feed",
                        },
                    }
                ]
            }

            client = MinifluxClient("http://localhost:8080", "test-key")
            # Just verify the entry parsing logic works
            result = await client.get_unread_entries()

            # Entry.from_dict should be called and return Entry objects
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].title == "Test Entry"


class TestMinifluxClientActions:
    """Test entry action methods."""

    @pytest.mark.asyncio
    async def test_mark_as_read_calls_change_status(self):
        """Test marking entry as read delegates to change_entry_status."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client
            mock_client.update_entries.return_value = None

            client = MinifluxClient("http://localhost:8080", "test-key")
            # This should not raise
            await client.mark_as_read(123)

    @pytest.mark.asyncio
    async def test_mark_as_unread_calls_change_status(self):
        """Test marking entry as unread delegates to change_entry_status."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client
            mock_client.update_entries.return_value = None

            client = MinifluxClient("http://localhost:8080", "test-key")
            # This should not raise
            await client.mark_as_unread(123)

    @pytest.mark.asyncio
    async def test_toggle_starred(self):
        """Test toggling starred status."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client
            mock_client.toggle_bookmark.return_value = None

            client = MinifluxClient("http://localhost:8080", "test-key")
            # Should not raise
            await client.toggle_starred(123)

    @pytest.mark.asyncio
    async def test_save_entry(self):
        """Test saving entry."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client
            mock_client.save_entry.return_value = None

            client = MinifluxClient("http://localhost:8080", "test-key")
            # Should not raise
            await client.save_entry(123)

    @pytest.mark.asyncio
    async def test_mark_all_as_read(self):
        """Test marking multiple entries as read."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client
            mock_client.update_entries.return_value = None

            client = MinifluxClient("http://localhost:8080", "test-key")
            # Should not raise
            await client.mark_all_as_read([1, 2, 3])

    @pytest.mark.asyncio
    async def test_refresh_all_feeds(self):
        """Test refreshing all feeds."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client
            mock_client.refresh_all_feeds.return_value = None

            client = MinifluxClient("http://localhost:8080", "test-key")
            # Should not raise
            await client.refresh_all_feeds()

    @pytest.mark.asyncio
    async def test_fetch_original_content(self):
        """Test fetching original content."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client

            # Mock the response
            mock_client.fetch_entry_content.return_value = {"content": "<html>Original content</html>"}

            client = MinifluxClient("http://localhost:8080", "test-key")
            result = await client.fetch_original_content(123)

            # Result should be a string (possibly empty or content)
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_feeds_list_response(self):
        """Test getting feeds when API returns a list."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client

            # Mock the response as a list
            mock_client.get_feeds.return_value = [
                {
                    "id": 1,
                    "title": "Test Feed 1",
                    "site_url": "http://localhost:8080",
                    "feed_url": "http://localhost:8080/feed.xml",
                    "parsing_error_message": "",
                    "parsing_error_count": 0,
                    "disabled": False,
                },
                {
                    "id": 2,
                    "title": "Test Feed 2",
                    "site_url": "http://localhost:8081",
                    "feed_url": "http://localhost:8081/feed.xml",
                    "parsing_error_message": "SSL error",
                    "parsing_error_count": 3,
                    "disabled": True,
                },
            ]

            client = MinifluxClient("http://localhost:8080", "test-key")
            feeds = await client.get_feeds()

            # Verify we got Feed objects
            assert len(feeds) == 2
            assert feeds[0].id == 1
            assert feeds[0].title == "Test Feed 1"
            assert feeds[0].has_errors is False
            assert feeds[1].id == 2
            assert feeds[1].parsing_error_message == "SSL error"
            assert feeds[1].parsing_error_count == 3
            assert feeds[1].disabled is True
            assert feeds[1].has_errors is True

    @pytest.mark.asyncio
    async def test_get_feeds_dict_response(self):
        """Test getting feeds when API returns a dict with 'feeds' key."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client

            # Mock the response as a dict with 'feeds' key
            mock_client.get_feeds.return_value = {
                "feeds": [
                    {
                        "id": 10,
                        "title": "Feed from Dict",
                        "site_url": "http://localhost:8082",
                        "feed_url": "http://localhost:8082/feed.xml",
                        "parsing_error_message": "Timeout",
                        "parsing_error_count": 1,
                        "checked_at": "2024-10-24T12:00:00Z",
                        "disabled": False,
                    },
                ]
            }

            client = MinifluxClient("http://localhost:8080", "test-key")
            feeds = await client.get_feeds()

            # Verify we got Feed objects
            assert len(feeds) == 1
            assert feeds[0].id == 10
            assert feeds[0].title == "Feed from Dict"
            assert feeds[0].parsing_error_message == "Timeout"
            assert feeds[0].has_errors is True

    @pytest.mark.asyncio
    async def test_get_feeds_empty_list(self):
        """Test getting feeds when no feeds exist."""
        with patch("miniflux_tui.api.client.MinifluxClientBase") as mock_base_class:
            mock_client = MagicMock()
            mock_base_class.return_value = mock_client

            # Mock the response as empty list
            mock_client.get_feeds.return_value = []

            client = MinifluxClient("http://localhost:8080", "test-key")
            feeds = await client.get_feeds()

            # Verify we got empty list
            assert len(feeds) == 0
            assert isinstance(feeds, list)
