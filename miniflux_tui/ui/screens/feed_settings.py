# SPDX-License-Identifier: MIT
"""Feed settings screen for comprehensive feed configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Static

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
    }

    FeedSettingsScreen > Header {
        dock: top;
    }

    FeedSettingsScreen > Footer {
        dock: bottom;
    }

    FeedSettingsScreen > ScrollableContainer {
        height: 1fr;
        width: 100%;
        overflow: auto auto;
    }

    #settings-header {
        width: 100%;
        height: auto;
        padding: 1 2;
        background: $boost;
        border-bottom: solid $primary;
        content-align: left middle;
    }

    .section {
        width: 100%;
        height: auto;
        padding: 1 2;
        margin-bottom: 1;
        border-bottom: solid $primary 30%;
    }

    .section-title {
        width: 100%;
        height: auto;
        padding-bottom: 1;
        text-style: bold;
        color: $accent;
    }

    .field-group {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
    }

    .field-label {
        width: 100%;
        height: auto;
        margin-bottom: 0;
        color: $text-muted;
    }

    .field-value {
        width: 100%;
        height: auto;
        margin: 0;
    }

    #status-message {
        width: 100%;
        height: auto;
        padding: 1 2;
        color: $text-muted;
    }

    #button-container {
        width: 100%;
        height: auto;
        padding: 1 2;
        border-top: solid $primary 30%;
        layout: horizontal;
    }

    #button-container Button {
        margin-right: 1;
    }

    .danger-button {
        background: $error;
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

        # Dirty state tracking
        self.dirty_fields: dict[str, bool] = {}
        self.is_dirty = False

        # Store original values for cancel
        self.original_values: dict[str, Any] = {}

        # Status message
        self.status_message = ""
        self.status_severity = "info"  # "info", "success", "error", "warning"

    def compose(self) -> ComposeResult:
        """Compose the feed settings screen layout.

        Yields:
            Composed widgets for the screen
        """
        yield Header()

        with ScrollableContainer():
            # Settings header
            yield Static(
                f"Feed Settings: {self.feed.title}",
                id="settings-header",
            )

            # General Settings Section
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

            # Placeholder for other sections
            yield Static("Network Settings - TBD", classes="section")
            yield Static("Rules & Filtering - TBD", classes="section")
            yield Static("Feed Information - TBD", classes="section")
            yield Static("Danger Zone - TBD", classes="section")

        # Status message area
        yield Static(self.status_message, id="status-message")

        # Button container
        with Static(id="button-container"):
            yield Button("Save", id="save-button", disabled=True)
            yield Button("Cancel", id="cancel-button")

        yield Footer()

    def on_mount(self) -> None:
        """Called when screen is mounted.

        Initialize screen state and load feed data.
        """
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
        2. Calls the API to update the feed
        3. Clears dirty state on success
        4. Shows success/error message
        """
        if not self.is_dirty:
            self._show_message("No changes to save", severity="info")
            return

        try:
            # Collect field values (to be implemented with actual fields)
            updates = self._collect_field_values()

            # Call API
            updated_feed = await self.client.update_feed(self.feed_id, **updates)

            # Update internal state
            self.feed = updated_feed
            self.is_dirty = False
            self.dirty_fields.clear()
            self.original_values.clear()

            # Disable save button
            self.query_one("Button#save-button", expect_type=Button).disabled = True

            self._show_message(
                "Feed settings saved successfully",
                severity="success",
            )

        except TimeoutError:
            self._show_message("Request timeout while saving", severity="error")
        except ConnectionError:
            self._show_message("Connection failed while saving", severity="error")
        except ValueError as e:
            self._show_message(f"Invalid input: {e}", severity="error")
        except Exception as e:
            self._show_message(f"Error saving settings: {e}", severity="error")

    async def action_cancel_changes(self) -> None:
        """Cancel changes and close screen.

        If there are unsaved changes, show confirmation dialog.
        Otherwise, close immediately.
        """
        if self.is_dirty:
            # Show confirmation (to be implemented)
            self._show_message(
                "Changes discarded. Press Escape again to close.",
                severity="warning",
            )
            self.is_dirty = False
            self.dirty_fields.clear()
            return

        # Close the screen
        self.app.pop_screen()

    def action_open_helper(self) -> None:
        """Open helper screen for current field.

        This action opens appropriate helper screens based on
        which rule field is currently focused (if any).
        To be implemented when helpers are added.
        """
        self._show_message("Helper not yet available", severity="info")

    def _on_field_changed(self, widget_id: str, new_value: Any) -> None:
        """Mark a field as dirty when its value changes.

        Args:
            widget_id: ID of the widget that changed
            new_value: New value of the widget
        """
        # Map widget IDs to feed field names
        field_mapping = {
            "feed-title": "title",
            "site-url": "site_url",
            "feed-url": "feed_url",
            "category-id": "category_id",
            "feed-disabled": "disabled",
        }

        field_name = field_mapping.get(widget_id, widget_id)

        # Store original value on first change
        if field_name not in self.original_values:
            self.original_values[field_name] = getattr(self.feed, field_name, None)

        # Store the new value for collection later
        if not hasattr(self, "_field_values"):
            self._field_values: dict[str, Any] = {}
        self._field_values[field_name] = new_value

        # Mark field as dirty
        self.dirty_fields[field_name] = True
        self.is_dirty = True

        # Enable save button
        self.query_one("Button#save-button", expect_type=Button).disabled = False

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
        """Display a status message.

        Args:
            message: Message text to display
            severity: Message severity ("info", "success", "error", "warning")
        """
        self.status_message = message
        self.status_severity = severity

        # Update status display
        status_widget = self.query_one("#status-message", expect_type=Static)
        status_widget.update(message)

        # Set color based on severity
        if severity == "success":
            status_widget.styles.color = "green"
        elif severity == "error":
            status_widget.styles.color = "red"
        elif severity == "warning":
            status_widget.styles.color = "yellow"
        else:
            status_widget.styles.color = "$text-muted"
