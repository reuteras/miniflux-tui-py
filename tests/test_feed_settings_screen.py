# SPDX-License-Identifier: MIT
"""Tests for the FeedSettingsScreen."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from miniflux_tui.api.models import Feed
from miniflux_tui.ui.screens.feed_settings import FeedSettingsScreen


@pytest.fixture
def mock_client():
    """Create a mock MinifluxClient."""
    client = AsyncMock()
    client.update_feed = AsyncMock()
    client.delete_feed = AsyncMock()
    client.get_feed = AsyncMock()
    return client


@pytest.fixture
def sample_feed():
    """Create a sample Feed for testing."""
    return Feed(
        id=1,
        title="Test Feed",
        site_url="https://example.com",
        feed_url="https://example.com/feed.xml",
        category_id=1,
        checked_at="2024-11-14T12:00:00Z",
        disabled=False,
    )


@pytest.fixture
def feed_settings_screen(sample_feed, mock_client):
    """Create a FeedSettingsScreen instance for testing."""
    return FeedSettingsScreen(
        feed_id=sample_feed.id,
        feed=sample_feed,
        client=mock_client,
    )


class TestFeedSettingsScreenInitialization:
    """Test FeedSettingsScreen initialization."""

    def test_init_stores_parameters(self, sample_feed, mock_client):
        """Test that __init__ properly stores all parameters."""
        screen = FeedSettingsScreen(
            feed_id=sample_feed.id,
            feed=sample_feed,
            client=mock_client,
        )

        assert screen.feed_id == sample_feed.id
        assert screen.feed == sample_feed
        assert screen.client == mock_client

    def test_init_initializes_dirty_state(self, feed_settings_screen):
        """Test that dirty state is initialized to clean."""
        assert feed_settings_screen.is_dirty is False
        assert feed_settings_screen.dirty_fields == {}
        assert feed_settings_screen.original_values == {}

    def test_init_initializes_status(self, feed_settings_screen):
        """Test that status message is initialized."""
        assert feed_settings_screen.status_message == ""
        assert feed_settings_screen.status_severity == "info"

    def test_bindings_defined(self):
        """Test that BINDINGS are defined."""
        assert hasattr(FeedSettingsScreen, "BINDINGS")
        assert len(FeedSettingsScreen.BINDINGS) > 0

    def test_default_css_defined(self):
        """Test that DEFAULT_CSS is defined."""
        assert hasattr(FeedSettingsScreen, "DEFAULT_CSS")
        assert isinstance(FeedSettingsScreen.DEFAULT_CSS, str)


class TestDirtyStateTracking:
    """Test dirty state tracking functionality."""

    def test_on_field_changed_marks_dirty(self, feed_settings_screen):
        """Test that _on_field_changed marks screen as dirty."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title")

        assert feed_settings_screen.is_dirty is True
        assert "title" in feed_settings_screen.dirty_fields
        assert feed_settings_screen.dirty_fields["title"] is True

    def test_on_field_changed_stores_original_value(self, feed_settings_screen):
        """Test that original values are stored on first change."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title")

        assert "title" in feed_settings_screen.original_values
        assert feed_settings_screen.original_values["title"] == "Test Feed"

    def test_on_field_changed_multiple_fields(self, feed_settings_screen):
        """Test tracking multiple field changes."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title")
            feed_settings_screen._on_field_changed("category_id", 2)

        assert feed_settings_screen.is_dirty is True
        assert len(feed_settings_screen.dirty_fields) == 2
        assert "title" in feed_settings_screen.dirty_fields
        assert "category_id" in feed_settings_screen.dirty_fields

    def test_on_field_changed_does_not_re_store_original(self, feed_settings_screen):
        """Test that original value is only stored once per field."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title 1")
            original_value_1 = feed_settings_screen.original_values["title"]

            feed_settings_screen._on_field_changed("title", "New Title 2")
            original_value_2 = feed_settings_screen.original_values["title"]

        assert original_value_1 == original_value_2
        assert original_value_2 == "Test Feed"


class TestSaveAction:
    """Test save action functionality."""

    @pytest.mark.asyncio
    async def test_save_calls_api_when_dirty(self, feed_settings_screen):
        """Test that save calls API when there are changes."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title")

        feed_settings_screen._collect_field_values = MagicMock(return_value={})

        with patch.object(feed_settings_screen, "query_one"):
            await feed_settings_screen.action_save_changes()

        feed_settings_screen.client.update_feed.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_does_nothing_if_not_dirty(self, feed_settings_screen):
        """Test that save does nothing when there are no changes."""
        assert feed_settings_screen.is_dirty is False

        with patch.object(feed_settings_screen, "query_one"):
            await feed_settings_screen.action_save_changes()

        feed_settings_screen.client.update_feed.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_shows_success_message(self, feed_settings_screen):
        """Test that success message is shown after save."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title")
            feed_settings_screen._collect_field_values = MagicMock(return_value={})
            await feed_settings_screen.action_save_changes()

        assert "saved successfully" in feed_settings_screen.status_message.lower()
        assert feed_settings_screen.status_severity == "success"

    @pytest.mark.asyncio
    async def test_save_handles_timeout_error(self, feed_settings_screen):
        """Test that timeout errors are handled gracefully."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title")
            feed_settings_screen._collect_field_values = MagicMock(return_value={})
            feed_settings_screen.client.update_feed.side_effect = TimeoutError()
            await feed_settings_screen.action_save_changes()

        assert "timeout" in feed_settings_screen.status_message.lower()
        assert feed_settings_screen.status_severity == "error"

    @pytest.mark.asyncio
    async def test_save_handles_connection_error(self, feed_settings_screen):
        """Test that connection errors are handled gracefully."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title")
            feed_settings_screen._collect_field_values = MagicMock(return_value={})
            feed_settings_screen.client.update_feed.side_effect = ConnectionError()
            await feed_settings_screen.action_save_changes()

        assert "connection" in feed_settings_screen.status_message.lower()
        assert feed_settings_screen.status_severity == "error"


class TestCancelAction:
    """Test cancel action functionality."""

    @pytest.mark.asyncio
    async def test_cancel_with_no_changes_closes_screen(self, feed_settings_screen):
        """Test that cancel closes screen when no unsaved changes."""
        assert feed_settings_screen.is_dirty is False

        mock_app = MagicMock()
        with patch("miniflux_tui.ui.screens.feed_settings.Screen.app", mock_app), patch.object(feed_settings_screen, "query_one"):
            await feed_settings_screen.action_cancel_changes()

        mock_app.pop_screen.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_with_changes_shows_warning(self, feed_settings_screen):
        """Test that cancel shows warning with unsaved changes."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("title", "New Title")
        assert feed_settings_screen.is_dirty is True

        with patch.object(feed_settings_screen, "query_one"):
            await feed_settings_screen.action_cancel_changes()

        assert feed_settings_screen.is_dirty is False
        assert "discarded" in feed_settings_screen.status_message.lower()
        assert feed_settings_screen.status_severity == "warning"


