# Improvement Plan for miniflux-tui-py

**Last Updated**: October 24, 2025
**Project Version**: 0.1.0

This document outlines a comprehensive plan for improving the miniflux-tui-py project, organized by priority and category.

## Executive Summary

The codebase has a solid foundation but needs improvements in:
- **Missing features**: ✅ MOSTLY RESOLVED - API calls implemented, filtering added
- **Testing**: Zero test coverage (tests were removed)
- **Code quality**: Significant code duplication and long functions
- **Documentation**: ✅ COMPLETED - Help screens and README updated with correct shortcuts (J/K navigation, e for save_entry, , for refresh)
- **Error handling**: Inconsistent patterns - silent failures in some areas
- **Performance**: Full screen remounts instead of incremental updates

**Total issues identified: 50+ across 7 categories**
**Recently completed**: Keyboard documentation fixes, save_entry feature (e key), refresh alias (, key), toggle_read/toggle_star API calls, entry filtering (u/t keys)

---

## Progress Summary

**Completed (5/15 Phase 1 items):**
- ✅ Keyboard shortcut documentation (help.py, README.md)
- ✅ Save entry feature implementation
- ✅ Refresh key alias
- ✅ API calls for toggle_read/toggle_star (Phase 1.1)
- ✅ Filtering by unread/starred entries (Phase 1.2)

**Next Priorities:**
1. Clean up remaining TODO comments (Phase 1.4)
2. Phase 2 improvements (code quality, refactoring)
3. Phase 3 improvements (input validation, documentation)

---

## Recently Implemented Features (2025)

### API Calls for Toggle Read/Star (Phase 1.1)
**Status**: ✅ COMPLETED
**Files**: `miniflux_tui/ui/screens/entry_list.py`
**Commit**: 8e0a1be

Implemented persistent API calls for marking entries as read/unread and toggling star status.

**What was implemented**:
- `action_toggle_read()` now calls `await self.app.client.change_entry_status()`
- `action_toggle_star()` now calls `await self.app.client.toggle_starred()`
- Error handling with user notifications
- Local state updates synchronized with server
- Display refresh after successful API calls

**Usage**: Press "m" to toggle read/unread status, "*" to toggle star status. Changes are now persisted to server.

### Filtering by Unread & Starred Entries (Phase 1.2)
**Status**: ✅ COMPLETED
**Files**: `miniflux_tui/ui/screens/entry_list.py`
**Commit**: 8e0a1be

Implemented filtering functionality to show only unread or starred entries.

**What was implemented**:
- Filter state variables: `filter_unread_only` and `filter_starred_only`
- `_filter_entries()` helper method to apply filters before sorting
- `action_show_unread()` to toggle unread-only view (u key)
- `action_show_starred()` to toggle starred-only view (t key)
- Mutually exclusive filters (toggling one clears the other)
- User notifications showing active filter status
- Removed misleading TODO comment from `action_show_help()`

**Usage**: Press "u" to show only unread entries, "t" to show only starred entries. Press again to show all entries.

### Save Entry Feature (e key)
**Status**: ✅ COMPLETED
**Files**: `miniflux_tui/api/client.py`, `miniflux_tui/ui/screens/entry_list.py`, `miniflux_tui/ui/screens/entry_reader.py`

Implemented the "e" key binding to save entries to third-party services using Miniflux's `save_entry` API method.

**What was implemented**:
- API client method using official `client.save_entry()` function
- Key binding in entry list screen (line 47)
- Action method `action_save_entry()` with error handling and notifications (lines 243-255)
- Key binding in entry reader screen (line 33)
- Action method in reader with success/error notifications (lines 166-173)
- Documentation in help screen and README

**Usage**: Press "e" on any entry to save it to configured third-party services (Wallabag, Shiori, or Shaarli).

### Refresh Alias (, key)
**Status**: ✅ COMPLETED
**Files**: `miniflux_tui/ui/screens/entry_list.py`

