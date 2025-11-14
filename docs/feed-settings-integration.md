# FeedSettingsScreen - Form Persistence Integration Guide

## Overview

This guide explains how to integrate Phase 9 Form Persistence & Auto-Recovery into the FeedSettingsScreen.

## Integration Steps

### Step 1: Add FormPersistenceManager to FeedSettingsScreen

```python
from miniflux_tui.form_persistence_manager import FormPersistenceManager

class FeedSettingsScreen(Screen):
    def __init__(self, feed_id: int, feed: Feed, client: MinifluxClient, **kwargs):
        super().__init__(**kwargs)
        self.feed_id = feed_id
        self.feed = feed
        self.client = client

        # Add persistence manager
        self.persistence = FormPersistenceManager()

        # Track original values for reset
        self.original_values: dict[str, Any] = {}
```

### Step 2: Check for Recovery on Mount

```python
def on_mount(self) -> None:
    """Called when screen is mounted."""
    # Store original values
    self._store_original_values()

    # Check for recovery
    self._check_for_recovery()

    # Initialize other screen elements
    ...

def _check_for_recovery(self) -> None:
    """Check and handle recovery."""
    # Check if recovery available and we should prompt
    if self.persistence.should_prompt_recovery(self.feed_id):
        recovery = self.persistence.check_for_recovery(self.feed_id)

        if recovery:
            # Show recovery dialog
            self._show_recovery_dialog(recovery)

        # Mark that we've prompted (even if no recovery)
        self.persistence.mark_recovery_handled(self.feed_id)

def _store_original_values(self) -> None:
    """Store original values for tracking changes."""
    self.original_values = {
        "feed-title": self.feed.title,
        "site-url": self.feed.site_url,
        "category": self.feed.category,
        # ... store all field original values
    }
```

### Step 3: Show Recovery Dialog

```python
def _show_recovery_dialog(self, recovery: RecoveryInfo) -> None:
    """Show recovery options dialog."""
    title = f"Recover from {recovery.time_since_last_save}?"

    message = (
        f"Found unsaved changes from {recovery.time_since_last_save}\n\n"
        f"Would you like to:\n"
        f"• Recover: Restore unsaved changes\n"
        f"• Discard: Start with current feed values\n"
        f"• Cancel: Cancel editing"
    )

    # Show modal dialog with three options
    # (Implementation depends on Textual dialog system)
    # On recover: self._restore_recovery()
    # On discard: self._discard_recovery()
    # On cancel: self.app.pop_screen()

def _restore_recovery(self) -> None:
    """Restore field values from recovery."""
    field_values = self.persistence.recover_field_values(self.feed_id)

    if field_values:
        # Populate all input fields from recovered values
        self._populate_fields_from_dict(field_values)
        self.app.notify("Recovery restored successfully", severity="success")
    else:
        self.app.notify("Failed to restore recovery", severity="error")

def _discard_recovery(self) -> None:
    """Discard recovery without restoring."""
    self.persistence.discard_recovery(self.feed_id)
    self.app.notify("Recovery discarded", severity="info")
```

### Step 4: Track Field Changes

```python
# When a field value changes, track it
async def _on_field_changed(self, field_id: str, new_value: Any) -> None:
    """Called when user modifies a field."""
    # Get the original value
    original_value = self.original_values.get(field_id)

    # Track the change
    self.persistence.track_field_change(
        feed_id=self.feed_id,
        field_id=field_id,
        field_name=self._get_field_display_name(field_id),
        before_value=original_value,
        after_value=new_value
    )

    # Auto-save draft
    self._auto_save_draft()

    # Update unsaved indicator
    self._update_unsaved_indicator()

def _get_field_display_name(self, field_id: str) -> str:
    """Get human-readable field name."""
    names = {
        "feed-title": "Title",
        "site-url": "Site URL",
        "category": "Category",
        # ... map all field IDs to display names
    }
    return names.get(field_id, field_id)

def _update_unsaved_indicator(self) -> None:
    """Update UI indicator for unsaved changes."""
    change_count = self.persistence.get_change_count(self.feed_id)

    if change_count > 0:
        # Show unsaved indicator (e.g., in header)
        self._show_unsaved_indicator(change_count)
    else:
        # Hide unsaved indicator
        self._hide_unsaved_indicator()

def _show_unsaved_indicator(self, count: int) -> None:
    """Show indicator that there are unsaved changes."""
    # Update screen header or status bar
    # Example: "● Unsaved: 3 changes"
    pass
```