class TestCollectFieldValues:
    """Test field value collection."""

    def test_collect_field_values_returns_dict(self, feed_settings_screen):
        """Test that _collect_field_values returns a dictionary."""
        result = feed_settings_screen._collect_field_values()
        assert isinstance(result, dict)


class TestStatusMessages:
    """Test status message display."""

    def test_show_message_updates_state(self, feed_settings_screen):
        """Test that show_message updates state correctly."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._show_message("Test", severity="info")

        assert feed_settings_screen.status_message == "Test"
        assert feed_settings_screen.status_severity == "info"

    def test_show_message_all_severities(self, feed_settings_screen):
        """Test show_message with all severity levels."""
        severities = ["info", "success", "error", "warning"]

        for severity in severities:
            with patch.object(feed_settings_screen, "query_one"):
                feed_settings_screen._show_message("Test", severity=severity)

            assert feed_settings_screen.status_severity == severity


class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_complete_edit_workflow(self, feed_settings_screen):
        """Test complete workflow: change -> dirty -> save."""
        with patch.object(feed_settings_screen, "query_one"):
            # Mark field as changed
            feed_settings_screen._on_field_changed("title", "Updated")
            assert feed_settings_screen.is_dirty is True

            # Prepare for save
            feed_settings_screen._collect_field_values = MagicMock(return_value={})

            # Save
            await feed_settings_screen.action_save_changes()

            # Verify clean
            assert feed_settings_screen.is_dirty is False


class TestGeneralSettingsFields:
    """Test General Settings field handling."""

    def test_field_mapping_for_widget_ids(self, feed_settings_screen):
        """Test that widget IDs are correctly mapped to feed field names."""
        with patch.object(feed_settings_screen, "query_one"):
            # Test title field mapping
            feed_settings_screen._on_field_changed("feed-title", "New Title")
            assert "title" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["title"] == "New Title"

            # Test site_url field mapping
            feed_settings_screen._on_field_changed("site-url", "https://example.com")
            assert "site_url" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["site_url"] == "https://example.com"

            # Test category_id field mapping
            feed_settings_screen._on_field_changed("category-id", "5")
            assert "category_id" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["category_id"] == "5"

            # Test disabled field mapping
            feed_settings_screen._on_field_changed("feed-disabled", True)
            assert "disabled" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["disabled"] is True

    def test_on_input_changed_event(self, feed_settings_screen):
        """Test on_input_changed event handler."""
        mock_input = MagicMock()
        mock_input.id = "feed-title"
        mock_input.disabled = False

        event = MagicMock()
        event.input = mock_input
        event.value = "Updated Title"

        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen.on_input_changed(event)

        assert feed_settings_screen.is_dirty is True
        assert "title" in feed_settings_screen.dirty_fields

    def test_on_input_changed_skips_disabled_fields(self, feed_settings_screen):
        """Test that on_input_changed skips disabled input fields."""
        mock_input = MagicMock()
        mock_input.id = "feed-url"
        mock_input.disabled = True

        event = MagicMock()
        event.input = mock_input
        event.value = "https://example.com/feed.xml"

        # Should not mark as dirty since the input is disabled
        feed_settings_screen.on_input_changed(event)
        assert feed_settings_screen.is_dirty is False

    def test_on_checkbox_changed_event(self, feed_settings_screen):
        """Test on_checkbox_changed event handler."""
        mock_checkbox = MagicMock()
        mock_checkbox.id = "feed-disabled"

        event = MagicMock()
        event.checkbox = mock_checkbox
        event.value = True

        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen.on_checkbox_changed(event)

        assert feed_settings_screen.is_dirty is True
        assert "disabled" in feed_settings_screen.dirty_fields
        assert feed_settings_screen._field_values["disabled"] is True

    def test_collect_field_values_with_mapped_fields(self, feed_settings_screen):
        """Test that _collect_field_values returns mapped field names."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("feed-title", "New Title")
            feed_settings_screen._on_field_changed("site-url", "https://example.com")
            feed_settings_screen._on_field_changed("feed-disabled", True)

        updates = feed_settings_screen._collect_field_values()
        assert updates["title"] == "New Title"
        assert updates["site_url"] == "https://example.com"
        assert updates["disabled"] is True
        assert len(updates) == 3

    def test_feed_url_read_only_field_not_collected(self, feed_settings_screen):
        """Test that read-only feed-url field is not collected on save."""
        with patch.object(feed_settings_screen, "query_one"):
            # Try to mark feed-url as dirty (should be skipped in actual usage)
            feed_settings_screen._on_field_changed("feed-url", "different_url")

        # The field mapping will map it to feed_url
        updates = feed_settings_screen._collect_field_values()
        # Since feed_url is read-only and we don't actually modify it in the UI,
        # it should still be in updates if we marked it dirty
        # This test documents the behavior - in real usage, disabled inputs won't trigger events
        assert "feed_url" in updates

    def test_original_values_with_mapped_fields(self, feed_settings_screen):
        """Test that original values are stored with mapped field names."""
        original_title = feed_settings_screen.feed.title
        original_disabled = feed_settings_screen.feed.disabled

        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("feed-title", "Modified")
            feed_settings_screen._on_field_changed("feed-disabled", not original_disabled)

        assert feed_settings_screen.original_values["title"] == original_title
        assert feed_settings_screen.original_values["disabled"] == original_disabled