Added comma (,) as an alternative key binding for refreshing the entry list.

**What was implemented**:
- Additional binding `Binding("comma", "refresh", "Refresh", show=False)` (line 50)
- Both "r" and "," now trigger the same refresh action
- Documentation updated in help screen and README

---

## Phase 1: Immediate Priority (High Impact, Low Effort)

Estimated effort: 2-4 hours | Impact: High | Do first!

### 1.1 Implement Missing API Calls in Entry List

**Status**: ✅ COMPLETED
**Files**: `miniflux_tui/ui/screens/entry_list.py`

The `action_toggle_read()` and `action_toggle_star()` methods have been updated to persist changes to the API.

```python
# Current (lines 216-244):
def action_toggle_read(self):
    highlighted.entry.status = "read"  # ❌ Local only
    # TODO: Call API to update status

def action_toggle_star(self):
    highlighted.entry.starred = not highlighted.entry.starred  # ❌ Local only
    # TODO: Call API to update star status
```

**Fix**:
```python
async def action_toggle_read(self):
    """Toggle read/unread status of current entry."""
    if not self.list_view:
        return

    highlighted = self.list_view.highlighted_child
    if highlighted and isinstance(highlighted, EntryListItem):
        try:
            new_status = "read" if highlighted.entry.is_unread else "unread"
            await self.app.client.change_entry_status(
                highlighted.entry.id,
                new_status
            )
            highlighted.entry.status = new_status
            self._populate_list()
            self.notify(f"Entry marked as {new_status}")
        except Exception as e:
            self.notify(f"Error updating status: {e}", severity="error")

async def action_toggle_star(self):
    """Toggle star status of current entry."""
    if not self.list_view:
        return

    highlighted = self.list_view.highlighted_child
    if highlighted and isinstance(highlighted, EntryListItem):
        try:
            await self.app.client.toggle_starred(highlighted.entry.id)
            highlighted.entry.starred = not highlighted.entry.starred
            self._populate_list()
            status = "starred" if highlighted.entry.starred else "unstarred"
            self.notify(f"Entry {status}")
        except Exception as e:
            self.notify(f"Error toggling star: {e}", severity="error")
```

**Why this matters**: Users expect m/\* keys to immediately update the server, but currently changes are lost.

---

### 1.2 Implement Filtering by Unread & Starred

**Status**: ✅ COMPLETED
**Files**: `miniflux_tui/ui/screens/entry_list.py`

Implemented full filtering support for showing only unread or starred entries.

**What was implemented**:
- Filter state variables: `filter_unread_only` and `filter_starred_only`
- `_filter_entries()` helper method applied before sorting
- `action_show_unread()` toggles unread-only view with user feedback
- `action_show_starred()` toggles starred-only view with user feedback
- Mutually exclusive filters (enabling one disables the other)
- Notifications show current filter status

**Benefits**: The u/t keys now provide expected filter functionality, improving user experience and content discovery.

---

### 1.3 Fix Keyboard Shortcut Documentation

**Status**: ✅ COMPLETED
**Files**: `miniflux_tui/ui/screens/help.py`, `README.md`

Help screen and README have been updated to match actual implementation.

**What was fixed**:
- ✅ Help screen now correctly shows 'J'/'K' for next/previous entry (was showing 'n'/'p')
- ✅ README updated to show correct bindings
- ✅ Added "e" key binding for saving entries to third-party services (Wallabag, Shiori, Shaarli)
- ✅ Added "," (comma) as alias for refresh entries
- ✅ All keyboard shortcuts now documented in both help screen and README

**Current documentation includes**:
- Entry List View: j/k navigation, m (read/unread), * (star), e (save), s (cycle sort), g (group), r/, (refresh), u (unread), t (starred)
- Entry Reader View: j/k scroll, u (mark unread), * (star), e (save), o (browser), f (fetch original), J/K (next/prev entry)

**Why this was important**: Users now have accurate documentation that matches implementation. The new save_entry feature is properly documented.