### Step 5: Auto-Save Drafts

```python
def _auto_save_draft(self) -> None:
    """Auto-save current field values as draft."""
    # Collect current values from all fields
    field_values = self._collect_current_field_values()

    # Save as draft
    self.persistence.auto_save_draft(self.feed_id, field_values)

    # Optional: Show brief "saving..." indicator
    # (auto-save should be fast and quiet)

def _collect_current_field_values(self) -> dict[str, Any]:
    """Collect current values from all input fields."""
    return {
        "feed-title": self.query_one("#feed-title", Input).value,
        "site-url": self.query_one("#site-url", Input).value,
        "category": self.query_one("#category-select").value,
        # ... collect all field values
    }
```

### Step 6: Save Changes to API

```python
async def action_save_changes(self) -> None:
    """Save changes to API."""
    try:
        # Collect current values
        updated_data = self._collect_current_field_values()

        # Call API to update feed
        await self.client.update_feed(self.feed_id, **updated_data)

        # Success: clear persistence state
        self.persistence.clear_session(self.feed_id)

        # Show success message
        self.app.notify("Feed settings saved successfully", severity="success")

        # Close screen
        self.app.pop_screen()

    except Exception as e:
        # Error: keep persistence state for recovery
        self.app.notify(f"Failed to save: {e}", severity="error")
        # Draft is still available for recovery

def _populate_fields_from_dict(self, values: dict[str, Any]) -> None:
    """Populate input fields from dictionary."""
    # Update all input fields with recovered values
    self.query_one("#feed-title", Input).value = values.get("feed-title", "")
    self.query_one("#site-url", Input).value = values.get("site-url", "")
    # ... populate all fields
```

### Step 7: Cancel Changes

```python
async def action_cancel_changes(self) -> None:
    """Cancel editing without saving."""
    if self.persistence.has_unsaved_changes(self.feed_id):
        # Confirm before discarding changes
        if await self._confirm_discard_changes():
            # Discard persistence state
            self.persistence.discard_recovery(self.feed_id)

            # Close screen
            self.app.pop_screen()
    else:
        # No changes, just close
        self.app.pop_screen()

async def _confirm_discard_changes(self) -> bool:
    """Ask user to confirm discarding changes."""
    # Show confirmation dialog
    # Return True if user confirms, False if cancels
    # (Implementation depends on Textual dialog system)
    pass
```

### Step 8: Display Change Summary (Optional)

```python
def _show_change_summary(self) -> None:
    """Display summary of changes."""
    summary = self.persistence.get_field_change_summary(self.feed_id)

    if summary:
        message = (
            f"Changes ({summary['total_changes']}):\n"
            f"  Modified: {summary['modified_count']}\n"
            f"  Added: {summary['added_count']}\n"
            f"  Removed: {summary['removed_count']}"
        )

        self.app.notify(message)

def _show_field_diff(self, field_id: str) -> None:
    """Display before/after for a specific field."""
    diff = self.persistence.get_field_diff(self.feed_id, field_id)

    if diff:
        message = (
            f"{diff['field_name']}:\n"
            f"Before: {diff['before']}\n"
            f"After: {diff['after']}"
        )

        self.app.notify(message)
```

## Complete Integration Checklist

- [ ] Add `FormPersistenceManager` import
- [ ] Initialize in `__init__()`
- [ ] Check for recovery in `on_mount()`
- [ ] Show recovery dialog
- [ ] Track changes in field change handlers
- [ ] Auto-save drafts periodically
- [ ] Show unsaved indicator
- [ ] Clear session after successful save
- [ ] Handle errors and keep draft on failure
- [ ] Display change summary (optional)
- [ ] Display field diffs (optional)
- [ ] Test recovery workflow
- [ ] Test change tracking
- [ ] Test auto-save
- [ ] Test error scenarios