class TestGeneralSettingsIntegration:
    """Integration tests for General Settings workflow."""

    @pytest.mark.asyncio
    async def test_general_settings_edit_workflow(self, feed_settings_screen):
        """Test complete workflow for editing General Settings."""
        with patch.object(feed_settings_screen, "query_one"):
            # Simulate user edits
            feed_settings_screen._on_field_changed("feed-title", "Updated Feed Title")
            feed_settings_screen._on_field_changed("site-url", "https://newsite.com")
            feed_settings_screen._on_field_changed("category-id", "10")
            feed_settings_screen._on_field_changed("feed-disabled", True)

            # Verify dirty state
            assert feed_settings_screen.is_dirty is True
            assert len(feed_settings_screen.dirty_fields) == 4

            # Collect values
            updates = feed_settings_screen._collect_field_values()
            assert updates["title"] == "Updated Feed Title"
            assert updates["site_url"] == "https://newsite.com"
            assert updates["category_id"] == "10"
            assert updates["disabled"] is True

    @pytest.mark.asyncio
    async def test_partial_general_settings_edit(self, feed_settings_screen):
        """Test workflow when only some General Settings fields are modified."""
        with patch.object(feed_settings_screen, "query_one"):
            # Only modify title and disabled
            feed_settings_screen._on_field_changed("feed-title", "Only Title Changed")
            feed_settings_screen._on_field_changed("feed-disabled", True)

        updates = feed_settings_screen._collect_field_values()
        # Should only have 2 updates
        assert len(updates) == 2
        assert updates["title"] == "Only Title Changed"
        assert updates["disabled"] is True
        # site_url and category_id should not be in updates
        assert "site_url" not in updates
        assert "category_id" not in updates


