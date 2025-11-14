# Phase 9: Form Persistence & Auto-Recovery System

## Overview

Phase 9 implements a comprehensive form persistence and automatic recovery system for the Feed Settings Screen. It protects against data loss from application crashes and enables multi-session editing workflows.

## Architecture

The system consists of four integrated components:

```
┌─────────────────────────────────────────────┐
│     FormPersistenceManager                  │ (Single Interface)
│  (Unified API for all persistence)          │
└──────────────────────────────────────────────┘
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
┌─────────────┐ ┌──────────────┐ ┌──────────────┐
│Draft        │ │Recovery      │ │Change        │
│Manager      │ │Manager       │ │Tracker       │
└─────────────┘ └──────────────┘ └──────────────┘
    ↓               ↓               ↓
    └───────────────┼───────────────┘
                    ↓
        ┌───────────────────────┐
        │ Persistent Storage    │
        │ (config/drafts/)      │
        └───────────────────────┘
```

### Components

#### 1. **DraftManager** (Phase 9.1)
Handles persistent storage of form drafts.

**Responsibilities:**
- Save field values to JSON files
- Load saved drafts from disk
- List available drafts
- Delete/cleanup old drafts (7-day retention)
- Handle corrupted files gracefully

**Storage:**
- Location: `~/.config/miniflux-tui/drafts/` (Linux/macOS)
- Format: `draft_FEED_ID.json`
- Timezone: UTC (cross-platform compatible)

#### 2. **RecoveryManager** (Phase 9.2)
Provides crash recovery and auto-save functionality.

**Responsibilities:**
- Detect available recovery sessions
- Smart prompting (5-minute timeout, no re-prompts)
- Recover field values from drafts
- Discard recovery without restoring
- Auto-cleanup of old sessions

**Recovery Flow:**
```
User opens FeedSettings
    ↓
Check for recovery (file exists?)
    ↓
[If exists] Show recovery dialog
    ↓
User chooses: Recover | Discard | Cancel
```

#### 3. **ChangeTracker** (Phase 9.3)
Tracks all field modifications with before/after values.

**Responsibilities:**
- Track field changes with timestamps
- Categorize changes (added, modified, removed)
- Provide field-level change history
- Generate change summaries and diffs
- Support complex value types

**Change Tracking:**
- Every field edit recorded with before/after values
- Automatic change type detection
- Timestamp for each change
- Change summaries for UI display

#### 4. **FormPersistenceManager** (Phase 9.4)
Unified interface orchestrating all three managers.

**Responsibilities:**
- Provide single API for form persistence
- Coordinate between managers
- Handle complex workflows
- Provide comprehensive session information

## Usage Patterns

### Basic Usage in FeedSettingsScreen

```python
from miniflux_tui.form_persistence_manager import FormPersistenceManager

class FeedSettingsScreen(Screen):
    def __init__(self, feed_id: int, ...):
        super().__init__()
        self.feed_id = feed_id
        self.persistence = FormPersistenceManager()

    def on_mount(self) -> None:
        # Check for recovery
        if self.persistence.should_prompt_recovery(self.feed_id):
            recovery = self.persistence.check_for_recovery(self.feed_id)
            if recovery:
                self._show_recovery_dialog(recovery)

    def _on_field_change(self, field_id: str, old_value, new_value):
        # Track changes
        self.persistence.track_field_change(
            self.feed_id,
            field_id,
            "Field Name",
            old_value,
            new_value
        )

        # Auto-save draft
        self._auto_save_draft()

    def _auto_save_draft(self):
        # Get current values from all fields
        field_values = self._collect_field_values()
        self.persistence.auto_save_draft(self.feed_id, field_values)

    async def action_save_changes(self) -> None:
        # Save to API
        await self.client.update_feed(self.feed_id, ...)

        # Clear recovery after successful save
        self.persistence.clear_draft_after_save(self.feed_id)

        # Clear changes
        self.persistence.clear_session(self.feed_id)

    def _show_recovery_dialog(self, recovery):
        # Display recovery options to user
        # If user accepts: restore_values = self.persistence.recover_field_values(...)
```

### Recovery Dialog UI

```python
async def _handle_recovery_choice(self, choice: str):
    """Handle user's recovery choice."""
    if choice == "recover":
        # Restore field values from recovery
        field_values = self.persistence.recover_field_values(self.feed_id)
        self._populate_fields_from_dict(field_values)
        self.persistence.mark_recovery_handled(self.feed_id)

    elif choice == "discard":
        # Discard recovery without restoring
        self.persistence.discard_recovery(self.feed_id)
        self.persistence.mark_recovery_handled(self.feed_id)

    elif choice == "cancel":
        # User cancelled, stay in recovery mode
        # Draft will be preserved for next session
        pass
```

### Change Summary Display

```python
def _show_change_summary(self):
    """Display changes to user."""
    summary = self.persistence.get_field_change_summary(self.feed_id)

    if summary:
        message = f"Unsaved changes: {summary['total_changes']} field(s)\n"
        message += f"  Modified: {summary['modified_count']}\n"
        message += f"  Added: {summary['added_count']}\n"
        message += f"  Removed: {summary['removed_count']}"

        self.app.notify(message)
```

### Before/After Diff Display

```python
def _show_field_diff(self, field_id: str):
    """Show before/after values for a field."""
    diff = self.persistence.get_field_diff(self.feed_id, field_id)

    if diff:
        message = f"{diff['field_name']}:\n"
        message += f"  Before: {diff['before']}\n"
        message += f"  After: {diff['after']}"

        self.app.notify(message)
```