## Event Hooks to Integrate

### On Field Changed
```
When user modifies any field:
1. Track the change with before/after values
2. Auto-save draft
3. Update unsaved indicator
```

### On Save Button Clicked
```
When user clicks save:
1. Validate all fields
2. Call API to update feed
3. On success: Clear persistence state + Close screen
4. On failure: Keep draft for recovery + Show error
```

### On Cancel Button Clicked
```
When user clicks cancel:
1. Check if unsaved changes exist
2. If yes: Show confirmation dialog
3. If confirmed: Discard recovery + Close screen
4. If cancelled: Stay in editing mode
```

### On Screen Mount
```
When screen opens:
1. Store original values
2. Check for recovery
3. If recovery exists: Show recovery dialog
4. Let user choose: Recover | Discard | Cancel
```

## Testing Checklist

### Test Recovery Workflow
```
1. Open feed settings
2. Edit fields and close WITHOUT saving (kill app)
3. Open feed settings again
4. Confirm recovery dialog shows
5. Test "Recover" - values restored ✓
6. Test "Discard" - values cleared ✓
7. Test "Cancel" - stays in recovery mode ✓
```

### Test Change Tracking
```
1. Open feed settings
2. Edit a field
3. Check: unsaved indicator shows
4. Check: change count is correct
5. Close without saving
6. Reopen and recover
7. Verify all changes restored ✓
```

### Test Auto-Save
```
1. Open feed settings
2. Edit a field
3. Check: draft_FEED_ID.json created
4. Edit more fields
5. Check: draft file updated
6. Close app
7. Reopen - all changes should be recoverable ✓
```

### Test Error Scenarios
```
1. API error during save: Draft preserved ✓
2. Network error: Draft preserved ✓
3. Invalid values: Show error, keep draft ✓
4. App crash: Draft recoverable ✓
5. Successful save: Draft cleared ✓
```

## Common Issues & Solutions

### Issue: Recovery Dialog Not Showing
**Check:**
- Draft file exists: `~/.config/miniflux-tui/drafts/draft_FEED_ID.json`
- `should_prompt_recovery()` returns True
- Recovery not recently marked as handled

**Solution:**
```python
# Verify recovery
recovery = self.persistence.check_for_recovery(self.feed_id)
print(f"Recovery exists: {recovery is not None}")
print(f"Should prompt: {self.persistence.should_prompt_recovery(self.feed_id)}")
```

### Issue: Changes Not Being Tracked
**Check:**
- Field change handler is being called
- Track change is called with correct parameters
- Feed ID is correct

**Solution:**
```python
# Add debug logging
print(f"Tracking change: {field_id} = {before_value} -> {after_value}")
self.persistence.track_field_change(...)
```

### Issue: Auto-Save Not Working
**Check:**
- `_auto_save_draft()` is being called
- Field values are being collected correctly
- Draft file permissions are correct

**Solution:**
```python
# Verify draft being saved
field_values = self._collect_current_field_values()
print(f"Saving draft with {len(field_values)} fields")
self.persistence.auto_save_draft(self.feed_id, field_values)
```

## Performance Tips

1. **Auto-save throttling**: Consider debouncing rapid changes
  ```python
  # Save only after 1 second of no changes
  self._debounce_auto_save()
  ```

2. **Large field values**: Be mindful of very large text fields
  ```python
  # Draft size shouldn't exceed 10KB
  # Keep rule fields reasonable
  ```

3. **Change tracking**: Clear after successful save
  ```python
  self.persistence.clear_session(self.feed_id)
  ```

## References

- See `docs/phase-9-persistence.md` for full system documentation
- See `miniflux_tui/form_persistence_manager.py` for API reference
- See test files for usage examples:
  - `tests/test_form_persistence_manager.py`
  - `tests/test_draft_manager.py`
  - `tests/test_recovery_manager.py`
  - `tests/test_change_tracker.py`
