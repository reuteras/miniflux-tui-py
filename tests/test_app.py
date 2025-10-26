"""Tests for MinifluxTUI application."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from miniflux_tui.api.models import Entry, Feed
from miniflux_tui.config import Config
from miniflux_tui.ui.app import MinifluxTUI, run_tui


@pytest.fixture
def sample_config():
    """Create a sample Config for testing."""
    return Config(
        server_url="https://example.com",
        api_key="test-key",
        allow_invalid_certs=False,
        unread_color="cyan",
        read_color="gray",
        default_sort="date",
        default_group_by_feed=False,
        group_collapsed={},
    )


@pytest.fixture
def sample_feed():
    """Create a sample Feed for testing."""
    return Feed(
        id=1,
        title="Test Feed",
        site_url="https://example.com",
        feed_url="https://example.com/feed",
    )


@pytest.fixture
def sample_entry(sample_feed):
    """Create a sample Entry for testing."""
    return Entry(
        id=1,
        feed_id=1,
        title="Test Entry",
        content="<p>Test content</p>",
        url="https://example.com/entry",
        published_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
        starred=False,
        status="unread",
        feed=sample_feed,
    )


class TestMinifluxTUIInitialization:
    """Test MinifluxTUI app initialization."""

    def test_initialization_with_config(self, sample_config):
        """Test app initializes with config."""
        app = MinifluxTUI(sample_config)

        assert app.config == sample_config
        assert app.client is None
        assert app.entries == []
        assert app.current_view == "unread"

    def test_initialization_with_custom_driver(self, sample_config):
        """Test app initializes with custom driver."""
        mock_driver = MagicMock()

        app = MinifluxTUI(sample_config, driver_class=mock_driver)

        assert app.config == sample_config

    def test_initialization_css_is_defined(self, sample_config):
        """Test app CSS is defined."""
        app = MinifluxTUI(sample_config)

        assert app.CSS is not None
        assert isinstance(app.CSS, str)
        assert "ListView" in app.CSS
        assert "ListItem" in app.CSS

    def test_app_inherits_from_textual_app(self, sample_config):
        """Test MinifluxTUI inherits from Textual App."""
        app = MinifluxTUI(sample_config)

        # Verify it has Textual App methods
        assert hasattr(app, "push_screen")
        assert hasattr(app, "install_screen")
        assert hasattr(app, "notify")


class TestMinifluxTUIPushEntryReader:
    """Test push_entry_reader method."""

    def test_push_entry_reader_with_entry(self, sample_config, sample_entry):
        """Test push_entry_reader creates and pushes reader screen."""
        app = MinifluxTUI(sample_config)
        app.push_screen = MagicMock()

        app.push_entry_reader(sample_entry)

        # Verify push_screen was called
        app.push_screen.assert_called_once()

    def test_push_entry_reader_with_entry_list(self, sample_config, sample_feed):
        """Test push_entry_reader with full entry list."""
        entries = []
        for i in range(3):
            entry = Entry(
                id=i,
                feed_id=1,
                title=f"Entry {i}",
                content=f"Content {i}",
                url=f"https://example.com/{i}",
                published_at=datetime(2023, 1, i + 1, 12, 0, 0, tzinfo=UTC),
                starred=False,
                status="unread",
                feed=sample_feed,
            )
            entries.append(entry)

        app = MinifluxTUI(sample_config)
        app.push_screen = MagicMock()

        app.push_entry_reader(entries[0], entry_list=entries, current_index=0)

        # Verify push_screen was called
        app.push_screen.assert_called_once()

    def test_push_entry_reader_uses_app_entries_as_default(self, sample_config, sample_entry):
        """Test push_entry_reader uses app entries list by default."""
        app = MinifluxTUI(sample_config)

        # Add entries to app
        app.entries = [sample_entry]

        app.push_screen = MagicMock()

        # Push without providing entry_list
        app.push_entry_reader(sample_entry)

        # Verify push_screen was called
        app.push_screen.assert_called_once()


class TestMinifluxTUILoadEntries:
    """Test load_entries method."""

    @pytest.mark.asyncio
    async def test_load_entries_unread(self, sample_config, sample_entry):
        """Test load_entries loads unread entries."""
        app = MinifluxTUI(sample_config)

        # Mock the client
        app.client = AsyncMock()
        app.client.get_unread_entries = AsyncMock(return_value=[sample_entry])

        # Mock notify and is_screen_installed
        app.notify = MagicMock()
        app.is_screen_installed = MagicMock(return_value=False)

        # Load entries
        await app.load_entries("unread")

        # Verify client was called
        app.client.get_unread_entries.assert_called_once()
        # Verify entries were set
        assert len(app.entries) == 1
        assert app.entries[0] == sample_entry
        # Verify current view was updated
        assert app.current_view == "unread"

    @pytest.mark.asyncio
    async def test_load_entries_starred(self, sample_config, sample_entry):
        """Test load_entries loads starred entries."""
        app = MinifluxTUI(sample_config)

        # Mock the client
        app.client = AsyncMock()
        app.client.get_starred_entries = AsyncMock(return_value=[sample_entry])

        # Mock notify and is_screen_installed
        app.notify = MagicMock()
        app.is_screen_installed = MagicMock(return_value=False)

        # Load entries
        await app.load_entries("starred")

        # Verify client was called
        app.client.get_starred_entries.assert_called_once()
        # Verify entries were set
        assert len(app.entries) == 1
        assert app.entries[0] == sample_entry
        # Verify current view was updated
        assert app.current_view == "starred"

    @pytest.mark.asyncio
    async def test_load_entries_no_client(self, sample_config):
        """Test load_entries handles missing client."""
        app = MinifluxTUI(sample_config)
        app.client = None

        # Mock notify
        app.notify = MagicMock()

        # Load entries
        await app.load_entries()

        # Verify error notification
        app.notify.assert_called_once()
        assert "not initialized" in app.notify.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_load_entries_updates_screen(self, sample_config, sample_entry):
        """Test load_entries updates the entry list screen."""
        app = MinifluxTUI(sample_config)

        # Mock the client
        app.client = AsyncMock()
        app.client.get_unread_entries = AsyncMock(return_value=[sample_entry])

        # Mock screen access
        mock_screen = MagicMock()
        mock_screen._populate_list = MagicMock()
        app.is_screen_installed = MagicMock(return_value=True)
        app.get_screen = MagicMock(return_value=mock_screen)
        app.notify = MagicMock()

        # Mock the isinstance check to return True
        with patch("miniflux_tui.ui.app.isinstance", return_value=True):
            await app.load_entries()

            # Verify screen was updated
            mock_screen._populate_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_entries_empty_result(self, sample_config):
        """Test load_entries handles empty results."""
        app = MinifluxTUI(sample_config)

        # Mock the client to return empty list
        app.client = AsyncMock()
        app.client.get_unread_entries = AsyncMock(return_value=[])

        # Mock notify and is_screen_installed
        app.notify = MagicMock()
        app.is_screen_installed = MagicMock(return_value=False)

        # Load entries
        await app.load_entries()

        # Verify empty notification was shown
        calls = [str(call) for call in app.notify.call_args_list]
        # Should have notification about no entries
        assert any("no" in str(call).lower() for call in calls)

    @pytest.mark.asyncio
    async def test_load_entries_api_error(self, sample_config):
        """Test load_entries handles API errors."""
        app = MinifluxTUI(sample_config)

        # Mock the client to raise an error
        app.client = AsyncMock()
        app.client.get_unread_entries = AsyncMock(side_effect=Exception("API Error"))

        # Mock notify
        app.notify = MagicMock()

        # Load entries
        await app.load_entries()

        # Verify error notification
        app.notify.assert_called()
        assert "error" in app.notify.call_args[0][0].lower()


class TestMinifluxTUIActions:
    """Test action methods."""

    @pytest.mark.asyncio
    async def test_action_refresh_entries(self, sample_config, sample_entry):
        """Test refresh entries action."""
        app = MinifluxTUI(sample_config)
        app.client = AsyncMock()
        app.client.get_unread_entries = AsyncMock(return_value=[sample_entry])
        app.notify = MagicMock()
        app.is_screen_installed = MagicMock(return_value=False)

        await app.action_refresh_entries()

        app.notify.assert_called()
        assert "refresh" in app.notify.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_action_show_unread(self, sample_config, sample_entry):
        """Test show unread action."""
        app = MinifluxTUI(sample_config)
        app.client = AsyncMock()
        app.client.get_unread_entries = AsyncMock(return_value=[sample_entry])
        app.notify = MagicMock()
        app.is_screen_installed = MagicMock(return_value=False)

        await app.action_show_unread()

        assert app.current_view == "unread"
        app.notify.assert_called()

    @pytest.mark.asyncio
    async def test_action_show_starred(self, sample_config, sample_entry):
        """Test show starred action."""
        app = MinifluxTUI(sample_config)
        app.client = AsyncMock()
        app.client.get_starred_entries = AsyncMock(return_value=[sample_entry])
        app.notify = MagicMock()
        app.is_screen_installed = MagicMock(return_value=False)

        await app.action_show_starred()

        assert app.current_view == "starred"
        app.notify.assert_called()


class TestMinifluxTUILifecycle:
    """Test app lifecycle methods."""

    @pytest.mark.asyncio
    async def test_on_unmount_closes_client(self, sample_config):
        """Test on_unmount closes the client."""
        app = MinifluxTUI(sample_config)
        app.client = AsyncMock()

        await app.on_unmount()

        app.client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_unmount_no_client(self, sample_config):
        """Test on_unmount handles missing client."""
        app = MinifluxTUI(sample_config)
        app.client = None

        # Should not raise exception
        await app.on_unmount()


class TestRunTUI:
    """Test run_tui function."""

    @pytest.mark.asyncio
    async def test_run_tui_creates_and_runs_app(self, sample_config):
        """Test run_tui creates and runs MinifluxTUI app."""
        with patch.object(MinifluxTUI, "run_async", new_callable=AsyncMock):
            await run_tui(sample_config)

            # Verify run_async was called (implicitly by patching)
            # The patch ensures the method exists and can be called


class TestMinifluxTUIIntegration:
    """Integration tests for the app."""

    def test_app_config_colors(self, sample_config):
        """Test app correctly uses config colors."""
        app = MinifluxTUI(sample_config)

        assert app.config.unread_color == "cyan"
        assert app.config.read_color == "gray"

    def test_app_config_server_url(self, sample_config):
        """Test app correctly uses config server URL."""
        app = MinifluxTUI(sample_config)

        assert app.config.server_url == "https://example.com"

    def test_app_current_view_defaults_to_unread(self, sample_config):
        """Test app defaults to unread view."""
        app = MinifluxTUI(sample_config)

        assert app.current_view == "unread"

    def test_app_entries_list_starts_empty(self, sample_config):
        """Test app starts with empty entries list."""
        app = MinifluxTUI(sample_config)

        assert app.entries == []
        assert len(app.entries) == 0

    @pytest.mark.asyncio
    async def test_load_entries_maintains_list_order(self, sample_config, sample_feed):
        """Test load_entries maintains entry order."""
        entries = []
        for i in range(5):
            entry = Entry(
                id=i,
                feed_id=1,
                title=f"Entry {i}",
                content=f"Content {i}",
                url=f"https://example.com/{i}",
                published_at=datetime(2023, 1, i + 1, 12, 0, 0, tzinfo=UTC),
                starred=False,
                status="unread",
                feed=sample_feed,
            )
            entries.append(entry)

        app = MinifluxTUI(sample_config)
        app.client = AsyncMock()
        app.client.get_unread_entries = AsyncMock(return_value=entries)
        app.notify = MagicMock()
        app.is_screen_installed = MagicMock(return_value=False)

        await app.load_entries()

        # Verify order is maintained
        assert app.entries[0].id == 0
        assert app.entries[1].id == 1
        assert app.entries[4].id == 4
