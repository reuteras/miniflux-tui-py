# Development Plan - miniflux-tui-py

## Quick Summary

This project needs improvements across 4 phases. Total estimated work: **24-32 hours**.

Focus on **Phase 1** first (4 hours) for immediate impact on functionality and user experience.

---

## Phase 1: Immediate Priority ⚡

**Estimated: 2-4 hours | Impact: HIGH | Do this first!**

### 1. Fix Missing API Calls (2 hours)

**Files**: `miniflux_tui/ui/screens/entry_list.py`

#### Problem
- `action_toggle_read()` - toggles local state but doesn't save to API
- `action_toggle_star()` - toggles local state but doesn't save to API

#### Solution
Make both methods `async` and call the API:
```python
async def action_toggle_read(self):
    """Toggle read/unread status."""
    if not self.list_view:
        return

    highlighted = self.list_view.highlighted_child
    if highlighted and isinstance(highlighted, EntryListItem):
        try:
            new_status = "read" if highlighted.entry.is_unread else "unread"
            await self.app.client.change_entry_status(
                highlighted.entry.id, new_status
            )
            highlighted.entry.status = new_status
            self._populate_list()
            self.notify(f"Entry marked as {new_status}")
        except Exception as e:
            self.notify(f"Error updating status: {e}", severity="error")

async def action_toggle_star(self):
    """Toggle star status."""
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

**Why**: Users expect m/\* keys to save changes to the server immediately.

---

### 2. Implement Filtering (1.5 hours)

**Files**: `miniflux_tui/ui/screens/entry_list.py`

#### Problem
- `action_show_unread()` - empty stub (line 268)
- `action_show_starred()` - empty stub (line 274)
- Keys 'u' and 't' don't work

#### Solution
Add filter state and filtering logic:

```python
# In __init__:
self.filter_unread_only = False
self.filter_starred_only = False

# Add methods:
def action_show_unread(self):
    """Toggle showing only unread entries."""
    self.filter_unread_only = not self.filter_unread_only
    self.filter_starred_only = False
    self._populate_list()
    status = "unread only" if self.filter_unread_only else "all"
    self.notify(f"Showing {status}")

def action_show_starred(self):
    """Toggle showing only starred entries."""
    self.filter_starred_only = not self.filter_starred_only
    self.filter_unread_only = False
    self._populate_list()
    status = "starred only" if self.filter_starred_only else "all"
    self.notify(f"Showing {status}")

# Modify _populate_list() to filter before sorting:
def _populate_list(self):
    """Populate the list with sorted entries."""
    if not self.list_view:
        try:
            self.list_view = self.query_one(ListView)
        except Exception as e:
            self.log(f"Failed to get list_view: {e}")
            return

    self.list_view.clear()

    # Apply filters
    entries = self.entries
    if self.filter_unread_only:
        entries = [e for e in entries if e.is_unread]
    elif self.filter_starred_only:
        entries = [e for e in entries if e.starred]

    # Sort entries (existing logic)
    if self.group_by_feed:
        sorted_entries = sorted(
            entries,
            key=lambda e: (e.feed.title.lower(), e.published_at),
            reverse=False
        )
    else:
        sorted_entries = self._sort_entries(entries)

    self.sorted_entries = sorted_entries

    if self.group_by_feed:
        self._add_grouped_entries(sorted_entries)
    else:
        self._add_flat_entries(sorted_entries)
```

**Why**: Features advertised in help/README should actually work.

---

### 3. Fix Documentation (1 hour)

**Files**: `miniflux_tui/ui/screens/help.py`, `README.md`

#### Problem A: help.py shows wrong keyboard shortcuts
- Says 'n'/'p' for next/previous entry
- Actual bindings are 'J'/'K' (uppercase)

#### Solution A
```python
# In help.py, around line 46-47, change from:
"n                     : Next entry",
"p                     : Previous entry",

# To:
"J                     : Next entry",
"K                     : Previous entry",

# Add missing:
"g                     : Toggle group by feed",
"s                     : Cycle sort mode",
```

#### Problem B: README lists non-existent features
- Line ~65: "f - Filter by feed" doesn't exist

#### Solution B
```markdown
# Remove "f - Filter by feed"
# Add correct shortcuts:
- u - Show unread entries
- t - Show starred entries
- g - Group by feed
- s - Cycle sort mode
```

**Why**: Documentation mismatch confuses new users.

---

### 4. Remove Misleading Comments (0.5 hours)

**File**: `miniflux_tui/ui/screens/entry_list.py`

#### Problem
Line 278 says "TODO: Push help screen" but code actually does it.

#### Solution
Remove the outdated TODO or update to reflect current implementation.

**Why**: Keeps codebase honest and prevents confusion.

---

## Phase 2: High Priority 🔧

**Estimated: 8-12 hours | Impact: HIGH**

### 2.1 Extract Repeated Code Patterns (4 hours)

**Problem**: Code duplication in 4 patterns across the codebase.

#### Pattern 1: Scroll Container Access (entry_reader.py)
Appears 5 times. Create helper:
```python
def _get_scroll_container(self) -> VerticalScroll:
    """Get scroll container, initializing if needed."""
    if not self.scroll_container:
        self.scroll_container = self.query_one(VerticalScroll)
    return self.scroll_container