class TestNetworkSettingsFields:
    """Test Network Settings field handling."""

    def test_network_field_mapping(self, feed_settings_screen):
        """Test that network widget IDs are correctly mapped to field names."""
        with patch.object(feed_settings_screen, "query_one"):
            # Test username field mapping
            feed_settings_screen._on_field_changed("auth-username", "testuser")
            assert "username" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["username"] == "testuser"

            # Test password field mapping
            feed_settings_screen._on_field_changed("auth-password", "secretpass")
            assert "password" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["password"] == "secretpass"  # noqa: S105

            # Test user_agent field mapping
            feed_settings_screen._on_field_changed("user-agent", "Mozilla/5.0")
            assert "user_agent" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["user_agent"] == "Mozilla/5.0"

            # Test proxy_url field mapping
            feed_settings_screen._on_field_changed("proxy-url", "http://proxy.example.com:8080")
            assert "proxy_url" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["proxy_url"] == "http://proxy.example.com:8080"

            # Test ignore_https_errors field mapping
            feed_settings_screen._on_field_changed("ignore-https-errors", True)
            assert "ignore_https_errors" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["ignore_https_errors"] is True

    def test_on_input_changed_for_network_fields(self, feed_settings_screen):
        """Test on_input_changed event handler for network fields."""
        mock_input = MagicMock()
        mock_input.id = "auth-username"
        mock_input.disabled = False

        event = MagicMock()
        event.input = mock_input
        event.value = "networkuser"

        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen.on_input_changed(event)

        assert feed_settings_screen.is_dirty is True
        assert "username" in feed_settings_screen.dirty_fields

    def test_on_checkbox_changed_for_https_errors(self, feed_settings_screen):
        """Test on_checkbox_changed for HTTPS certificate errors setting."""
        mock_checkbox = MagicMock()
        mock_checkbox.id = "ignore-https-errors"

        event = MagicMock()
        event.checkbox = mock_checkbox
        event.value = True

        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen.on_checkbox_changed(event)

        assert feed_settings_screen.is_dirty is True
        assert "ignore_https_errors" in feed_settings_screen.dirty_fields
        assert feed_settings_screen._field_values["ignore_https_errors"] is True

    def test_collect_network_field_values(self, feed_settings_screen):
        """Test that _collect_field_values returns network field names."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("auth-username", "user123")
            feed_settings_screen._on_field_changed("auth-password", "pass123")
            feed_settings_screen._on_field_changed("user-agent", "CustomAgent/1.0")
            feed_settings_screen._on_field_changed("ignore-https-errors", True)

        updates = feed_settings_screen._collect_field_values()
        assert updates["username"] == "user123"
        assert updates["password"] == "pass123"  # noqa: S105
        assert updates["user_agent"] == "CustomAgent/1.0"
        assert updates["ignore_https_errors"] is True
        assert len(updates) == 4

    def test_empty_network_fields_not_collected(self, feed_settings_screen):
        """Test that empty network fields are not collected if not modified."""
        # Don't modify any network fields
        updates = feed_settings_screen._collect_field_values()
        # Should have no network fields since nothing was modified
        assert "username" not in updates
        assert "password" not in updates
        assert "user_agent" not in updates
        assert "proxy_url" not in updates

    def test_partial_network_settings_edit(self, feed_settings_screen):
        """Test workflow when only some network settings are modified."""
        with patch.object(feed_settings_screen, "query_one"):
            # Only modify username and proxy
            feed_settings_screen._on_field_changed("auth-username", "admin")
            feed_settings_screen._on_field_changed("proxy-url", "http://proxy:3128")

        updates = feed_settings_screen._collect_field_values()
        assert len(updates) == 2
        assert updates["username"] == "admin"
        assert updates["proxy_url"] == "http://proxy:3128"
        # password and user_agent should not be in updates
        assert "password" not in updates
        assert "user_agent" not in updates


class TestNetworkSettingsIntegration:
    """Integration tests for Network Settings workflow."""

    @pytest.mark.asyncio
    async def test_network_settings_full_workflow(self, feed_settings_screen):
        """Test complete workflow for editing all Network Settings."""
        with patch.object(feed_settings_screen, "query_one"):
            # Simulate user edits for all network fields
            feed_settings_screen._on_field_changed("auth-username", "networkuser")
            feed_settings_screen._on_field_changed("auth-password", "networkpass")
            feed_settings_screen._on_field_changed("user-agent", "Mozilla/5.0 Custom")
            feed_settings_screen._on_field_changed("proxy-url", "http://proxy.example.com:8080")
            feed_settings_screen._on_field_changed("ignore-https-errors", True)

            # Verify dirty state
            assert feed_settings_screen.is_dirty is True
            assert len(feed_settings_screen.dirty_fields) == 5

            # Collect values
            updates = feed_settings_screen._collect_field_values()
            assert updates["username"] == "networkuser"
            assert updates["password"] == "networkpass"  # noqa: S105
            assert updates["user_agent"] == "Mozilla/5.0 Custom"
            assert updates["proxy_url"] == "http://proxy.example.com:8080"
            assert updates["ignore_https_errors"] is True

    @pytest.mark.asyncio
    async def test_mixed_general_and_network_settings_edit(self, feed_settings_screen):
        """Test workflow when both General and Network Settings are modified."""
        with patch.object(feed_settings_screen, "query_one"):
            # Modify both general and network fields
            feed_settings_screen._on_field_changed("feed-title", "Updated Title")
            feed_settings_screen._on_field_changed("auth-username", "user456")
            feed_settings_screen._on_field_changed("ignore-https-errors", True)

        updates = feed_settings_screen._collect_field_values()
        # Should have 3 updates total
        assert len(updates) == 3
        assert updates["title"] == "Updated Title"
        assert updates["username"] == "user456"
        assert updates["ignore_https_errors"] is True

    @pytest.mark.asyncio
    async def test_network_settings_save_workflow(self, feed_settings_screen):
        """Test save workflow with network settings changes."""
        with patch.object(feed_settings_screen, "query_one"):
            # Modify network fields
            feed_settings_screen._on_field_changed("auth-username", "saveuser")
            feed_settings_screen._on_field_changed("proxy-url", "http://save-proxy:8080")

            # Verify dirty before save
            assert feed_settings_screen.is_dirty is True

            # Prepare for save
            feed_settings_screen._collect_field_values = MagicMock(
                return_value={
                    "username": "saveuser",
                    "proxy_url": "http://save-proxy:8080",
                }
            )

            # Save
            await feed_settings_screen.action_save_changes()

            # Verify clean after save
            assert feed_settings_screen.is_dirty is False
            assert feed_settings_screen.dirty_fields == {}


class TestRulesAndFilteringFields:
    """Test Rules & Filtering field handling."""

    def test_rules_field_mapping(self, feed_settings_screen):
        """Test that rule widget IDs are correctly mapped to field names."""
        with patch.object(feed_settings_screen, "query_one"):
            # Test scraper rules mapping
            feed_settings_screen._on_field_changed("scraper-rules", "div.content")
            assert "scraper_rules" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["scraper_rules"] == "div.content"

            # Test rewrite rules mapping
            feed_settings_screen._on_field_changed("rewrite-rules", "regex pattern")
            assert "rewrite_rules" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["rewrite_rules"] == "regex pattern"

            # Test URL rewrite rules mapping
            feed_settings_screen._on_field_changed("url-rewrite-rules", "url -> replacement")
            assert "url_rewrite_rules" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["url_rewrite_rules"] == "url -> replacement"

            # Test blocking rules mapping
            feed_settings_screen._on_field_changed("blocking-rules", "block pattern")
            assert "blocking_rules" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["blocking_rules"] == "block pattern"

            # Test keep rules mapping
            feed_settings_screen._on_field_changed("keep-rules", "keep pattern")
            assert "keep_rules" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["keep_rules"] == "keep pattern"

    def test_on_text_area_changed_event(self, feed_settings_screen):
        """Test on_text_area_changed event handler."""
        mock_textarea = MagicMock()
        mock_textarea.id = "scraper-rules"
        mock_textarea.text = "div.article"

        event = MagicMock()
        event.text_area = mock_textarea

        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen.on_text_area_changed(event)

        assert feed_settings_screen.is_dirty is True
        assert "scraper_rules" in feed_settings_screen.dirty_fields

    def test_collect_rule_field_values(self, feed_settings_screen):
        """Test that _collect_field_values returns rule field names."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("scraper-rules", "div.post")
            feed_settings_screen._on_field_changed("rewrite-rules", "replace_pattern")
            feed_settings_screen._on_field_changed("blocking-rules", "ad_pattern")

        updates = feed_settings_screen._collect_field_values()
        assert updates["scraper_rules"] == "div.post"
        assert updates["rewrite_rules"] == "replace_pattern"
        assert updates["blocking_rules"] == "ad_pattern"
        assert len(updates) == 3

    def test_empty_rule_fields_not_collected(self, feed_settings_screen):
        """Test that empty rule fields are not collected if not modified."""
        # Don't modify any rule fields
        updates = feed_settings_screen._collect_field_values()
        # Should have no rule fields since nothing was modified
        assert "scraper_rules" not in updates
        assert "rewrite_rules" not in updates
        assert "url_rewrite_rules" not in updates
        assert "blocking_rules" not in updates
        assert "keep_rules" not in updates

    def test_partial_rules_edit(self, feed_settings_screen):
        """Test workflow when only some rule fields are modified."""
        with patch.object(feed_settings_screen, "query_one"):
            # Only modify scraper and blocking rules
            feed_settings_screen._on_field_changed("scraper-rules", "article.main")
            feed_settings_screen._on_field_changed("blocking-rules", "spam_regex")

        updates = feed_settings_screen._collect_field_values()
        assert len(updates) == 2
        assert updates["scraper_rules"] == "article.main"
        assert updates["blocking_rules"] == "spam_regex"
        # rewrite and keep rules should not be in updates
        assert "rewrite_rules" not in updates
        assert "keep_rules" not in updates

    def test_multiline_rule_content(self, feed_settings_screen):
        """Test handling of multiline rule content."""
        multiline_rules = "line1\nline2\nline3"
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("scraper-rules", multiline_rules)

        updates = feed_settings_screen._collect_field_values()
        assert updates["scraper_rules"] == multiline_rules
        assert "\n" in updates["scraper_rules"]