---

### 1.4 Clean Up Outdated TODO Comments

**Status**: ✅ COMPLETED
**Files**: `miniflux_tui/ui/screens/entry_list.py`

Removed misleading "TODO: Push help screen" comment from `action_show_help()` method, which already implements the feature correctly.

---

## Phase 2: High Priority (High Impact, Medium Effort)

Estimated effort: 4-8 hours | Impact: High

### 2.1 Extract Repeated Code Patterns

**Problem**: Several patterns are repeated 4-5 times throughout codebase.

#### Pattern 1: Scroll Container Access (entry_reader.py)
Repeated in lines 115-135 (5 times):
```python
if not self.scroll_container:
    self.scroll_container = self.query_one(VerticalScroll)
```

**Solution**: Create helper method
```python
def _get_scroll_container(self) -> VerticalScroll:
    """Get scroll container, initializing if needed."""
    if not self.scroll_container:
        self.scroll_container = self.query_one(VerticalScroll)
    return self.scroll_container
```

Usage:
```python
# Before:
if not self.scroll_container:
    self.scroll_container = self.query_one(VerticalScroll)
self.scroll_container.scroll_down()

# After:
self._get_scroll_container().scroll_down()
```

#### Pattern 2: ListView Access (entry_list.py)
Repeated 5 times:
```python
if not self.list_view:
    try:
        self.list_view = self.query_one(ListView)
    except Exception as e:
        self.log(f"Failed to get list_view: {e}")
        return
```

**Solution**: Create helper method
```python
def _ensure_list_view(self) -> bool:
    """Ensure list_view is available. Returns False if unavailable."""
    if not self.list_view:
        try:
            self.list_view = self.query_one(ListView)
        except Exception as e:
            self.log(f"Failed to get list_view: {e}")
            return False
    return True
```

Usage:
```python
# Before:
if not self.list_view:
    try:
        self.list_view = self.query_one(ListView)
    except Exception as e:
        self.log(f"Failed to get list_view: {e}")
        return
# ... code ...

# After:
if not self._ensure_list_view():
    return
# ... code ...
```

#### Pattern 3: Client Access Check (entry_reader.py)
Repeated 4 times in async methods:
```python
if hasattr(self.app, "client") and self.app.client:
    try:
        await self.app.client.method()
    except Exception as e:
        self.notify(f"Error: {e}", severity="error")
```

**Solution**: Create helper decorator or context manager
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def api_call(self, operation_name: str = "Operation"):
    """Context manager for safe API calls with error handling."""
    if not hasattr(self.app, "client") or not self.app.client:
        self.notify("API client not available", severity="error")
        return

    try:
        yield self.app.client
    except Exception as e:
        self.log(f"Error during {operation_name}: {e}")
        self.notify(f"Error: {e}", severity="error")
```

Usage:
```python
# Before:
if hasattr(self.app, "client") and self.app.client:
    try:
        await self.app.client.mark_as_read(self.entry.id)
        self.entry.status = "read"
    except Exception as e:
        self.log(f"Error marking as read: {e}")
        self.notify(f"Error marking as read: {e}", severity="error")

# After:
async with self.api_call("marking entry as read") as client:
    await client.mark_as_read(self.entry.id)
    self.entry.status = "read"
```

#### Pattern 4: Star Icon Display
Hardcoded in 3+ places:
```python
star_icon = "★" if entry.starred else "☆"
```

**Solution**: Extract to utility function/constant
```python
# In a new utils.py:
def get_star_icon(is_starred: bool) -> str:
    """Get star icon based on starred status."""
    return "★" if is_starred else "☆"

