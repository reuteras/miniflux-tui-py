"""Tests for SettingsScreen."""

import re
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import urlparse

from textual.app import App

from miniflux_tui.ui.screens.settings_management import SettingsScreen


class SettingsTestApp(App):
    """Test app for SettingsScreen testing."""

    def __init__(self, **kwargs):
        """Initialize test app."""
        super().__init__(**kwargs)
        self.client = MagicMock()

    def on_mount(self) -> None:
        """Mount the settings screen."""
        self.push_screen(SettingsScreen())


class TestSettingsScreenInitialization:
    """Test SettingsScreen initialization."""

    def test_settings_screen_creation(self) -> None:
        """Test creating a SettingsScreen."""
        screen = SettingsScreen()
        assert screen.server_url == "Loading..."
        assert screen.username == "Loading..."
        assert screen.timezone == "Loading..."
        assert screen.language == "Loading..."
        assert screen.integrations_enabled is False

    def test_settings_screen_has_bindings(self) -> None:
        """Test that SettingsScreen has proper key bindings."""
        screen = SettingsScreen()
        binding_keys = [binding.key for binding in screen.BINDINGS]
        assert "escape" in binding_keys
        assert "q" in binding_keys
        assert "r" in binding_keys
        assert "o" in binding_keys


class TestSettingsScreenComposition:
    """Test SettingsScreen composition and rendering."""

    async def test_screen_composes_with_header_and_footer(self) -> None:
        """Test that SettingsScreen composes with header and footer."""
        app = SettingsTestApp()

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            assert isinstance(screen, SettingsScreen)
            assert screen._header_widget is not None
            assert screen._footer_widget is not None
            assert screen._scroll_container is not None

    async def test_screen_has_required_widgets(self) -> None:
        """Test that SettingsScreen has all required static widgets."""
        app = SettingsTestApp()

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            assert screen.query_one("#title")
            assert screen.query_one("#user-info")
            assert screen.query_one("#display-prefs")
            assert screen.query_one("#integrations-status")