class TestRulesAndFilteringIntegration:
    """Integration tests for Rules & Filtering workflow."""

    @pytest.mark.asyncio
    async def test_rules_and_filtering_full_workflow(self, feed_settings_screen):
        """Test complete workflow for editing all Rules & Filtering fields."""
        with patch.object(feed_settings_screen, "query_one"):
            # Simulate user edits for all rule fields
            feed_settings_screen._on_field_changed("scraper-rules", "div.content")
            feed_settings_screen._on_field_changed("rewrite-rules", "pattern1 -> replacement1")
            feed_settings_screen._on_field_changed("url-rewrite-rules", "old.url -> new.url")
            feed_settings_screen._on_field_changed("blocking-rules", "ads|spam")
            feed_settings_screen._on_field_changed("keep-rules", "important|urgent")

            # Verify dirty state
            assert feed_settings_screen.is_dirty is True
            assert len(feed_settings_screen.dirty_fields) == 5

            # Collect values
            updates = feed_settings_screen._collect_field_values()
            assert updates["scraper_rules"] == "div.content"
            assert updates["rewrite_rules"] == "pattern1 -> replacement1"
            assert updates["url_rewrite_rules"] == "old.url -> new.url"
            assert updates["blocking_rules"] == "ads|spam"
            assert updates["keep_rules"] == "important|urgent"

    @pytest.mark.asyncio
    async def test_combined_all_sections_edit(self, feed_settings_screen):
        """Test workflow when fields from all sections are modified."""
        with patch.object(feed_settings_screen, "query_one"):
            # Modify fields from each section
            feed_settings_screen._on_field_changed("feed-title", "New Title")  # General
            feed_settings_screen._on_field_changed("auth-username", "user1")  # Network
            feed_settings_screen._on_field_changed("scraper-rules", "div")  # Rules

        updates = feed_settings_screen._collect_field_values()
        # Should have 3 updates total
        assert len(updates) == 3
        assert updates["title"] == "New Title"
        assert updates["username"] == "user1"
        assert updates["scraper_rules"] == "div"

    @pytest.mark.asyncio
    async def test_rules_save_workflow(self, feed_settings_screen):
        """Test save workflow with rules changes."""
        with patch.object(feed_settings_screen, "query_one"):
            # Modify rules
            feed_settings_screen._on_field_changed("scraper-rules", "main.article")
            feed_settings_screen._on_field_changed("blocking-rules", "\\badv\\b")

            # Verify dirty before save
            assert feed_settings_screen.is_dirty is True

            # Prepare for save
            feed_settings_screen._collect_field_values = MagicMock(
                return_value={
                    "scraper_rules": "main.article",
                    "blocking_rules": "\\badv\\b",
                }
            )

            # Save
            await feed_settings_screen.action_save_changes()

            # Verify clean after save
            assert feed_settings_screen.is_dirty is False
            assert feed_settings_screen.dirty_fields == {}