## Storage Details

### Draft File Format

```json
{
  "feed_id": 1,
  "timestamp": "2025-01-15T14:30:00+00:00",
  "field_values": {
    "feed-title": "My Feed",
    "site-url": "https://example.com",
    "description": "A great feed"
  },
  "metadata": {
    "version": 1
  }
}
```

### Directory Structure

```
~/.config/miniflux-tui/
├── config.toml                    (Main config)
└── drafts/                        (Drafts directory)
    ├── draft_1.json              (Feed 1 draft)
    ├── draft_2.json              (Feed 2 draft)
    └── draft_999.json            (Feed 999 draft)
```

## Configuration

### Cleanup Settings

```python
# Cleanup old drafts (7 days by default)
manager.cleanup_old_sessions(days=7)

# Called periodically or on app startup
# Automatic: no configuration needed
```

### Recovery Prompting

```python
# Smart prompting: 5-minute timeout between prompts
if manager.should_prompt_recovery(feed_id):
    recovery = manager.check_for_recovery(feed_id)
    if recovery:
        # Show recovery dialog
        pass

    # Mark that we prompted
    manager.mark_recovery_handled(feed_id)

# Next prompt only shows after 5 minutes
```

## Error Handling

The system gracefully handles errors:

### Corrupted Draft Files
- Corrupted JSON files are skipped
- User can start fresh without data loss
- System logs warnings (future enhancement)

### File System Errors
- IO errors during save are caught and logged
- Prevents app crash from persistence failures
- User can continue editing (draft may be lost)

### Timestamp Issues
- UTC timezone used consistently
- Cross-platform compatibility guaranteed
- Future recovery from any OS

## Performance Considerations

### Storage Efficiency
- One file per feed (not per change)
- No automatic periodic saves (saves on change)
- Automatic cleanup of old drafts (7-day retention)

### Memory Usage
- ChangeTracker stores only in-memory changes
- Changes cleared after successful save
- No persistent storage of change history

### Disk Usage
- Average draft: ~1-5 KB per feed
- Cleanup: Automatic removal of old drafts
- No significant disk impact

## Limitations

### Current Version (Phase 9.4)
1. **No field-level revert**: Can't revert individual fields
2. **No change persistence**: Changes lost on app close (in-memory only)
3. **No change history UI**: Change history not displayed in UI
4. **Manual integration needed**: Must integrate with FeedSettingsScreen

### Future Enhancements (Phase 10+)
1. **Field-level revert**: Revert specific fields to before values
2. **Change history viewer**: Display complete change timeline
3. **Diff viewer**: Visual before/after comparison
4. **Batch operations**: Batch undo/redo for multiple fields

## Testing

All components are fully tested:

### Test Coverage
- **DraftManager**: 34 tests
- **RecoveryManager**: 33 tests
- **ChangeTracker**: 31 tests
- **FormPersistenceManager**: 19 tests
- **Total**: 117 new tests

### Test Categories
- Unit tests for each component
- Integration tests for workflows
- Error handling tests
- Complex value handling tests
- Multi-feed independence tests

### Running Tests
```bash
# Run all Phase 9 tests
uv run pytest tests/test_draft_manager.py \
                tests/test_recovery_manager.py \
                tests/test_change_tracker.py \
                tests/test_form_persistence_manager.py -v

# Run full test suite
uv run pytest tests -v
```

## Migration Guide

### From No Persistence to Phase 9

1. **Add FormPersistenceManager to Screen**
  ```python
  self.persistence = FormPersistenceManager()
  ```

2. **Check for recovery on mount**
  ```python
  recovery = self.persistence.check_for_recovery(feed_id)
  if recovery and self.persistence.should_prompt_recovery(feed_id):
      # Show recovery dialog
  ```

3. **Track changes on field modification**
  ```python
  self.persistence.track_field_change(
      feed_id, field_id, field_name, old_val, new_val
  )
  ```

4. **Auto-save drafts during editing**
  ```python
  self.persistence.auto_save_draft(feed_id, field_values)
  ```

5. **Clear session after successful save**
  ```python
  self.persistence.clear_session(feed_id)
  ```

## Troubleshooting

### No Recovery Showing
- Check: `drafts_dir/draft_FEED_ID.json` exists
- Check: `should_prompt_recovery()` returns True
- Check: Recovery not marked as handled recently

### Stale Recovery Data
- Automatic cleanup runs: 7 days by default
- Manual cleanup: `cleanup_old_sessions(days=N)`
- Manual delete: `discard_recovery(feed_id)`

### Performance Issues
- Monitor draft file size (should be < 10KB)
- Check: No circular references in field values
- Check: Complex nested objects minimized

## References

### Files
- `miniflux_tui/draft_manager.py` - Draft persistence
- `miniflux_tui/recovery_manager.py` - Auto-recovery
- `miniflux_tui/change_tracker.py` - Change tracking
- `miniflux_tui/form_persistence_manager.py` - Unified interface

### Tests
- `tests/test_draft_manager.py` - 34 tests
- `tests/test_recovery_manager.py` - 33 tests
- `tests/test_change_tracker.py` - 31 tests
- `tests/test_form_persistence_manager.py` - 19 tests

### Related
- See FeedSettingsScreen for integration example
- See ROADMAP.md for Phase 10+ plans
- See ARCHITECTURE.md for system design