# Or as constants:
STAR_ICON_FILLED = "★"
STAR_ICON_EMPTY = "☆"
```

**Impact**: Reduces code duplication by ~80 lines, improves maintainability.

---

### 2.2 Improve Error Handling Consistency

**Problem**: Error handling is inconsistent across screens.

**Current patterns**:
- Entry list: Uses `log()` only (silent failures)
- Entry reader: Uses both `log()` and `notify()` (good)
- App: Mixed approaches

**Solution**: Standardize on dual reporting for user-facing actions:
```python
async def action_some_feature(self):
    """Description."""
    try:
        if not hasattr(self.app, "client") or not self.app.client:
            self.notify("API not available", severity="error")
            return

        result = await self.app.client.some_call()
        self.notify("Success", severity="information")
    except TimeoutError:
        self.notify("Request timed out", severity="error")
    except ConnectionError:
        self.notify("Connection failed", severity="error")
    except ValueError as e:
        self.notify(f"Invalid input: {e}", severity="error")
    except Exception as e:
        self.log(f"Unexpected error: {e}")
        self.notify("An unexpected error occurred", severity="error")
```

**Benefits**:
- Users see notifications for all errors
- Developers see detailed logs
- Specific error types handled differently when needed

---

### 2.3 Extract Constants & Magic Numbers

**Problem**: Hardcoded values scattered throughout code.

**Current hardcoded values**:
- `limit=100` in app.py (lines 133, 137) - API result limit
- `"━━ {feed_title} ━━"` separator format (entry_list.py:188)
- `"─" * 80` separator in entry_reader.py (lines 76, 249)
- `sort_modes = ["date", "feed", "status"]` (entry_list.py:261)

**Solution**: Create constants file or config section
```python
# In miniflux_tui/constants.py:
"""Application constants."""

# API Limits
DEFAULT_ENTRY_LIMIT = 100

# UI Constants
FEED_HEADER_FORMAT = "━━ {feed_title} ━━"
CONTENT_SEPARATOR = "─" * 80

# Sorting
SORT_MODES = ["date", "feed", "status"]
DEFAULT_SORT = "date"

# Display
STAR_ICON_FILLED = "★"
STAR_ICON_EMPTY = "☆"
UNREAD_ICON = "●"
READ_ICON = "○"

# Colors (from config)
DEFAULT_UNREAD_COLOR = "cyan"
DEFAULT_READ_COLOR = "gray"
```

Usage:
```python
# Before:
limit=100
separator = "━━ {feed_title} ━━"
SEPARATOR_CHAR = "─" * 80
sort_modes = ["date", "feed", "status"]

# After:
from miniflux_tui.constants import (
    DEFAULT_ENTRY_LIMIT, FEED_HEADER_FORMAT,
    CONTENT_SEPARATOR, SORT_MODES
)

limit=DEFAULT_ENTRY_LIMIT
separator = FEED_HEADER_FORMAT
SEPARATOR_CHAR = CONTENT_SEPARATOR
sort_modes = SORT_MODES
```

---

### 2.4 Add Comprehensive Error Handling to API Client

**Problem**: No retry logic, no timeout handling, no response validation.

**Current issues**:
- Network transients cause immediate failure
- No backoff strategy
- `allow_invalid_certs` parameter accepted but unused

**Improvements**:
```python
# In api/client.py:
import asyncio
from typing import TypeVar, Callable, Any

T = TypeVar('T')

async def _call_with_retry(
    self,
    func: Callable[..., T],
    max_retries: int = 3,
    backoff_factor: float = 1.0,
) -> T:
    """Call function with exponential backoff retry logic."""
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await self._run_sync(func)
        except (ConnectionError, TimeoutError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)
        except Exception:
            # Don't retry on other errors
            raise

    raise last_exception

# Use in methods:
async def get_unread_entries(self, limit: int = 100):
    """Get unread entries with retry logic."""
    func = lambda: self.client.get_entries(
        status="unread",
        limit=limit,
        order="published_at",
    )
    return await self._call_with_retry(func)