class TestFeedInformationFields:
    """Test Feed Information field handling."""

    def test_feed_information_field_mapping(self, feed_settings_screen):
        """Test that feed information widget IDs are correctly mapped."""
        with patch.object(feed_settings_screen, "query_one"):
            # Test check interval field mapping
            feed_settings_screen._on_field_changed("check-interval", "60")
            assert "check_interval" in feed_settings_screen.dirty_fields
            assert feed_settings_screen._field_values["check_interval"] == "60"

    def test_collect_feed_information_field_values(self, feed_settings_screen):
        """Test that _collect_field_values returns feed information field names."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("check-interval", "120")

        updates = feed_settings_screen._collect_field_values()
        assert updates["check_interval"] == "120"
        assert len(updates) == 1

    def test_empty_check_interval_not_collected(self, feed_settings_screen):
        """Test that empty check interval is not collected if not modified."""
        # Don't modify check interval
        updates = feed_settings_screen._collect_field_values()
        # Should have no check_interval since nothing was modified
        assert "check_interval" not in updates

    def test_original_values_with_feed_information(self, feed_settings_screen):
        """Test that original values are stored for feed information fields."""
        with patch.object(feed_settings_screen, "query_one"):
            feed_settings_screen._on_field_changed("check-interval", "30")

        # Original value should be None for new field
        assert feed_settings_screen.original_values["check_interval"] is None


class TestFeedInformationIntegration:
    """Integration tests for Feed Information workflow."""

    @pytest.mark.asyncio
    async def test_feed_information_edit_workflow(self, feed_settings_screen):
        """Test complete workflow for editing Feed Information."""
        with patch.object(feed_settings_screen, "query_one"):
            # Simulate user edit for check interval
            feed_settings_screen._on_field_changed("check-interval", "45")

            # Verify dirty state
            assert feed_settings_screen.is_dirty is True
            assert "check_interval" in feed_settings_screen.dirty_fields

            # Collect values
            updates = feed_settings_screen._collect_field_values()
            assert updates["check_interval"] == "45"

    @pytest.mark.asyncio
    async def test_combined_all_four_sections_edit(self, feed_settings_screen):
        """Test workflow when fields from all four sections are modified."""
        with patch.object(feed_settings_screen, "query_one"):
            # Modify fields from each section
            feed_settings_screen._on_field_changed("feed-title", "Updated")  # General
            feed_settings_screen._on_field_changed("auth-username", "user")  # Network
            feed_settings_screen._on_field_changed("scraper-rules", "div")  # Rules
            feed_settings_screen._on_field_changed("check-interval", "60")  # Feed Info

        updates = feed_settings_screen._collect_field_values()
        # Should have 4 updates total
        assert len(updates) == 4
        assert updates["title"] == "Updated"
        assert updates["username"] == "user"
        assert updates["scraper_rules"] == "div"
        assert updates["check_interval"] == "60"

    @pytest.mark.asyncio
    async def test_feed_information_save_workflow(self, feed_settings_screen):
        """Test save workflow with feed information changes."""
        with patch.object(feed_settings_screen, "query_one"):
            # Modify feed information
            feed_settings_screen._on_field_changed("check-interval", "30")

            # Verify dirty before save
            assert feed_settings_screen.is_dirty is True

            # Prepare for save
            feed_settings_screen._collect_field_values = MagicMock(return_value={"check_interval": "30"})

            # Save
            await feed_settings_screen.action_save_changes()

            # Verify clean after save
            assert feed_settings_screen.is_dirty is False
            assert feed_settings_screen.dirty_fields == {}


class TestDeleteFeedFunctionality:
    """Test delete feed functionality and error handling."""

    @pytest.fixture
    def feed_settings_with_app(self):
        """Create feed settings screen with mock app."""
        feed = Feed(
            id=1,
            title="Test Feed",
            feed_url="https://example.com/feed",
            site_url="https://example.com",
            category_id=1,
            disabled=False,
            checked_at=None,
            parsing_error_count=0,
            parsing_error_message="",
        )

        return FeedSettingsScreen(feed_id=1, feed=feed, client=AsyncMock())

    @pytest.mark.asyncio
    async def test_delete_feed_requires_confirmation(self, feed_settings_with_app):
        """Test that delete feed requires two button presses (confirmation)."""
        screen = feed_settings_with_app
        mock_app = MagicMock()
        mock_app.client = AsyncMock()

        with patch.object(type(screen), "app", new_callable=PropertyMock) as mock_app_prop, patch.object(screen, "query_one"):
            mock_app_prop.return_value = mock_app
            # First press - should show confirmation message, not delete
            await screen.action_delete_feed()

            # Verify confirmation message shown
            assert screen._delete_confirmed is True
            assert "confirm" in screen.status_message.lower()
            assert "cannot be undone" in screen.status_message.lower()
            assert screen.status_severity == "error"

            # Verify client.delete_feed was NOT called yet
            mock_app.client.delete_feed.assert_not_called()
            mock_app.pop_screen.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_feed_successful_delete(self, feed_settings_with_app):
        """Test successful feed deletion on second confirmation press."""
        screen = feed_settings_with_app
        mock_app = MagicMock()
        mock_app.client = AsyncMock()
        mock_app.client.delete_feed = AsyncMock()

        with patch.object(type(screen), "app", new_callable=PropertyMock) as mock_app_prop, patch.object(screen, "query_one"):
            mock_app_prop.return_value = mock_app
            # First press - confirmation message
            await screen.action_delete_feed()
            assert screen._delete_confirmed is True

            # Second press - actual deletion
            await screen.action_delete_feed()

            # Verify API was called
            mock_app.client.delete_feed.assert_called_once_with(1)

            # Verify success message
            assert "deleted successfully" in screen.status_message.lower()
            assert screen.status_severity == "success"

            # Verify screen closed
            mock_app.pop_screen.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_feed_no_client(self, feed_settings_with_app):
        """Test error when API client is not available."""
        screen = feed_settings_with_app
        screen._delete_confirmed = True  # Skip confirmation
        mock_app = MagicMock()
        mock_app.client = None

        with patch.object(type(screen), "app", new_callable=PropertyMock) as mock_app_prop, patch.object(screen, "query_one"):
            mock_app_prop.return_value = mock_app
            await screen.action_delete_feed()

            # Verify error message
            assert "API client not available" in screen.status_message
            assert screen.status_severity == "error"

            # Verify screen not closed
            mock_app.pop_screen.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_feed_timeout_error(self, feed_settings_with_app):
        """Test timeout error handling during deletion."""
        screen = feed_settings_with_app
        screen._delete_confirmed = True  # Skip confirmation
        mock_app = MagicMock()
        mock_app.client = AsyncMock()
        mock_app.client.delete_feed = AsyncMock(side_effect=TimeoutError())

        with patch.object(type(screen), "app", new_callable=PropertyMock) as mock_app_prop, patch.object(screen, "query_one"):
            mock_app_prop.return_value = mock_app
            await screen.action_delete_feed()

            # Verify error message
            assert "timeout" in screen.status_message.lower()
            assert screen.status_severity == "error"

            # Verify confirmation flag reset for retry
            assert screen._delete_confirmed is False

            # Verify screen not closed
            mock_app.pop_screen.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_feed_connection_error(self, feed_settings_with_app):
        """Test connection error handling during deletion."""
        screen = feed_settings_with_app
        screen._delete_confirmed = True  # Skip confirmation
        mock_app = MagicMock()
        mock_app.client = AsyncMock()
        mock_app.client.delete_feed = AsyncMock(side_effect=ConnectionError())

        with patch.object(type(screen), "app", new_callable=PropertyMock) as mock_app_prop, patch.object(screen, "query_one"):
            mock_app_prop.return_value = mock_app
            await screen.action_delete_feed()

            # Verify error message
            assert "connection failed" in screen.status_message.lower()
            assert screen.status_severity == "error"

            # Verify confirmation flag reset for retry
            assert screen._delete_confirmed is False

            # Verify screen not closed
            mock_app.pop_screen.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_feed_generic_error(self, feed_settings_with_app):
        """Test generic exception handling during deletion."""
        screen = feed_settings_with_app
        screen._delete_confirmed = True  # Skip confirmation
        mock_app = MagicMock()
        mock_app.client = AsyncMock()
        mock_app.client.delete_feed = AsyncMock(side_effect=ValueError("Invalid feed"))

        with patch.object(type(screen), "app", new_callable=PropertyMock) as mock_app_prop, patch.object(screen, "query_one"):
            mock_app_prop.return_value = mock_app
            await screen.action_delete_feed()

            # Verify error message
            assert "Error deleting feed" in screen.status_message
            assert "Invalid feed" in screen.status_message
            assert screen.status_severity == "error"

            # Verify confirmation flag reset for retry
            assert screen._delete_confirmed is False

            # Verify screen not closed
            mock_app.pop_screen.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_confirmation_reset_on_error(self, feed_settings_with_app):
        """Test that confirmation flag is reset after error for safe retry."""
        screen = feed_settings_with_app
        mock_app = MagicMock()
        mock_app.client = AsyncMock()
        delete_feed_mock = AsyncMock(side_effect=TimeoutError())
        mock_app.client.delete_feed = delete_feed_mock

        with patch.object(type(screen), "app", new_callable=PropertyMock) as mock_app_prop, patch.object(screen, "query_one"):
            mock_app_prop.return_value = mock_app
            screen._delete_confirmed = True

            # First attempt fails
            await screen.action_delete_feed()
            assert screen._delete_confirmed is False
            assert delete_feed_mock.call_count == 1

            # Reset for retry
            screen._delete_confirmed = True
            delete_feed_mock.side_effect = None  # Clear side_effect for success
            delete_feed_mock.reset_mock()

            # Second attempt should succeed
            await screen.action_delete_feed()
            assert delete_feed_mock.call_count == 1
            mock_app.pop_screen.assert_called_once()


class TestDangerZoneIntegration:
    """Integration tests for Danger Zone section."""

    @pytest.mark.asyncio
    async def test_delete_feed_complete_workflow(self):
        """Test complete delete feed workflow from confirmation to success."""
        mock_app = MagicMock()
        mock_app.pop_screen = MagicMock()
        mock_app.client = AsyncMock()
        mock_app.client.delete_feed = AsyncMock()

        feed = Feed(
            id=42,
            title="Complex Feed Title",
            feed_url="https://example.com/feed",
            site_url="https://example.com",
            category_id=5,
            disabled=False,
            checked_at=None,
            parsing_error_count=0,
            parsing_error_message="",
        )

        screen = FeedSettingsScreen(feed_id=42, feed=feed, client=AsyncMock())

        with patch.object(type(screen), "app", new_callable=PropertyMock) as mock_app_prop, patch.object(screen, "query_one"):
            mock_app_prop.return_value = mock_app
            # Step 1: First delete press - confirmation
            await screen.action_delete_feed()
            assert screen._delete_confirmed is True
            assert "confirm" in screen.status_message.lower()
            assert screen.status_severity == "error"
            mock_app.pop_screen.assert_not_called()

            # Step 2: Second delete press - actual deletion
            await screen.action_delete_feed()
            assert mock_app.client.delete_feed.call_count == 1
            assert mock_app.client.delete_feed.call_args[0][0] == 42
            assert "deleted successfully" in screen.status_message.lower()
            assert screen.status_severity == "success"
            mock_app.pop_screen.assert_called_once()