class TestSettingsScreenLoadSettings:
    """Test SettingsScreen settings loading."""

    async def test_load_settings_success(self) -> None:
        """Test successful settings loading."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(
            return_value={
                "username": "testuser",
                "timezone": "America/New_York",
                "language": "en_US",
            }
        )
        app.client.get_integrations_status = AsyncMock(return_value=True)

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            await screen._load_settings()

            assert screen.server_url == "https://miniflux.example.com"
            assert screen.username == "testuser"
            assert screen.timezone == "America/New_York"
            assert screen.language == "en_US"
            assert screen.integrations_enabled is True

    async def test_load_settings_no_client(self) -> None:
        """Test loading settings when client is not available."""
        app = SettingsTestApp()
        app.client = None  # type: ignore[assignment]

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            await screen._load_settings()

            # Should handle gracefully
            user_info = screen.query_one("#user-info")
            assert "API client not available" in user_info.render().plain  # type: ignore[attr-defined]

    async def test_load_settings_api_error(self) -> None:
        """Test handling API errors during settings load."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(side_effect=Exception("Network error"))

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            await screen._load_settings()

            # Should show error state
            user_info = screen.query_one("#user-info")
            assert "Error" in user_info.render().plain  # type: ignore[attr-defined]

    async def test_load_settings_missing_user_data(self) -> None:
        """Test loading settings with incomplete user data."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(return_value={})
        app.client.get_integrations_status = AsyncMock(return_value=False)

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            await screen._load_settings()

            # Should handle missing fields with defaults
            assert screen.username == "unknown"
            assert screen.timezone == "unknown"
            assert screen.language == "unknown"


class TestSettingsScreenDisplay:
    """Test SettingsScreen display updates."""

    async def test_update_user_info_display(self) -> None:
        """Test updating user information display."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(
            return_value={
                "username": "john",
                "timezone": "UTC",
                "language": "en_US",
            }
        )
        app.client.get_integrations_status = AsyncMock(return_value=False)

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            await screen._load_settings()

            user_info = screen.query_one("#user-info")
            content = user_info.render().plain  # type: ignore[attr-defined]
            assert "john" in content
            # Extract and parse URL to ensure it's exactly "https://miniflux.example.com"
            urls = re.findall(r"https?://[^\s,]+", content)
            assert any(urlparse(url).netloc == "miniflux.example.com" and urlparse(url).scheme == "https" for url in urls)

    async def test_update_display_preferences(self) -> None:
        """Test updating display preferences."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(
            return_value={
                "username": "john",
                "timezone": "Europe/Paris",
                "language": "fr_FR",
            }
        )
        app.client.get_integrations_status = AsyncMock(return_value=False)

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            await screen._load_settings()

            display_prefs = screen.query_one("#display-prefs")
            content = display_prefs.render().plain  # type: ignore[attr-defined]
            assert "Europe/Paris" in content
            assert "fr_FR" in content

    async def test_update_integrations_enabled(self) -> None:
        """Test displaying integrations when enabled."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(return_value={"username": "john", "timezone": "UTC", "language": "en_US"})
        app.client.get_integrations_status = AsyncMock(return_value=True)

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            await screen._load_settings()

            integrations = screen.query_one("#integrations-status")
            content = integrations.render().plain  # type: ignore[attr-defined]
            assert "enabled" in content.lower()

    async def test_update_integrations_disabled(self) -> None:
        """Test displaying integrations when disabled."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(return_value={"username": "john", "timezone": "UTC", "language": "en_US"})
        app.client.get_integrations_status = AsyncMock(return_value=False)

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            await screen._load_settings()

            integrations = screen.query_one("#integrations-status")
            content = integrations.render().plain  # type: ignore[attr-defined]
            assert "No integrations enabled" in content


class TestSettingsScreenActions:
    """Test SettingsScreen actions."""

    async def test_action_close(self) -> None:
        """Test closing the settings screen."""
        app = SettingsTestApp()

        async with app.run_test() as pilot:
            screen = cast(SettingsScreen, app.screen)
            assert isinstance(screen, SettingsScreen)

            # Close the screen
            await pilot.press("escape")
            await pilot.pause()

            # Should return to previous screen
            assert app.screen is not screen

    async def test_action_close_with_q(self) -> None:
        """Test closing with 'q' key."""
        app = SettingsTestApp()

        async with app.run_test() as pilot:
            screen = cast(SettingsScreen, app.screen)
            await pilot.press("q")
            await pilot.pause()
            assert app.screen is not screen

    async def test_action_refresh(self) -> None:
        """Test refreshing settings."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(
            return_value={
                "username": "testuser",
                "timezone": "UTC",
                "language": "en_US",
            }
        )
        app.client.get_integrations_status = AsyncMock(return_value=False)

        async with app.run_test() as pilot:
            screen = cast(SettingsScreen, app.screen)

            # Initial load
            await pilot.pause()
            assert screen.username == "testuser"

            # Change the mock return value
            app.client.get_user_info = AsyncMock(
                return_value={
                    "username": "newuser",
                    "timezone": "America/New_York",
                    "language": "en_US",
                }
            )

            # Refresh
            await pilot.press("r")
            await pilot.pause()

            # Should have new data
            assert screen.username == "newuser"
            assert screen.timezone == "America/New_York"

    async def test_action_open_web_settings(self) -> None:
        """Test opening web settings notification."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(return_value={"username": "john", "timezone": "UTC", "language": "en_US"})
        app.client.get_integrations_status = AsyncMock(return_value=False)

        async with app.run_test() as pilot:
            screen = cast(SettingsScreen, app.screen)
            await pilot.pause()

            # Open web settings
            await pilot.press("o")
            await pilot.pause()

            # Check notification was shown (this is implementation dependent)
            # We can't easily verify the notification, but we can verify the action runs
            assert screen.server_url == "https://miniflux.example.com"

    async def test_action_open_web_settings_no_url(self) -> None:
        """Test opening web settings when URL not loaded."""
        app = SettingsTestApp()
        app.client = None  # type: ignore[assignment]

        async with app.run_test() as pilot:
            screen = cast(SettingsScreen, app.screen)
            await pilot.pause()

            # Try to open web settings
            await pilot.press("o")
            await pilot.pause()

            # Should handle gracefully
            assert screen.server_url == "Loading..."


class TestSettingsScreenErrorHandling:
    """Test SettingsScreen error handling."""

    async def test_update_error_state(self) -> None:
        """Test updating display when error occurs."""
        app = SettingsTestApp()

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)
            screen._update_error_state("Test error message")

            user_info = screen.query_one("#user-info")
            assert "Test error message" in user_info.render().plain  # type: ignore[attr-defined]

    async def test_update_display_widget_not_found(self) -> None:
        """Test graceful handling when widget not found."""
        app = SettingsTestApp()

        async with app.run_test():
            screen = cast(SettingsScreen, app.screen)

            # Try to update before widgets are ready (should not crash)
            with patch.object(screen, "query_one", side_effect=Exception("Widget not found")):
                screen._update_user_info()
                screen._update_display_preferences()
                screen._update_integrations()
                # Should not raise exception


class TestSettingsScreenAPIIntegration:
    """Test SettingsScreen API integration."""

    async def test_calls_get_user_info(self) -> None:
        """Test that screen calls get_user_info API."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(return_value={"username": "test", "timezone": "UTC", "language": "en_US"})
        app.client.get_integrations_status = AsyncMock(return_value=False)

        async with app.run_test():
            # on_mount calls _load_settings automatically
            app.client.get_user_info.assert_called()
            assert app.client.get_user_info.call_count >= 1

    async def test_calls_get_integrations_status(self) -> None:
        """Test that screen calls get_integrations_status API."""
        app = SettingsTestApp()
        app.client.base_url = "https://miniflux.example.com"
        app.client.get_user_info = AsyncMock(return_value={"username": "test", "timezone": "UTC", "language": "en_US"})
        app.client.get_integrations_status = AsyncMock(return_value=True)

        async with app.run_test():
            # on_mount calls _load_settings automatically
            app.client.get_integrations_status.assert_called()
            assert app.client.get_integrations_status.call_count >= 1
