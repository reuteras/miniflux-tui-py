# SPDX-License-Identifier: MIT
"""Feed settings screen for comprehensive feed configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Static, TextArea

from miniflux_tui.docs_cache import DocsCache
from miniflux_tui.form_persistence_manager import FormPersistenceManager
from miniflux_tui.ui.screens.rules_helper import RulesHelperScreen

if TYPE_CHECKING:
    from miniflux_tui.api.client import MinifluxClient
    from miniflux_tui.api.models import Feed


class FeedSettingsScreen(Screen):
    """Full-screen scrollable feed settings interface.

    Provides centralized management of feed configuration including:
    - General settings (title, category, site URL, description)
    - Network settings (authentication, proxies, certificates)
    - Rules and filtering (scraper, rewrite, blocking rules)
    - Feed metadata (last check, next check, ETag, LastModified)
    - Feed management (delete)

    Attributes:
        feed_id: ID of the feed being configured
        feed: Current feed data
        client: Miniflux API client
        dirty_fields: Dictionary tracking which fields have been modified
        is_dirty: Boolean flag indicating if any changes have been made
    """

    BINDINGS: ClassVar = [
        Binding("tab", "focus_next", "Next Field"),
        Binding("shift+tab", "focus_previous", "Prev Field"),
        Binding("enter", "save_changes", "Save", key_display="Enter"),
        Binding("escape", "cancel_changes", "Cancel"),
        Binding("x", "open_helper", "Helper"),
    ]

    DEFAULT_CSS: ClassVar[str] = """
    FeedSettingsScreen {
        background: $surface;
        color: $text;
        layout: vertical;
    }

    FeedSettingsScreen > Header {
        dock: top;
    }

    FeedSettingsScreen > Footer {
        dock: bottom;
    }

    FeedSettingsScreen > VerticalScroll {
        height: 1fr;
        width: 100%;
        overflow: auto y;
    }

    FeedSettingsScreen > #bottom-section {
        height: auto;
        width: 100%;
        layout: vertical;
    }

    #bottom-section > #status-message {
        height: auto;
        width: 100%;
        padding: 1 2;
        border-top: solid $primary 30%;
    }

    #bottom-section > #button-container {
        height: auto;
        width: 100%;
        padding: 1 2;
        layout: horizontal;
    }

    #settings-header {
        width: 100%;
        height: auto;
        padding: 2 2;
        background: $boost;
        border-bottom: solid $primary 50%;
        content-align: left middle;
        text-style: bold;
        color: $text;
    }

    #unsaved-indicator {
        width: 100%;
        height: auto;
        padding: 0 2;
        margin-bottom: 1;
        color: $warning;
        text-style: dim;
    }

    .section {
        width: 100%;
        height: auto;
        padding: 2 2;
        margin-bottom: 2;
        border-bottom: solid $primary 30%;
    }

    .section-title {
        width: 100%;
        height: auto;
        padding: 1 0;
        padding-bottom: 1;
        text-style: bold;
        color: $accent;
        border-bottom: solid $primary 20%;
        margin-bottom: 1;
    }

    .field-group {
        width: 100%;
        height: auto;
        margin-bottom: 2;
        padding: 0 0;
    }

    .field-label {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        color: $text-muted;
        text-style: dim;
    }

    .field-value {
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
    }

    .textarea-container {
        width: 100%;
        height: 8;
        border: solid $primary 50%;
    }

    TextArea {
        width: 100%;
        height: 100%;
        min-height: 8;
    }

    #status-message {
        width: 100%;
        height: auto;
        padding: 1 2;
        color: $text-muted;
        min-height: 1;
    }

    #status-message.success {
        color: $success;
        text-style: bold;
    }

    #status-message.error {
        color: $error;
        text-style: bold;
    }

    #status-message.warning {
        color: $warning;
        text-style: bold;
    }

    #status-message.info {
        color: $text;
    }

    #button-container Button {
        margin-right: 2;
        min-width: 20;
    }

    .danger-button {
        background: $error;
        color: $text;
    }

    .danger-button:hover {
        background: $error 80%;
    }
    """

    def __init__(
        self,
        feed_id: int,
        feed: Feed,
        client: MinifluxClient,
        **kwargs,
    ):
        """Initialize the feed settings screen.

        Args:
            feed_id: ID of the feed to configure
            feed: Current feed data
            client: Miniflux API client for API calls
            **kwargs: Additional keyword arguments for Screen
        """
        super().__init__(**kwargs)
        self.feed_id = feed_id
        self.feed = feed
        self.client = client

        # Documentation cache for helper screens
        self.docs_cache = DocsCache()

        # Form persistence and auto-recovery
        self.persistence = FormPersistenceManager()

        # Dirty state tracking
        self.dirty_fields: dict[str, bool] = {}
        self.is_dirty = False

        # Store original values for cancel
        self.original_values: dict[str, Any] = {}

        # Status message
        self.status_message = ""
        self.status_severity = "info"  # "info", "success", "error", "warning"

        # Auto-save debounce timer
        self._auto_save_handle = None

    def compose(self) -> ComposeResult:
        """Compose the feed settings screen layout.

        Yields:
            Composed widgets for the screen
        """
        yield Header()

        with VerticalScroll(id="settings-scroll"):
            # Settings header with unsaved indicator
            yield Static(
                f"Feed Settings: {self.feed.title}",
                id="settings-header",
            )
            yield Static("", id="unsaved-indicator", classes="field-label")

            # Yield each section
            yield from self._compose_general_settings()
            yield from self._compose_network_settings()
            yield from self._compose_rules_and_filtering()
            yield from self._compose_feed_information()
            yield from self._compose_danger_zone()

        # Bottom container for status message and buttons
        with Static(id="bottom-section"):
            # Status message area
            yield Static(self.status_message, id="status-message")

            # Button container
            with Static(id="button-container"):
                yield Button("Save", id="save-button", disabled=True)
                yield Button("Cancel", id="cancel-button")

        yield Footer()

    def _compose_general_settings(self) -> ComposeResult:
        """Compose the General Settings section."""
        yield Static("General Settings", classes="section-title")
        with Static(classes="section"):
            # Feed Title
            yield Static("Title", classes="field-label")
            yield Input(
                value=self.feed.title,
                id="feed-title",
                classes="field-value",
            )

            # Site URL
            yield Static("Site URL", classes="field-label")
            yield Input(
                value=self.feed.site_url,
                id="site-url",
                classes="field-value",
            )

            # Feed URL (read-only)
            yield Static("Feed URL", classes="field-label")
            yield Input(
                value=self.feed.feed_url,
                id="feed-url",
                disabled=True,
                classes="field-value",
            )

            # Category ID
            yield Static("Category", classes="field-label")
            yield Input(
                value=str(self.feed.category_id or ""),
                id="category-id",
                classes="field-value",
            )

            # Disabled checkbox
            yield Static("Disabled", classes="field-label")
            yield Checkbox(
                label="Disable this feed",
                value=self.feed.disabled,
                id="feed-disabled",
                classes="field-value",
            )

    def _compose_network_settings(self) -> ComposeResult:
        """Compose the Network Settings section."""
        yield Static("Network Settings", classes="section-title")
        with Static(classes="section"):
            # Username
            yield Static("Username (optional)", classes="field-label")
            yield Input(
                value="",
                id="auth-username",
                classes="field-value",
            )

            # Password
            yield Static("Password (optional)", classes="field-label")
            yield Input(
                value="",
                id="auth-password",
                password=True,
                classes="field-value",
            )

            # User-Agent
            yield Static("User-Agent (optional)", classes="field-label")
            yield Input(
                value="",
                id="user-agent",
                classes="field-value",
            )

            # Proxy URL
            yield Static("Proxy URL (optional)", classes="field-label")
            yield Input(
                value="",
                id="proxy-url",
                classes="field-value",
            )

            # Ignore HTTPS errors
            yield Static("HTTPS Settings", classes="field-label")
            yield Checkbox(
                label="Ignore HTTPS certificate errors",
                value=False,
                id="ignore-https-errors",
                classes="field-value",
            )

    def _compose_rules_and_filtering(self) -> ComposeResult:
        """Compose the Rules & Filtering section."""
        yield Static("Rules & Filtering", classes="section-title")
        with Static(classes="section"):
            # Scraper Rules
            yield Static("Scraper Rules (optional)", classes="field-label")
            with Container(classes="textarea-container"):
                yield TextArea(text="", id="scraper-rules")

            # Rewrite Rules
            yield Static("Rewrite Rules (optional)", classes="field-label")
            with Container(classes="textarea-container"):
                yield TextArea(text="", id="rewrite-rules")

            # URL Rewrite Rules
            yield Static("URL Rewrite Rules (optional)", classes="field-label")
            with Container(classes="textarea-container"):
                yield TextArea(text="", id="url-rewrite-rules")

            # Blocking Rules
            yield Static("Blocking Rules (optional)", classes="field-label")
            with Container(classes="textarea-container"):
                yield TextArea(text="", id="blocking-rules")

            # Keep Rules
            yield Static("Keep Rules (optional)", classes="field-label")
            with Container(classes="textarea-container"):
                yield TextArea(text="", id="keep-rules")

    def _compose_feed_information(self) -> ComposeResult:
        """Compose the Feed Information section."""
        yield Static("Feed Information", classes="section-title")
        with Static(classes="section"):
            # Last Checked
            yield Static("Last Checked", classes="field-label")
            yield Static(
                self.feed.checked_at or "Never",
                id="last-checked",
                classes="field-value",
            )

            # Parsing Error Count
            yield Static("Parsing Errors", classes="field-label")
            yield Static(
                f"{self.feed.parsing_error_count} error(s)",
                id="error-count",
                classes="field-value",
            )

            # Parsing Error Message (if present)
            if self.feed.parsing_error_message:
                yield Static("Error Message", classes="field-label")
                yield Static(
                    self.feed.parsing_error_message,
                    id="error-message",
                    classes="field-value",
                )

            # Check Interval
            yield Static("Check Interval (minutes, optional)", classes="field-label")
            yield Input(
                value="",
                id="check-interval",
                classes="field-value",
            )

            # Feed ID (read-only for reference)
            yield Static("Feed ID", classes="field-label")
            yield Static(
                str(self.feed.id),
                id="feed-id",
                classes="field-value",
            )

    def _compose_danger_zone(self) -> ComposeResult:
        """Compose the Danger Zone section."""
        yield Static("Danger Zone", classes="section-title")
        with Static(classes="section"):
            yield Static(
                "Delete this feed permanently. This action cannot be undone.",
                classes="field-label",
            )
            yield Button(
                "🗑️ Delete Feed",
                id="delete-feed-button",
                classes="danger-button",
            )

    def on_mount(self) -> None:
        """Called when screen is mounted.

        Initialize screen state, check for recovery, and load feed data.
        """
        # Store original field values for change tracking
        self._store_original_values()

        # Check for recovery from previous session
        self._check_for_recovery()

        # Focus on first focusable element
        self.query_one("Button#save-button", expect_type=Button)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes.

        Args:
            event: Input change event
        """
        if event.input.id and not event.input.disabled:
            self._on_field_changed(event.input.id, event.value)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox state changes.

        Args:
            event: Checkbox change event
        """
        if event.checkbox.id:
            self._on_field_changed(event.checkbox.id, event.value)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area content changes.

        Args:
            event: TextArea change event
        """
        if event.text_area.id:
            self._on_field_changed(event.text_area.id, event.text_area.text)

    async def action_focus_next(self) -> None:
        """Focus next focusable widget."""
        self.screen.focus_next()

    async def action_focus_previous(self) -> None:
        """Focus previous focusable widget."""
        self.screen.focus_previous()

    async def action_save_changes(self) -> None:
        """Save all changes to Miniflux API.

        This action:
        1. Collects all modified field values
        2. Shows loading indicator
        3. Calls the API to update the feed
        4. Clears persistence state on success
        5. Shows success/error message with visual feedback
        """
        if not self.is_dirty:
            self._show_message("No changes to save", severity="info")
            return

        # Disable save button and show loading message
        save_button = self.query_one("Button#save-button", expect_type=Button)
        save_button.disabled = True
        self._show_message("💾 Saving feed settings...", severity="info")

        try:
            # Collect field values
            updates = self._collect_field_values()

            # Call API to update feed
            updated_feed = await self.client.update_feed(self.feed_id, **updates)

            # Update internal state
            self.feed = updated_feed
            self.is_dirty = False
            self.dirty_fields.clear()
            self.original_values.clear()

            # Clear persistence state after successful save
            self.persistence.clear_session(self.feed_id)

            # Clear unsaved indicator
            self._update_unsaved_indicator()

            # Show success message with confirmation
            self._show_message(
                "✓ Feed settings saved successfully",
                severity="success",
            )

        except TimeoutError:
            self._show_message("✗ Request timeout while saving", severity="error")
            save_button.disabled = False
        except ConnectionError:
            self._show_message("✗ Connection failed while saving", severity="error")
            save_button.disabled = False
        except ValueError as e:
            self._show_message(f"✗ Invalid input: {e}", severity="error")
            save_button.disabled = False
        except Exception as e:
            self._show_message(f"✗ Error saving settings: {e}", severity="error")
            save_button.disabled = False

    async def action_cancel_changes(self) -> None:
        """Cancel changes and close screen.

        If there are unsaved changes, show confirmation message.
        Otherwise, close immediately.
        """
        if self.is_dirty:
            # Show confirmation message
            if not hasattr(self, "_cancel_confirmed"):
                self._cancel_confirmed = False

            if not self._cancel_confirmed:
                # First press - show confirmation
                self._show_message(
                    "Press Escape again to discard unsaved changes",
                    severity="warning",
                )
                self._cancel_confirmed = True
                return

            # Second press - discard changes and close
            self.is_dirty = False
            self.dirty_fields.clear()
            self.persistence.discard_recovery(self.feed_id)
            self._cancel_confirmed = False
            self._update_unsaved_indicator()

        # Close the screen
        self.app.pop_screen()

    def action_open_helper(self) -> None:
        """Open helper screen for current field.

        This action opens appropriate helper screens based on
        which rule field is currently focused (if any).
        """
        # Map of rule field IDs to rule types
        rule_field_mapping = {
            "scraper-rules": "scraper_rules",
            "rewrite-rules": "rewrite_rules",
            "url-rewrite-rules": "url_rewrite_rules",
            "blocking-rules": "blocking_rules",
            "keep-rules": "keep_rules",
        }

        # Get currently focused widget
        focused = self.focused
        if focused is None:
            self._show_message(
                "No field focused. Focus a rule field and press 'x' for help.",
                severity="info",
            )
            return

        # Check if the focused widget or its parent is a rule field
        widget = focused
        rule_type = None

        # Check the focused widget itself
        if widget.id and widget.id in rule_field_mapping:
            rule_type = rule_field_mapping[widget.id]
        else:
            # Check parent widgets
            parent = widget.parent
            while parent and not rule_type:
                if parent.id and parent.id in rule_field_mapping:
                    rule_type = rule_field_mapping[parent.id]
                    break
                parent = parent.parent

        if not rule_type:
            self._show_message(
                "Focus a rule field to see help. Rule fields: Scraper, Rewrite, URL Rewrite, Blocking, Keep.",
                severity="info",
            )
            return

        # Open the helper screen with the appropriate rule type
        helper_screen = RulesHelperScreen(
            rule_type=rule_type,
            docs_cache=self.docs_cache,
        )
        self.app.push_screen(helper_screen)

    async def action_delete_feed(self) -> None:
        """Delete the feed with confirmation and visual feedback.

        Shows a confirmation message before deleting.
        Requires pressing the button twice for safety.
        Provides visual feedback during deletion.
        """
        # Check if this is a confirmation press
        if not hasattr(self, "_delete_confirmed"):
            self._delete_confirmed = False

        if not self._delete_confirmed:
            # First press - show confirmation
            self._show_message(
                "⚠️  Press Delete Feed again to confirm. This action cannot be undone.",
                severity="error",
            )
            self._delete_confirmed = True
            return

        # Second press - proceed with deletion
        if not hasattr(self.app, "client") or not self.app.client:  # type: ignore[attr-defined]
            self._show_message("✗ Error: API client not available", severity="error")
            self._delete_confirmed = False
            return

        # Disable delete button and show loading message
        delete_button = self.query_one("Button#delete-feed-button", expect_type=Button)
        delete_button.disabled = True
        self._show_message("🗑️  Deleting feed...", severity="info")

        try:
            await self.app.client.delete_feed(self.feed_id)  # type: ignore[attr-defined]
            self._show_message(
                f"✓ Feed '{self.feed.title}' deleted successfully",
                severity="success",
            )
            # Close the screen after successful deletion
            self.app.pop_screen()
        except TimeoutError:
            self._show_message("✗ Request timeout while deleting feed", severity="error")
            self._delete_confirmed = False
            delete_button.disabled = False
        except ConnectionError:
            self._show_message("✗ Connection failed while deleting feed", severity="error")
            self._delete_confirmed = False
            delete_button.disabled = False
        except Exception as e:
            self._show_message(f"✗ Error deleting feed: {e}", severity="error")
            self._delete_confirmed = False
            delete_button.disabled = False

    def _on_field_changed(self, widget_id: str, new_value: Any) -> None:
        """Mark a field as dirty when its value changes.

        Args:
            widget_id: ID of the widget that changed
            new_value: New value of the widget
        """
        # Map widget IDs to feed field names
        field_mapping = {
            # General Settings
            "feed-title": "title",
            "site-url": "site_url",
            "feed-url": "feed_url",
            "category-id": "category_id",
            "feed-disabled": "disabled",
            # Network Settings
            "auth-username": "username",
            "auth-password": "password",
            "user-agent": "user_agent",
            "proxy-url": "proxy_url",
            "ignore-https-errors": "ignore_https_errors",
            # Rules & Filtering
            "scraper-rules": "scraper_rules",
            "rewrite-rules": "rewrite_rules",
            "url-rewrite-rules": "url_rewrite_rules",
            "blocking-rules": "blocking_rules",
            "keep-rules": "keep_rules",
            # Feed Information
            "check-interval": "check_interval",
        }

        field_name = field_mapping.get(widget_id, widget_id)

        # Store original value on first change
        if field_name not in self.original_values:
            self.original_values[field_name] = getattr(self.feed, field_name, None)

        # Store the new value for collection later
        if not hasattr(self, "_field_values"):
            self._field_values: dict[str, Any] = {}
        self._field_values[field_name] = new_value

        # Track change with persistence manager
        old_value = self.original_values.get(field_name)
        self.persistence.track_field_change(
            feed_id=self.feed_id,
            field_id=widget_id,
            field_name=field_name,
            before_value=old_value,
            after_value=new_value,
        )

        # Mark field as dirty
        self.dirty_fields[field_name] = True
        self.is_dirty = True

        # Enable save button
        self.query_one("Button#save-button", expect_type=Button).disabled = False

        # Update unsaved indicator
        self._update_unsaved_indicator()

        # Trigger auto-save with debouncing
        self._schedule_auto_save()

    def _collect_field_values(self) -> dict[str, Any]:
        """Collect all modified field values for API update.

        Returns:
            Dictionary of field_name: new_value for dirty fields
        """
        updates: dict[str, Any] = {}

        # Collect values for dirty fields
        if hasattr(self, "_field_values"):
            for field_name in self.dirty_fields:
                if self.dirty_fields[field_name] and field_name in self._field_values:
                    updates[field_name] = self._field_values[field_name]

        return updates

    def _show_message(
        self,
        message: str,
        severity: str = "info",
    ) -> None:
        """Display a status message with styled appearance.

        Args:
            message: Message text to display
            severity: Message severity ("info", "success", "error", "warning")
        """
        self.status_message = message
        self.status_severity = severity

        # Update status display
        status_widget = self.query_one("#status-message", expect_type=Static)
        status_widget.update(message)

        # Remove all severity classes
        status_widget.remove_class("success")
        status_widget.remove_class("error")
        status_widget.remove_class("warning")
        status_widget.remove_class("info")

        # Add appropriate severity class and color
        if severity == "success":
            status_widget.add_class("success")
        elif severity == "error":
            status_widget.add_class("error")
        elif severity == "warning":
            status_widget.add_class("warning")
        else:
            status_widget.add_class("info")

    def _store_original_values(self) -> None:
        """Store original field values for change tracking."""
        self.original_values = {
            # General Settings
            "title": self.feed.title,
            "site_url": self.feed.site_url,
            "feed_url": self.feed.feed_url,
            "category_id": self.feed.category_id,
            "disabled": self.feed.disabled,
            # Network Settings
            "username": "",
            "password": "",
            "user_agent": "",
            "proxy_url": "",
            "ignore_https_errors": False,
            # Rules & Filtering
            "scraper_rules": "",
            "rewrite_rules": "",
            "url_rewrite_rules": "",
            "blocking_rules": "",
            "keep_rules": "",
            # Feed Information
            "check_interval": "",
        }

    def _check_for_recovery(self) -> None:
        """Check and handle recovery from previous session."""
        if self.persistence.should_prompt_recovery(self.feed_id):
            recovery = self.persistence.check_for_recovery(self.feed_id)

            if recovery:
                self._show_recovery_dialog(recovery)
            else:
                # Mark that we prompted (even if no recovery)
                self.persistence.mark_recovery_handled(self.feed_id)

    def _show_recovery_dialog(self, recovery: Any) -> None:
        """Show recovery dialog with user options.

        Args:
            recovery: RecoveryInfo object with recovery data
        """
        message = (
            f"Found unsaved changes from {recovery.time_since_last_save}\n\n"
            f"Would you like to:\n"
            f"• (R)ecover: Restore unsaved changes\n"
            f"• (D)iscard: Start with current feed values\n"
            f"• (C)ancel: Cancel editing"
        )

        self._show_message(message, severity="warning")
        self._recovery_pending = recovery

    def _update_unsaved_indicator(self) -> None:
        """Update the unsaved changes indicator in the header."""
        try:
            indicator = self.query_one("#unsaved-indicator", expect_type=Static)
            change_count = self.persistence.get_change_count(self.feed_id)

            if change_count > 0:
                indicator.update(f"● Unsaved changes: {change_count} field(s)")
                indicator.styles.color = "yellow"
            else:
                indicator.update("")
                indicator.styles.color = "$text-muted"
        except Exception:  # noqa: S110  # nosec: B110
            pass

    def _schedule_auto_save(self) -> None:
        """Schedule auto-save with debouncing (1 second delay)."""
        # Cancel previous timer if exists
        if self._auto_save_handle:
            self._auto_save_handle.stop()

        # Schedule new auto-save (1 second debounce delay)
        self._auto_save_handle = self.set_timer(1.0, self._auto_save_draft)

    def _auto_save_draft(self) -> None:
        """Auto-save current field values as draft."""
        # Collect current field values from UI
        field_values = self._collect_field_values()

        if field_values:
            # Add current field values
            field_values.update(self._get_current_field_values())

            # Save as draft
            self.persistence.auto_save_draft(self.feed_id, field_values)

    def _get_current_field_values(self) -> dict[str, Any]:
        """Get current values from all UI fields.

        Returns:
            Dictionary of field_id: value for all fields
        """
        field_values: dict[str, Any] = {}

        try:
            # Collect from Input fields
            for input_field in self.query(Input):
                if input_field.id and not input_field.disabled:
                    field_values[input_field.id] = input_field.value

            # Collect from Checkbox fields
            for checkbox in self.query(Checkbox):
                if checkbox.id:
                    field_values[checkbox.id] = checkbox.value

            # Collect from TextArea fields
            for textarea in self.query(TextArea):
                if textarea.id:
                    field_values[textarea.id] = textarea.text
        except Exception:  # noqa: S110  # nosec: B110
            pass

        return field_values