```

---

## Phase 3: Medium Priority (Medium Impact, Low-Medium Effort)

Estimated effort: 2-4 hours | Impact: Medium

### 3.1 Refactor Long Functions

**Problem**: Some functions are 30+ lines and do multiple things.

#### refactor_populate_list (entry_list.py:121-151)
Currently: 31 lines doing 5 things

**Break into**:
```python
def _populate_list(self):
    """Populate the list with sorted entries."""
    if not self._ensure_list_view():
        return

    self.list_view.clear()
    sorted_entries = self._get_sorted_entries()
    self.sorted_entries = sorted_entries
    self._display_entries(sorted_entries)

def _get_sorted_entries(self) -> list[Entry]:
    """Get entries sorted/grouped according to current settings."""
    entries = self._filter_entries(self.entries)

    if self.group_by_feed:
        return sorted(
            entries,
            key=lambda e: (e.feed.title.lower(), e.published_at),
            reverse=False
        )
    return self._sort_entries(entries)

def _filter_entries(self, entries: list[Entry]) -> list[Entry]:
    """Apply active filters to entries."""
    if self.filter_unread_only:
        return [e for e in entries if e.is_unread]
    if self.filter_starred_only:
        return [e for e in entries if e.starred]
    return entries

def _display_entries(self, entries: list[Entry]):
    """Display entries in list view."""
    if self.group_by_feed:
        self._add_grouped_entries(entries)
    else:
        self._add_flat_entries(entries)
```

#### refactor_refresh_screen (entry_reader.py:223-260)
Currently: 38 lines doing multiple things

**Break into**:
```python
async def refresh_screen(self):
    """Refresh the screen with current entry."""
    scroll = self._get_scroll_container()
    self._clear_scroll_content(scroll)
    self._mount_entry_content(scroll)
    scroll.scroll_home(animate=False)

def _clear_scroll_content(self, scroll: VerticalScroll):
    """Remove all children from scroll container."""
    for child in scroll.children:
        child.remove()

def _mount_entry_content(self, scroll: VerticalScroll):
    """Mount entry content widgets."""
    self._mount_title(scroll)
    self._mount_metadata(scroll)
    self._mount_url(scroll)
    self._mount_separator(scroll)
    self._mount_content(scroll)

def _mount_title(self, scroll: VerticalScroll):
    """Mount entry title widget."""
    star_icon = STAR_ICON_FILLED if self.entry.starred else STAR_ICON_EMPTY
    scroll.mount(Static(
        f"[bold cyan]{star_icon} {self.entry.title}[/bold cyan]",
        classes="entry-title",
    ))

# ... other _mount_* methods ...
```

---

### 3.2 Add Input Validation

**Problem**: No validation of config or API responses.

**Add to config.py**:
```python
def validate_config(config: dict) -> tuple[bool, str]:
    """Validate configuration dictionary."""
    required = ["server_url", "api_key"]

    for field in required:
        if field not in config:
            return False, f"Missing required field: {field}"

    # Validate URL format
    if not config["server_url"].startswith(("http://", "https://")):
        return False, "server_url must start with http:// or https://"

    # Validate API key is not empty
    if not config["api_key"].strip():
        return False, "api_key cannot be empty"

    return True, "Configuration valid"
```

---

### 3.3 Improve Inline Documentation

**Problem**: Complex logic lacks inline comments.

**Example - sorting logic (entry_list.py:149-171)**:
```python
def _sort_entries(self, entries: list[Entry]) -> list[Entry]:
    """Sort entries based on current sort mode."""
    if self.current_sort == "feed":
        # Sort by feed name (A-Z), then by date (newest first within each feed)
        return sorted(
            entries,
            key=lambda e: (e.feed.title.lower(), -e.published_at.timestamp()),
            reverse=True,
        )
    if self.current_sort == "date":
        # Sort by published date (newest first)
        return sorted(entries, key=lambda e: e.published_at, reverse=True)
    if self.current_sort == "status":
        # Sort by read status (unread first), then by date (oldest first)
        # This keeps unread entries prominent but in chronological order
        return sorted(
            entries,
            key=lambda e: (e.is_read, e.published_at),
            reverse=False,
        )
    return entries
