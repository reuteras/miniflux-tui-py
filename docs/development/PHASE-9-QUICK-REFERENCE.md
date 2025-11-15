# Phase 9: Form Persistence & Auto-Recovery - Quick Reference Guide

## Quick Facts

- **Current Status**: Phases 1-8 complete, production-ready
- **Test Coverage**: 96.5% (1,273+ tests)
- **Files with Code**: 679 lines (feed_settings.py)
- **Test Files**: 1,273+ tests across multiple test files
- **Recommended Next**: Phase 9 - Form Persistence & Auto-Recovery

## Phase 9 At A Glance

|  Aspect                |  Details                                            |
| ---------------------- | --------------------------------------------------- |
|  **Goal**              |  Auto-save drafts, recover from crashes             |
|  **Timeline**          |  85-128 hours (2-3 weeks)                           |
|  **Components**        |  3 (Draft persistence, Recovery, Diff viewer)       |
|  **New Tests**         |  170+ tests (draft, recovery, diff)                 |
|  **New Files**         |  3 (state_cache.py, recovery.py, change_viewer.py)  |
|  **Modified Files**    |  2 (feed_settings.py, app.py)                       |
|  **Risk Level**        |  Low (orthogonal to existing code)                  |
|  **Breaking Changes**  |  None                                               |

## The 3 Components of Phase 9

### Component 1: Draft State Persistence
```
User edits feed settings
    ↓
Every change triggers auto-save (debounced 3s)
    ↓
Draft saved to ~/.config/miniflux-tui/drafts/feed_{id}.json
    ↓
User closes app without saving
    ↓
On next open: "Restore draft?" → [Restore] [Discard]
```

**Scope**: 15-20 hours | **Tests**: 80+ | **Key Files**: `state_cache.py`

### Component 2: Auto-Recovery on Crash
```
App crashes or force-quit
    ↓
Recovery Manager detects stale drafts on startup
    ↓
Recovery Dialog appears: "Recover draft for Feed XYZ?"
    ↓
User selects:
  • "Restore & Edit" → Opens settings with draft loaded
  • "Discard" → Deletes draft file
  • "Save as Template" → Saves for future use
```

**Scope**: 10-15 hours | **Tests**: 50+ | **Key Files**: `recovery.py`

### Component 3: Change History/Diff Viewer
```
User opens change viewer (v key)
    ↓
Shows: Original Value → New Value [Status]
    ↓
User can revert individual fields
    ↓
Or continue editing with visual feedback
```

**Scope**: 12-18 hours | **Tests**: 40+ | **Key Files**: `change_viewer.py`

## Implementation Checklist

### Phase 9 Tasks (Recommended Sequence)

- [ ] **Days 1-2: State Cache Infrastructure**
  - [ ] Create `miniflux_tui/state_cache.py`
  - [ ] Implement FieldStateCache class
  - [ ] Add save/load/delete draft methods
  - [ ] Write 30+ unit tests
  - [ ] Add cleanup for old drafts

- [ ] **Days 3-4: FeedSettingsScreen Integration**
  - [ ] Modify `feed_settings.py` __init__
  - [ ] Add auto-save on field change (debounced)
  - [ ] Add draft loading on screen open
  - [ ] Add "Draft restored" UI indicator
  - [ ] Write 50+ integration tests

- [ ] **Days 5-6: App-Level Recovery**
  - [ ] Create `miniflux_tui/recovery.py`
  - [ ] Implement RecoveryManager
  - [ ] Create recovery dialog screen
  - [ ] Integrate with `app.py` startup
  - [ ] Write 50+ recovery tests

- [ ] **Day 7: Change Viewer Screen**
  - [ ] Create `change_viewer.py`
  - [ ] Implement ChangeViewerScreen
  - [ ] Add diff calculation
  - [ ] Add field revert functionality
  - [ ] Write 40+ viewer tests

- [ ] **Days 8-9: Testing & Polish**
  - [ ] Integration tests (all 3 components together)
  - [ ] Performance testing (auto-save latency)
  - [ ] Manual testing with crash simulation
  - [ ] Documentation updates
  - [ ] Code review preparation

## File Changes Summary

### New Files
|  File                                        |  Purpose                  |  Size (est.)    |
| -------------------------------------------- | ------------------------- | --------------- |
|  `miniflux_tui/state_cache.py`               |  Draft state persistence  |  200-300 lines  |
|  `miniflux_tui/recovery.py`                  |  Recovery system          |  200-250 lines  |
|  `miniflux_tui/ui/screens/change_viewer.py`  |  Diff viewer              |  250-350 lines  |
|  `tests/test_state_cache.py`                 |  State cache tests        |  400-500 lines  |
|  `tests/test_recovery.py`                    |  Recovery tests           |  300-400 lines  |
|  `tests/test_change_viewer.py`               |  Diff viewer tests        |  300-400 lines  |

### Modified Files
|  File                                        |  Changes                        |  Impact          |
| -------------------------------------------- | ------------------------------- | ---------------- |
|  `miniflux_tui/ui/screens/feed_settings.py`  |  Add auto-save, draft loading   |  +150-200 lines  |
|  `miniflux_tui/ui/app.py`                    |  Add recovery check on startup  |  +100-150 lines  |

## Key Implementation Details

