# Pre-Release Testing Checklist for miniflux-tui-py

This checklist contains essential manual tests that MUST be completed before any minor (0.x.0) or major (x.0.0) release. This is NOT required for patch releases (0.0.x).

**Version being tested:** ____________

**Tester:** ____________

**Date:** ____________

**Platform(s):** [ ] Linux  [ ] macOS  [ ] Windows

---

## Critical Functionality (MUST PASS)

These tests verify core functionality that cannot be broken in any release.

### Application Launch and Configuration
- [ ] `miniflux-tui --init` creates config file successfully
- [ ] `miniflux-tui --check-config` validates configuration
- [ ] Application launches with valid configuration
- [ ] Application exits cleanly with `q`

### Entry List - Core Navigation
- [ ] `j`/`k` keys navigate up/down through entries
- [ ] `Enter` opens entry reader
- [ ] Entry reader displays content correctly
- [ ] `b` or `Esc` returns to entry list from reader

### Entry List - Core Actions
- [ ] `m` toggles read/unread status (API call succeeds)
- [ ] `*` toggles star status (API call succeeds)
- [ ] Status icons (●/○) and colors update correctly
- [ ] Changes persist after application restart

### Entry Reader - Core Functions
- [ ] Entry content displays with proper Markdown formatting
- [ ] `j`/`k` scrolls content up/down
- [ ] `J`/`K` navigates to next/previous entry
- [ ] Entry is automatically marked as read when opened

---

## Major Features (MUST WORK)

These features represent significant functionality that defines the application.

### Sorting and Grouping
- [ ] `s` cycles through all sort modes (date, feed, status)
- [ ] Each sort mode orders entries correctly
- [ ] `g` toggles feed grouping on/off
- [ ] Grouped mode displays feed headers correctly
- [ ] `h`/`l` collapse/expand feeds in grouped mode
- [ ] `j`/`k` navigation skips collapsed entries correctly

### Category Support (if applicable)
- [ ] `Shift+C` toggles category grouping
- [ ] Categories display with correct headers and formatting
- [ ] Category folding works correctly

### Filtering and Views
- [ ] `u` loads and displays unread entries only
- [ ] `t` loads and displays starred entries only
- [ ] Entry counts match server state

### Feed Operations
- [ ] `r` refreshes current feed on server
- [ ] `Shift+R` refreshes all feeds on server
- [ ] Entries reload after refresh operations

---

## UI and Screens

### Help Screen
- [ ] `?` opens help screen from entry list
- [ ] `?` opens help screen from entry reader
- [ ] Help displays all keyboard shortcuts correctly
- [ ] System information loads and displays
- [ ] `Esc` or `q` closes help screen

### Status Screen
- [ ] `i` opens status screen
- [ ] Server information displays correctly
- [ ] Feed health statistics display
- [ ] Problematic feeds list shows errors (if any exist)
- [ ] `r` refreshes status data
- [ ] `Esc` or `q` closes status screen

---

## Cross-Platform Testing (if multi-platform release)

Test on each target platform:

### Linux
- [ ] All critical functionality passes
- [ ] Config path: `~/.config/miniflux-tui/config.toml`
- [ ] Terminal rendering correct

### macOS
- [ ] All critical functionality passes
- [ ] Config path: `~/.config/miniflux-tui/config.toml`
- [ ] Terminal rendering correct (Terminal.app and iTerm2)

### Windows
- [ ] All critical functionality passes
- [ ] Config path: `%APPDATA%\miniflux-tui\config.toml`
- [ ] Windows Terminal rendering correct

---

## Error Handling and Edge Cases

### API Errors
- [ ] Invalid API key shows clear error message
- [ ] Unreachable server shows error notification
- [ ] Network errors during operations handled gracefully
- [ ] Application doesn't crash on API failures

### Empty States
- [ ] No unread entries: appropriate message shown
- [ ] No starred entries: appropriate message shown
- [ ] No feeds with errors: status screen shows "all healthy"

### Large Datasets
- [ ] 100+ entries load and display correctly
- [ ] Navigation smooth with large entry lists
- [ ] Grouping works with 20+ feeds

---

## Performance Benchmarks

Record approximate times for these operations (for performance regression tracking):

- [ ] Application startup time: ______ seconds
- [ ] Load 100 unread entries: ______ seconds
- [ ] Toggle sort mode with 100 entries: ______ seconds
- [ ] Toggle grouping with 20 feeds: ______ seconds
- [ ] Refresh all feeds: ______ seconds

**Performance acceptable:** [ ] Yes  [ ] No

---

## Documentation and Installation

### Installation
- [ ] `uv pip install miniflux-tui-py` works from PyPI
- [ ] `uv sync` works for development setup
- [ ] All dependencies install without errors

### Documentation
- [ ] README.md installation instructions accurate
- [ ] CHANGELOG.md includes all changes for this version
- [ ] Help screen matches actual key bindings
- [ ] Configuration options documented

---

## Version-Specific Features

List any new features introduced in this release and verify they work:

1. Feature: ______________________________
- [ ] Works as designed
- [ ] Documented
- [ ] Tested

2. Feature: ______________________________
- [ ] Works as designed
- [ ] Documented
- [ ] Tested

3. Feature: ______________________________
- [ ] Works as designed
- [ ] Documented
- [ ] Tested

---

## Regression Testing

If fixing critical bugs, verify the original issue is resolved:

1. Issue #____: ______________________________
    - [ ] Original bug no longer occurs
    - [ ] Fix doesn't introduce new issues

2. Issue #____: ______________________________
    - [ ] Original bug no longer occurs
    - [ ] Fix doesn't introduce new issues

---

## Final Checks

### Code Quality
- [ ] All CI/CD checks passing on GitHub
- [ ] Test coverage ≥ 60%
- [ ] No critical linting or type errors
- [ ] Pre-commit hooks pass

### Release Preparation
- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG.md updated with all changes
- [ ] Git tag created (format: `v0.x.0`)
- [ ] All commits follow conventional commit format

---

## Test Results

**Overall Status:** [ ] PASS - Ready for Release  [ ] FAIL - Not Ready

### Critical Issues Found (must be fixed before release)
1.
2.
3.

### Non-Critical Issues (can be deferred to patch release)
1.
2.
3.

### Notes
---
---
---

---

## Approval

**Tested by:** ______________________

**Date:** ______________________

**Approved for Release:** [ ] Yes  [ ] No

**Signatures:**

Tester: ______________________ Date: __________

Maintainer: ______________________ Date: __________

---

**Estimated Testing Time:** 45-60 minutes for complete checklist

**Priority Levels:**
- ✅ **Critical**: Must pass for release
- ⚠️ **Major**: Should pass for release
- ℹ️ **Optional**: Good to verify but not blocking