```

#### Pattern 2: ListView Access (entry_list.py)
Appears 5 times. Create helper:
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

#### Pattern 3: Client Access Check (entry_reader.py)
Appears 4 times. Consider context manager approach or consistent try/except.

#### Pattern 4: Star Icon
Appears 3+ times:
```python
# Instead of repeating:
star_icon = "★" if entry.starred else "☆"

# Use constants:
STAR_ICON_FILLED = "★"
STAR_ICON_EMPTY = "☆"
```

**Impact**: Reduces duplication by ~80 lines, easier to maintain.

---

### 2.2 Improve Error Handling (2 hours)

**Problem**: Inconsistent error handling across screens.

**Current**: Entry list uses only `log()`, entry reader uses `log()` + `notify()`

**Solution**: Standardize on dual reporting for user-facing actions
```python
async def action_something(self):
    """Description."""
    try:
        if not hasattr(self.app, "client") or not self.app.client:
            self.notify("API not available", severity="error")
            return

        result = await self.app.client.some_call()
        self.notify("Success", severity="information")
    except Exception as e:
        self.log(f"Error: {e}")
        self.notify("An error occurred", severity="error")
```

**Why**: Users see notifications, developers see logs.

---

### 2.3 Extract Constants (2 hours)

**Problem**: Magic numbers and hardcoded strings scattered throughout.

**Create**: `miniflux_tui/constants.py`
```python
"""Application constants."""

# API
DEFAULT_ENTRY_LIMIT = 100

# UI Text
FEED_HEADER_FORMAT = "━━ {feed_title} ━━"
CONTENT_SEPARATOR = "─" * 80

# Icons
STAR_FILLED = "★"
STAR_EMPTY = "☆"
UNREAD_ICON = "●"
READ_ICON = "○"

# Sorting
SORT_MODES = ["date", "feed", "status"]
DEFAULT_SORT = "date"

# Colors
DEFAULT_UNREAD_COLOR = "cyan"
DEFAULT_READ_COLOR = "gray"
```

Then use throughout:
```python
from miniflux_tui.constants import STAR_FILLED, STAR_EMPTY

star_icon = STAR_FILLED if entry.starred else STAR_EMPTY
```

**Why**: Single source of truth, easier to customize later.

---

### 2.4 Add Retry Logic to API Client (2-4 hours)

**Problem**: Network errors cause immediate failure, no recovery.

**Solution**: Add exponential backoff retry
```python
# In api/client.py
import asyncio

async def _call_with_retry(self, func, max_retries=3, backoff_factor=1.0):
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
            raise  # Don't retry on other errors

    raise last_exception

# Use in methods:
async def get_unread_entries(self, limit=100):
    """Get unread entries with retry logic."""
    func = lambda: self.client.get_entries(
        status="unread", limit=limit, order="published_at"
    )
    return await self._call_with_retry(func)
```

**Why**: Improves reliability on spotty connections.

---

## Phase 3: Medium Priority 📚

**Estimated: 4 hours | Impact: MEDIUM**

### 3.1 Refactor Long Functions (2 hours)

#### Before: `_populate_list()` - 31 lines
- Gets ListView reference
- Clears list
- Sorts entries
- Stores entries
- Adds entries

#### After: Break into smaller methods
```python
def _populate_list(self):
    if not self._ensure_list_view():
        return
    self.list_view.clear()
    sorted_entries = self._get_sorted_entries()
    self.sorted_entries = sorted_entries
    self._display_entries(sorted_entries)

def _get_sorted_entries(self) -> list[Entry]:
    entries = self._filter_entries(self.entries)
    if self.group_by_feed:
        return sorted(
            entries,
            key=lambda e: (e.feed.title.lower(), e.published_at),
            reverse=False
        )
    return self._sort_entries(entries)

def _filter_entries(self, entries: list[Entry]) -> list[Entry]:
    if self.filter_unread_only:
        return [e for e in entries if e.is_unread]
    if self.filter_starred_only:
        return [e for e in entries if e.starred]
    return entries
```

**Why**: Easier to understand, test, and maintain.

---

### 3.2 Add Inline Documentation (1 hour)

Add comments explaining complex logic:
```python
def _sort_entries(self, entries: list[Entry]) -> list[Entry]:
    """Sort entries based on current sort mode."""
    if self.current_sort == "feed":
        # Sort by feed name (A-Z), then date (newest first)
        return sorted(
            entries,
            key=lambda e: (e.feed.title.lower(), -e.published_at.timestamp()),
            reverse=True,
        )
    if self.current_sort == "date":
        # Sort by published date (newest first)
        return sorted(entries, key=lambda e: e.published_at, reverse=True)
    if self.current_sort == "status":
        # Sort by read status (unread first), then date (oldest first)
        return sorted(
            entries,
            key=lambda e: (e.is_read, e.published_at),
            reverse=False,
        )
    return entries