```

---

## Phase 4: Lower Priority (Nice-to-Have Improvements)

Estimated effort: 8+ hours | Impact: Medium

### 4.1 Add Test Suite

**Current state**: Zero tests, pytest removed from dependencies

**Recommendation**: Add pytest back and create minimal test suite
```bash
tests/
├── conftest.py                  # Pytest fixtures
├── test_api_client.py           # API client tests
├── test_config.py               # Config loading/validation
├── test_data_models.py          # Entry/Feed models
└── test_ui_screens.py           # Basic screen tests (harder)
```

**Example test**:
```python
# tests/test_config.py
import pytest
from miniflux_tui.config import Config, validate_config

def test_validate_config_missing_required_field():
    """Config validation fails without server_url."""
    config = {"api_key": "test-key"}
    valid, msg = validate_config(config)
    assert not valid
    assert "server_url" in msg

def test_validate_config_invalid_url():
    """Config validation fails with invalid URL."""
    config = {
        "server_url": "invalid-url",
        "api_key": "test-key"
    }
    valid, msg = validate_config(config)
    assert not valid
    assert "http" in msg
```

**Priority**: Medium - good to have but project works without tests

---

### 4.2 Performance: Optimize Screen Refresh

**Current approach**: Full widget remount on every refresh
```python
# Current (inefficient):
for child in scroll.children:
    child.remove()  # Remove all
scroll.mount(...)   # Remount all
```

**Better approach**: Update only changed widgets
```python
async def refresh_screen(self):
    """Refresh only changed content."""
    # Update title if changed
    title_widget = self.query_one("Static.entry-title")
    star_icon = STAR_ICON_FILLED if self.entry.starred else STAR_ICON_EMPTY
    title_widget.update(f"[bold cyan]{star_icon} {self.entry.title}[/bold cyan]")

    # Update metadata
    meta_widget = self.query_one("Static.entry-meta")
    meta_widget.update(
        f"[dim]{self.entry.feed.title} | {self.entry.published_at.strftime('%Y-%m-%d %H:%M')}[/dim]"
    )

    # Update content (heavier operation)
    content = self._html_to_markdown(self.entry.content)
    markdown = self.query_one(Markdown)
    markdown.update(content)
```

**Benefit**: ~50% faster refresh on navigation (200ms → 100ms estimates)

---

### 4.3 Add Pagination/Infinite Scroll

**Current limitation**: Loads only 100 entries max

**Enhancement**: Load more on scroll
```python
# In EntryListScreen:
def on_list_view_highlighted(self, event: ListView.Highlighted):
    """Load more entries when approaching end of list."""
    if not self.sorted_entries:
        return

    # Check if near end (within 10 items)
    if event.cursor_location >= len(self.sorted_entries) - 10:
        self.app.call_later(self._load_more_entries)

async def _load_more_entries(self):
    """Load additional entries from API."""
    try:
        additional = await self.app.client.get_unread_entries(
            limit=100,
            offset=len(self.entries)
        )
        self.entries.extend(additional)
        self._populate_list()
        self.notify(f"Loaded {len(additional)} more entries")
    except Exception as e:
        self.notify(f"Error loading more: {e}", severity="error")
```

---

### 4.4 Add Loading Indicators

**Current limitation**: No feedback during API calls

**Enhancement**:
```python
async def action_refresh(self):
    """Refresh the entry list from API."""
    try:
        self.app.notify("⏳ Refreshing entries...")
        await self.app.load_entries(self.app.current_view)
        self.app.notify("✓ Entries refreshed", severity="information")
    except Exception as e:
        self.app.notify(f"✗ Refresh failed: {e}", severity="error")