### Draft File Format (JSON)
```json
{
  "feed_id": 42,
  "timestamp": "2025-11-14T19:30:00Z",
  "dirty_fields": {
    "title": true,
    "username": true,
    "scraper_rules": false
  },
  "field_values": {
    "title": "Updated Feed Title",
    "username": "newuser",
    "site_url": "https://example.com"
  }
}
```

### Auto-Save Debouncing
```python
# Debounce 3 seconds to avoid excessive disk writes
# Only save when user stops typing for 3 seconds
async def _schedule_auto_save(self):
    if self._auto_save_timeout:
        self._auto_save_timeout.cancel()
    self._auto_save_timeout = asyncio.create_task(
        self._auto_save_draft_delayed()
    )

async def _auto_save_draft_delayed(self):
    await asyncio.sleep(3)  # Wait 3 seconds
    await self._auto_save_draft()
```

### Recovery Dialog Options
```python
class RecoveryDialog(Screen):
    """User options for recovered drafts"""

    # Button layout:
    # [Restore & Edit] [Discard] [Save as Template]

    async def on_restore_pressed(self):
        # Load draft and open FeedSettingsScreen

    async def on_discard_pressed(self):
        # Delete draft file

    async def on_template_pressed(self):
        # Save as config template for future use
```

## Integration with Existing Phases

### Reusing Phase 1-2 Patterns
- **DocsCache pattern** → Inspire FieldStateCache design
- **Error handling** → Reuse TimeoutError, ConnectionError patterns
- **Session state** → Extend to persistent state

### Leveraging Phase 3-6 Infrastructure
- **Field mapping** → Use for state serialization
- **_on_field_changed hook** → Trigger auto-save
- **Original values** → Enable diff comparison
- **Dirty tracking** → Persist dirty_fields dict

### Building on Phase 7-8
- **Confirmation pattern** → Reuse for recovery confirmation
- **Error messaging** → Integrate recovery status
- **Helper patterns** → No direct dependency

## Success Metrics

### Performance
- Auto-save completes in <500ms (no UI lag)
- Startup recovery check in <100ms
- Change viewer loads in <200ms

### Reliability
- Can recover from simulated app crash
- Drafts >7 days auto-deleted
- No data loss scenarios
- All edge cases tested

### Code Quality
- 90%+ test coverage for new code
- No breaking changes to Phases 1-8
- Documentation up to date
- All pre-commit checks pass

## Testing Strategy

### Unit Tests (70+ tests)
- Draft save/load/delete operations
- Auto-save debouncing logic
- State serialization/deserialization
- Draft cleanup scheduling

### Integration Tests (50+ tests)
- Draft restoration workflow
- Auto-save triggers on field change
- Save clears draft after success
- Cancel preserves draft for next session

### Recovery Tests (50+ tests)
- Recovery detection on startup
- User choice handling (restore/discard/template)
- Multiple concurrent drafts
- Stale draft handling

### Diff Viewer Tests (40+ tests)
- Diff calculation algorithm
- Change detection accuracy
- Revert functionality
- Edge cases (null values, etc.)

## Common Gotchas & Solutions

|  Gotcha                                |  Solution                                |
| -------------------------------------- | ---------------------------------------- |
|  Auto-save on every keystroke = slow   |  Use 3-second debounce                   |
|  Drafts pile up over time              |  Auto-cleanup (>7 days)                  |
|  Recovery on every startup = slow      |  Cache recovery check results            |
|  Concurrent save+load = corruption     |  Use atomic writes (temp file)           |
|  User ignores recovery dialog = noise  |  Show only for recent crashes (<1h old)  |

## Alternative Approaches If Phase 9 Too Large

### Cut to MVP (50 hours instead of 85-128)
Keep only:
- Draft persistence (Component 1)
- Simple recovery (Component 2, minimal UI)

Drop:
- Advanced recovery options (templates)
- Change viewer (Component 3)

### Focus on Safety First (60 hours)
Keep:
- Draft persistence + cleanup
- Recovery with restore/discard

Drop:
- Diff viewer
- Template saving

### Focus on UX (70 hours)
Keep:
- Diff viewer (Component 3)
- Draft persistence
- Basic recovery

Drop:
- Auto-recovery dialog
- Template functionality

## Phase 9 After Phase 8

```
Phase 8 (Helper Docs)
    ↓
    • Users can now read rule documentation while editing
    • But changes are lost on crash - UX problem!
    ↓
Phase 9 (Persistence)
    ↓
    • Changes auto-saved to disk
    • Recovery from crashes
    • Can review changes before saving
    ↓
Phase 10 (Batch Operations)
    ↓
    • Configuration templates from Phase 9
    • Apply same config to multiple feeds
    • Build on Phase 9's change viewer
```

## Resources

- **Full Analysis**: `docs/development/feed-settings-phase-analysis.md`
- **FeedSettingsScreen**: `miniflux_tui/ui/screens/feed_settings.py` (679 lines)
- **Current Tests**: `tests/test_feed_settings_screen.py` (1,273+ tests)
- **Git History**: `git log --oneline --all | grep "Phase"`

## Starting Phase 9?

1. Read full analysis: `docs/development/feed-settings-phase-analysis.md`
2. Create feature branch: `git checkout -b feat/phase9-form-persistence`
3. Start with Component 1 (state_cache.py)
4. Follow implementation checklist above
5. Run tests frequently: `uv run pytest tests/test_state_cache.py -v`

Good luck!
