"""Tests for utility functions."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from miniflux_tui.utils import api_call, get_star_icon, get_status_icon


class TestGetStarIcon:
    """Test get_star_icon function."""

    def test_starred_returns_filled_star(self):
        """Test that starred=True returns filled star."""
        assert get_star_icon(True) == "★"

    def test_unstarred_returns_empty_star(self):
        """Test that starred=False returns empty star."""
        assert get_star_icon(False) == "☆"

    def test_star_icons_are_different(self):
        """Test that filled and empty stars are different."""
        filled = get_star_icon(True)
        empty = get_star_icon(False)
        assert filled != empty


class TestGetStatusIcon:
    """Test get_status_icon function."""

    def test_unread_returns_filled_circle(self):
        """Test that is_unread=True returns filled circle."""
        assert get_status_icon(True) == "●"

    def test_read_returns_empty_circle(self):
        """Test that is_unread=False returns empty circle."""
        assert get_status_icon(False) == "○"

    def test_status_icons_are_different(self):
        """Test that filled and empty circles are different."""
        unread = get_status_icon(True)
        read = get_status_icon(False)
        assert unread != read


class TestApiCallContextManager:
    """Test api_call async context manager."""

    @pytest.mark.asyncio
    async def test_api_call_yields_client(self):
        """Test that api_call context manager yields the client."""
        # Create mock screen and app
        mock_client = AsyncMock()
        mock_app = MagicMock()
        mock_app.client = mock_client

        mock_screen = MagicMock()
        mock_screen.app = mock_app
        mock_screen.notify = MagicMock()
        mock_screen.log = MagicMock()

        # Use context manager
        async with api_call(mock_screen, "test operation") as client:
            assert client is mock_client

    @pytest.mark.asyncio
    async def test_api_call_handles_connection_error(self):
        """Test that api_call handles ConnectionError."""
        # Create mock screen and app
        mock_client = AsyncMock()
        mock_app = MagicMock()
        mock_app.client = mock_client

        mock_screen = MagicMock()
        mock_screen.app = mock_app
        mock_screen.notify = MagicMock()
        mock_screen.log = MagicMock()

        # Test that ConnectionError is caught and handled
        error_msg = "Network failed"
        async with api_call(mock_screen, "test operation") as _:
            raise ConnectionError(error_msg)

        # Verify error was logged
        mock_screen.notify.assert_called()
        assert "Connection failed" in mock_screen.notify.call_args[0][0]

    @pytest.mark.asyncio
    async def test_api_call_handles_timeout_error(self):
        """Test that api_call handles TimeoutError."""
        # Create mock screen and app
        mock_client = AsyncMock()
        mock_app = MagicMock()
        mock_app.client = mock_client

        mock_screen = MagicMock()
        mock_screen.app = mock_app
        mock_screen.notify = MagicMock()
        mock_screen.log = MagicMock()

        # Test that TimeoutError is caught and handled
        error_msg = "Request timed out"
        async with api_call(mock_screen, "test operation") as _:
            raise TimeoutError(error_msg)

        # Verify error was logged
        mock_screen.notify.assert_called()
        assert "timeout" in mock_screen.notify.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_api_call_handles_value_error(self):
        """Test that api_call handles ValueError."""
        # Create mock screen and app
        mock_client = AsyncMock()
        mock_app = MagicMock()
        mock_app.client = mock_client

        mock_screen = MagicMock()
        mock_screen.app = mock_app
        mock_screen.notify = MagicMock()
        mock_screen.log = MagicMock()

        # Test that ValueError is caught and handled
        error_msg = "Invalid input"
        async with api_call(mock_screen, "test operation") as _:
            raise ValueError(error_msg)

        # Verify error was logged
        mock_screen.notify.assert_called()
        assert "Invalid input" in mock_screen.notify.call_args[0][0]

    @pytest.mark.asyncio
    async def test_api_call_handles_generic_exception(self):
        """Test that api_call handles generic Exception."""
        # Create mock screen and app
        mock_client = AsyncMock()
        mock_app = MagicMock()
        mock_app.client = mock_client

        mock_screen = MagicMock()
        mock_screen.app = mock_app
        mock_screen.notify = MagicMock()
        mock_screen.log = MagicMock()

        # Test that generic Exception is caught and handled
        error_msg = "Some error"
        async with api_call(mock_screen, "test operation") as _:
            raise Exception(error_msg)

        # Verify error was logged
        mock_screen.notify.assert_called()

    @pytest.mark.asyncio
    async def test_api_call_no_client_available(self):
        """Test that api_call handles missing client by notifying user."""
        # Create mock screen without client
        mock_screen = MagicMock()
        mock_screen.app = MagicMock()
        # Don't set app.client
        if hasattr(mock_screen.app, "client"):
            delattr(mock_screen.app, "client")
        mock_screen.notify = MagicMock()

        # The context manager returns early without yielding when client is unavailable
        # This is the expected behavior - it prevents operations when client is not available
        with pytest.raises(RuntimeError, match="generator didn't yield"):
            async with api_call(mock_screen, "test operation") as _:
                pytest.fail("Should not reach here when client is unavailable")

        # Verify that the user was notified
        mock_screen.notify.assert_called()
        assert "not available" in mock_screen.notify.call_args[0][0]