```

---

### 4.5 Implement Undo/Redo for Status Changes

**Current behavior**: Changes are immediate and irreversible

**Enhancement**: Store change history
```python
class StatusChangeUndo:
    """Manage undo history for status changes."""
    def __init__(self, max_history: int = 20):
        self.history: list[tuple[int, str, str]] = []  # (entry_id, old_status, new_status)
        self.max_history = max_history

    def record(self, entry_id: int, old_status: str, new_status: str):
        """Record a status change."""
        self.history.append((entry_id, old_status, new_status))
        if len(self.history) > self.max_history:
            self.history.pop(0)

    async def undo(self, client, entry_list):
        """Undo last change."""
        if not self.history:
            return False

        entry_id, old_status, _ = self.history.pop()
        await client.change_entry_status(entry_id, old_status)

        # Update local entry
        for entry in entry_list:
            if entry.id == entry_id:
                entry.status = old_status
                return True
        return False
```

Add keybinding: `Binding("ctrl+z", "undo_change", "Undo")`

---

## Implementation Timeline

### Week 1: Phase 1 (4 hours)
- [ ] Implement API calls for toggle_read/toggle_star
- [ ] Implement filtering (show_unread/show_starred)
- [x] Fix keyboard shortcut documentation ✅ COMPLETED
- [x] Implement save_entry feature (e key) ✅ COMPLETED
- [x] Add refresh alias (, key) ✅ COMPLETED
- [ ] Clean up TODO comments (partially done)

### Week 2: Phase 2 Part 1 (4 hours)
- [ ] Extract repeated code patterns
- [ ] Improve error handling consistency
- [ ] Extract constants

### Week 3: Phase 2 Part 2 (4 hours)
- [ ] Add retry logic to API client
- [ ] Input validation for config
- [ ] Inline documentation improvements

### Week 4: Phase 3 (4 hours)
- [ ] Refactor long functions
- [ ] Add basic tests
- [ ] Performance monitoring

### Future: Phase 4 (as time permits)
- Pagination
- Loading indicators
- Performance optimization
- Advanced features

---

## Quick Win Checklist

Copy this to your issue tracker or notes:

**Phase 1 - API Integration:**
- [ ] Fix `action_toggle_read()` - add API call
- [ ] Fix `action_toggle_star()` - add API call
- [ ] Implement `action_show_unread()`
- [ ] Implement `action_show_starred()`

**Phase 1 - Documentation:** ✅ COMPLETED
- [x] Update help.py keyboard shortcuts (J/K, e, ,)
- [x] Update README.md keyboard shortcuts (J/K, e, ,)
- [x] Implement save_entry feature (e key)
- [x] Add refresh alias (, key)

**Phase 2 - Code Quality:**
- [ ] Create constants.py file
- [ ] Create utils.py with helper functions
- [ ] Extract _get_scroll_container() helper
- [ ] Extract _ensure_list_view() helper
- [ ] Extract api_call() context manager
- [ ] Update error handling in entry_list.py
- [ ] Add inline comments to sorting logic
- [ ] Add config validation
- [ ] Remove/update misleading TODO comments

---

## Resource Links

- **Textual Framework**: [https://textual.textualize.io/](https://textual.textualize.io/)
- **Miniflux API**: [https://miniflux.app/api.html](https://miniflux.app/api.html)
- **Python Best Practices**: [https://pep8.org/](https://pep8.org/)
- **Async/Await Pattern**: [https://docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html)

---

## Questions for Project Owner

1. **Testing Strategy**: Would you like to add a test suite? Start minimal or comprehensive?
2. **Performance**: Are there reports of lag with large entry counts (500+)?
3. **Feature Priority**: Which improvements align best with your roadmap?
4. **Backward Compatibility**: Any concerns about breaking changes?
5. **Maintenance Cadence**: How frequently can you merge improvements?

---

## Notes

- **Total estimated work**: ~24-32 hours across all phases
- **Recommended focus**: Phases 1-2 for stability and user experience
- **Low-risk items**: Phase 1 and constants extraction (Phase 2.3)
- **High-risk items**: Large refactors without test coverage (Phase 3.1)
- **Quick wins**: Phase 1 items (1-2 hours each)