```

**Why**: Future maintainers (including you!) understand the logic.

---

### 3.3 Add Config Validation (1 hour)

```python
# In config.py
def validate_config(config: dict) -> tuple[bool, str]:
    """Validate configuration dictionary."""
    required = ["server_url", "api_key"]

    for field in required:
        if field not in config:
            return False, f"Missing required field: {field}"

    if not config["server_url"].startswith(("http://", "https://")):
        return False, "server_url must start with http:// or https://"

    if not config["api_key"].strip():
        return False, "api_key cannot be empty"

    return True, "Configuration valid"
```

**Why**: Catch errors early with helpful messages.

---

## Phase 4: Nice-to-Have 🎁

**Estimated: 8+ hours | Impact: MEDIUM-LOW**

### 4.1 Add Test Suite
- Start with basic API client tests
- Add config validation tests
- Build from there

### 4.2 Performance: Optimize Screen Refresh
- Update only changed widgets instead of full remount
- Estimated: ~50% faster (200ms → 100ms)

### 4.3 Implement Pagination
- Load more entries as user scrolls
- Support 500+ entries

### 4.4 Add Loading Indicators
- Visual feedback during API calls
- Better UX

### 4.5 Implement Undo/Redo
- Store change history
- Let users undo status changes

---

## Quick Reference: What to Do

### Today (30 minutes)
```
□ Read this Plan.md
□ Identify which phase to start with
□ Create git branch for Phase 1
```

### Week 1: Phase 1 (4 hours total)
```
□ Fix toggle_read() - add API call (1 hour)
□ Fix toggle_star() - add API call (1 hour)
□ Implement filtering - show_unread/show_starred (1.5 hours)
□ Fix keyboard shortcut documentation (1 hour)
□ Remove misleading TODOs (0.5 hours)
□ Test all changes
□ Create commit
□ Submit PR
```

### Week 2-3: Phase 2 (8-12 hours total)
```
□ Create constants.py
□ Extract repeated code patterns
□ Improve error handling consistency
□ Add retry logic to API client
□ Test all changes
□ Submit PR
```

### Week 4+: Phase 3 & 4 (as time permits)
```
□ Refactor long functions
□ Add tests
□ Performance optimizations
□ Nice-to-have features
```

---

## Issues By Severity

### 🔴 Critical (Must Fix)
1. Empty stub methods (show_unread, show_starred)
2. Missing API calls (toggle_read, toggle_star)
3. Inconsistent keyboard shortcut documentation
4. Test coverage: 0%

### 🟠 High (Should Fix Soon)
1. Code duplication (4 patterns, 80+ lines)
2. Silent failures (no user notification)
3. Hardcoded magic numbers
4. Long complex functions

### 🟡 Medium (Nice to Have)
1. Performance optimization
2. Inline documentation
3. Input validation
4. Better error messages

### 🟢 Low (Can Wait)
1. Pagination
2. Loading indicators
3. Undo/redo
4. Advanced features

---

## File Locations

| Task | File |
|------|------|
| Fix API calls | `miniflux_tui/ui/screens/entry_list.py` (lines 216-244) |
| Implement filtering | `miniflux_tui/ui/screens/entry_list.py` (lines 268-274) |
| Fix help shortcuts | `miniflux_tui/ui/screens/help.py` (lines 46-51) |
| Fix README | `README.md` (lines 55-81) |
| Extract helpers | `miniflux_tui/ui/screens/entry_*.py` |
| Create constants | `miniflux_tui/constants.py` (new file) |
| Improve API client | `miniflux_tui/api/client.py` |

---

## Success Criteria

After Phase 1:
- ✅ m/\* keys save changes to API
- ✅ u/t keys filter entries
- ✅ Help screen shows correct shortcuts
- ✅ README documents actual features

After Phase 2:
- ✅ No code duplication in patterns
- ✅ Consistent error handling
- ✅ Constants centralized
- ✅ Retry logic on network errors

After Phase 3:
- ✅ Functions <20 lines or single responsibility
- ✅ Complex logic documented
- ✅ Config validated on load
- ✅ Basic tests written

---

## Tips for Success

1. **Start small**: Do Phase 1 before Phase 2
2. **Test as you go**: Don't wait until end to test
3. **Commit frequently**: After each major change
4. **One PR per phase**: Easier to review
5. **Write tests early**: Easier to refactor with tests
6. **Ask questions**: Unclear requirements? Ask before coding

---

## Resources

- Textual docs: https://textual.textualize.io/
- Miniflux API: https://miniflux.app/api.html
- Python asyncio: https://docs.python.org/3/library/asyncio.html

---

## Related Documents

- `CLAUDE.md` - Project architecture and overview
- `IMPROVEMENTS.md` - Detailed analysis with code examples
- This file - Quick execution plan
