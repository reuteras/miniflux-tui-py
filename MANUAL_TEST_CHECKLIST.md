# Manual Testing Checklist for miniflux-tui-py

This comprehensive checklist covers all features and functions of the miniflux-tui-py application that should be tested manually by a human user.

## Prerequisites

- [ ] Miniflux server running and accessible
- [ ] Valid API key generated from Miniflux web interface
- [ ] Multiple feeds with various states (unread, read, starred, with errors)
- [ ] Python 3.11+ installed
- [ ] `uv` package manager installed

---

## 1. Configuration and Setup

### Initial Configuration
- [ ] Run `miniflux-tui --init` to create default config
- [ ] Verify config file created at correct OS-specific location:
  - Linux: `~/.config/miniflux-tui/config.toml`
  - macOS: `~/Library/Application Support/miniflux-tui/config.toml`
  - Windows: `%APPDATA%\miniflux-tui\config.toml`
- [ ] Edit config file with valid server URL and API key
- [ ] Run `miniflux-tui --check-config` to verify configuration
- [ ] Verify all config settings displayed correctly

### Configuration Options
- [ ] Test with `allow_invalid_certs = true`
- [ ] Test with `allow_invalid_certs = false`
- [ ] Test custom theme colors (unread_color, read_color)
- [ ] Test different default_sort modes (date, feed, status)
- [ ] Test `default_group_by_feed = true`
- [ ] Test `default_group_by_feed = false`
- [ ] Test `group_collapsed = true`
- [ ] Test `group_collapsed = false`

### Error Handling
- [ ] Test with missing config file
- [ ] Test with invalid server URL
- [ ] Test with invalid API key
- [ ] Test with unreachable server
- [ ] Test with malformed TOML config

---

## 2. Application Launch

### Startup
- [ ] Launch with `miniflux-tui`
- [ ] Verify application loads without errors
- [ ] Verify "Loading data..." notification appears
- [ ] Verify entries load and display
- [ ] Verify categories load (if available)
- [ ] Check application responds to keyboard input

### Initial View
- [ ] Verify header displays correctly
- [ ] Verify footer with key bindings displays
- [ ] Verify entry list populates
- [ ] Verify default sort/grouping applied per config

---

## 3. Entry List Screen - Navigation

### Basic Navigation
- [ ] Press `j` to move cursor down
- [ ] Press `k` to move cursor up
- [ ] Press `↓` (down arrow) to move down
- [ ] Press `↑` (up arrow) to move up
- [ ] Navigate through multiple entries
- [ ] Verify cursor position highlighted correctly
- [ ] Verify scroll follows cursor position

### Entry Selection
- [ ] Press `Enter` on an entry
- [ ] Verify entry reader screen opens
- [ ] Verify correct entry content displayed
- [ ] Return to list and verify cursor position preserved

---

## 4. Entry List Screen - Status Management

### Mark Read/Unread
- [ ] Select an unread entry
- [ ] Press `m` to mark as read
- [ ] Verify icon changes from ● to ○
- [ ] Verify color changes to read_color
- [ ] Press `m` again to mark as unread
- [ ] Verify icon changes back to ●
- [ ] Verify color changes to unread_color
- [ ] Verify success notification appears

### Toggle Star
- [ ] Select an entry
- [ ] Press `*` to star the entry
- [ ] Verify star icon (★) appears
- [ ] Press `*` again to unstar
- [ ] Verify star icon (☆) appears
- [ ] Verify success notification appears

### Save Entry
- [ ] Select an entry
- [ ] Press `e` to save entry
- [ ] Verify success notification appears
- [ ] Note: Requires third-party service configured in Miniflux

---

## 5. Entry List Screen - Sorting

### Cycle Sort Modes
- [ ] Press `s` to cycle sort mode
- [ ] Verify sort changes to next mode
- [ ] Verify subtitle updates to show current sort
- [ ] Test all sort modes:
  - [ ] **Date**: Newest entries first
  - [ ] **Feed**: Alphabetical by feed, then by date
  - [ ] **Status**: Unread first, then by date (oldest first)
- [ ] Verify entries reorder correctly for each mode
- [ ] Verify cursor position updates appropriately

---

## 6. Entry List Screen - Grouping by Feed

### Toggle Grouping
- [ ] Press `g` to enable grouping by feed
- [ ] Verify feed headers appear
- [ ] Verify entries grouped under feed names
- [ ] Verify fold indicators show (▼ expanded, ▶ collapsed)
- [ ] Press `g` again to disable grouping
- [ ] Verify flat list restored

### Fold/Unfold Individual Feeds
- [ ] Enable grouping with `g`
- [ ] Navigate to a feed header
- [ ] Press `o` to toggle fold state
- [ ] Verify feed collapses (▶) or expands (▼)
- [ ] Verify entries show/hide correctly
- [ ] Press `h` or `←` on expanded feed
- [ ] Verify feed collapses
- [ ] Press `l` or `→` on collapsed feed
- [ ] Verify feed expands

### Navigate in Grouped Mode
- [ ] With some feeds collapsed
- [ ] Press `j`/`k` to navigate
- [ ] Verify cursor skips hidden entries
- [ ] Verify navigation only stops on visible items
- [ ] Navigate from feed header to entries
- [ ] Navigate from entries to next feed header

### Expand/Collapse All Feeds
- [ ] Enable grouping with `g`
- [ ] Press `Shift+Z` to collapse all feeds
- [ ] Verify all feeds collapse
- [ ] Verify all entries hidden
- [ ] Verify notification appears
- [ ] Press `Shift+G` to expand all feeds
- [ ] Verify all feeds expand
- [ ] Verify all entries visible
- [ ] Verify notification appears

### Cursor Position Preservation
- [ ] Select an entry in a grouped feed
- [ ] Press `Enter` to open entry reader
- [ ] Press `b` or `Esc` to return
- [ ] Verify cursor returns to same entry
- [ ] Collapse a feed while on an entry
- [ ] Open and return from entry reader
- [ ] Verify cursor position preserved

---

## 7. Entry List Screen - Grouping by Category

### Toggle Category Grouping
- [ ] Press `Shift+C` to enable category grouping
- [ ] Verify category headers appear with "[CATEGORY]" label
- [ ] Verify entries grouped under categories
- [ ] Verify feed grouping disabled automatically
- [ ] Press `Shift+C` again to disable
- [ ] Verify category grouping turned off

### With No Categories
- [ ] On a server without categories
- [ ] Press `Shift+C`
- [ ] Verify warning notification: "No categories available"
- [ ] Verify no change to list view

### Category Fold/Unfold
- [ ] Enable category grouping
- [ ] Navigate to category header
- [ ] Press `o` to toggle fold
- [ ] Verify entries under category show/hide
- [ ] Test expand/collapse all with categories

---

## 8. Entry List Screen - Filtering

### Show Unread Only
- [ ] Press `u` to load unread entries
- [ ] Verify "Loading data..." notification
- [ ] Verify only unread entries shown
- [ ] Verify notification shows count
- [ ] Verify entries reload from server

### Show Starred Only
- [ ] Press `t` to load starred entries
- [ ] Verify "Loading data..." notification
- [ ] Verify only starred entries shown
- [ ] Verify notification shows count
- [ ] Verify entries reload from server

### Search Entries
- [ ] Press `/` to toggle search mode
- [ ] Verify notification about search feature
- [ ] Note: Search implementation uses `set_search_term()` method
- [ ] Press `/` again to clear any active search
- [ ] Verify notification: "Search cleared"

---

## 9. Entry List Screen - Refresh Operations

### Refresh Current Feed
- [ ] Select an entry
- [ ] Press `r` or `,` to refresh current feed
- [ ] Verify notification: "Refreshing feed: [feed name]..."
- [ ] Verify notification: "Feed '[feed name]' refreshed on server"
- [ ] Verify notification: "Reloading entries..."
- [ ] Verify entries reload
- [ ] Verify notification: "Entries reloaded"

### Refresh All Feeds
- [ ] Press `Shift+R` to refresh all feeds
- [ ] Verify notification: "Refreshing all feeds..."
- [ ] Wait for completion (may take time)
- [ ] Verify notification: "All feeds refreshed on server"
- [ ] Verify entries reload automatically
- [ ] Verify notification: "Entries reloaded"

### Error Handling
- [ ] Disconnect network temporarily
- [ ] Try to refresh feed
- [ ] Verify error notification appears
- [ ] Reconnect network
- [ ] Verify refresh works again

---

## 10. Entry Reader Screen - Navigation

### Open Entry
- [ ] From entry list, press `Enter` on an entry
- [ ] Verify entry reader opens
- [ ] Verify entry content displays
- [ ] Verify HTML converted to Markdown
- [ ] Verify metadata shown:
  - [ ] Entry title with star icon
  - [ ] Feed name and publish date
  - [ ] Entry URL
  - [ ] Content separator
  - [ ] Article content

### Scroll Content
- [ ] Press `j` to scroll down one line
- [ ] Press `k` to scroll up one line
- [ ] Press `PageDown` to scroll down one page
- [ ] Press `PageUp` to scroll up one page
- [ ] Verify smooth scrolling
- [ ] Verify content doesn't jump unexpectedly

### Navigate Between Entries
- [ ] Open an entry (not the last one)
- [ ] Press `J` (Shift+j) to go to next entry
- [ ] Verify next entry loads
- [ ] Verify content refreshes
- [ ] Press `K` (Shift+k) to go to previous entry
- [ ] Verify previous entry loads
- [ ] On first entry, press `K`
- [ ] Verify warning: "No previous entry"
- [ ] On last entry, press `J`
- [ ] Verify warning: "No next entry"

### Auto-Mark as Read
- [ ] Open an unread entry
- [ ] Verify entry automatically marked as read
- [ ] Return to entry list
- [ ] Verify entry shows as read

---

## 11. Entry Reader Screen - Actions

### Mark as Unread
- [ ] Open a read entry
- [ ] Press `u` to mark as unread
- [ ] Verify notification: "Marked as unread"
- [ ] Return to entry list
- [ ] Verify entry shows as unread

### Toggle Star
- [ ] In entry reader, press `*` to star
- [ ] Verify notification: "Entry starred"
- [ ] Verify star icon updates in title
- [ ] Press `*` again to unstar
- [ ] Verify notification: "Entry unstarred"
- [ ] Verify star icon updates

### Save Entry
- [ ] Press `e` to save entry
- [ ] Verify notification: "Entry saved: [entry title]"
- [ ] Note: Requires third-party service configured

### Open in Browser
- [ ] Press `o` to open in browser
- [ ] Verify default browser opens
- [ ] Verify correct URL loaded
- [ ] Verify notification appears with URL

### Fetch Original Content
- [ ] Press `f` to fetch original content
- [ ] Verify notification: "Fetching original content..."
- [ ] Wait for completion
- [ ] Verify notification: "Original content loaded" or "No original content available"
- [ ] If successful, verify content updates
- [ ] Verify screen refreshes with new content

### Return to List
- [ ] Press `b` to go back
- [ ] Verify entry list screen appears
- [ ] Verify cursor at correct position
- [ ] Press `Esc` to go back
- [ ] Verify same behavior

---

## 12. Help Screen

### Open Help
- [ ] From entry list, press `?`
- [ ] Verify help screen opens
- [ ] From entry reader, press `?`
- [ ] Verify help screen opens

### Help Content
- [ ] Verify keyboard shortcuts displayed for:
  - [ ] Entry List View
  - [ ] Entry Reader View
- [ ] Verify "About" section shows:
  - [ ] Application name and version
  - [ ] Repository URL
  - [ ] License
- [ ] Verify "System Information" section shows:
  - [ ] Python version
  - [ ] Platform
  - [ ] Textual version
  - [ ] Miniflux API version
  - [ ] Miniflux Server version
  - [ ] Username

### Close Help
- [ ] Press `Esc` to close help
- [ ] Verify returns to previous screen
- [ ] Press `q` to close help
- [ ] Verify same behavior

---

## 13. Status Screen

### Open Status
- [ ] From entry list, press `i`
- [ ] Verify status screen opens
- [ ] From entry reader, press `i`
- [ ] Verify status screen opens

### Status Content
- [ ] Verify "Server Information" shows:
  - [ ] Server URL
  - [ ] Server Version
  - [ ] Username
- [ ] Verify "Feed Health" shows:
  - [ ] Total Feeds count
  - [ ] Healthy feeds count
  - [ ] Feeds with errors count
  - [ ] Disabled feeds count
  - [ ] Overall status indicator
- [ ] Verify "Problematic Feeds" section:
  - [ ] If no issues: "No problematic feeds found ✓"
  - [ ] If issues: List of feeds with problems

### Problematic Feeds Details
- [ ] For each problematic feed, verify shows:
  - [ ] Feed title
  - [ ] Status (DISABLED, error count)
  - [ ] Feed URL
  - [ ] Error message (if any)
  - [ ] Last checked timestamp

### Refresh Status
- [ ] Press `r` to refresh status
- [ ] Verify notification: "Status refreshed"
- [ ] Verify data reloads
- [ ] Verify "Refreshing..." message appears briefly

### Close Status
- [ ] Press `Esc` to close
- [ ] Verify returns to previous screen
- [ ] Press `q` to close
- [ ] Verify same behavior

---

## 14. Application-Wide Functions

### Quit Application
- [ ] From entry list, press `q`
- [ ] Verify application exits cleanly
- [ ] From entry reader, press `q`
- [ ] Verify application exits cleanly
- [ ] Press `Ctrl+C` during operation
- [ ] Verify graceful shutdown

### Screen Stack Management
- [ ] Open entry reader → press `?` for help → press `i` for status
- [ ] Verify multiple screens stacked
- [ ] Press `Esc` repeatedly
- [ ] Verify screens pop in reverse order
- [ ] Verify returns to entry list

---

## 15. Edge Cases and Error Handling

### Empty States
- [ ] Test with no unread entries
- [ ] Verify warning: "No unread entries found"
- [ ] Test with no starred entries
- [ ] Verify warning: "No starred entries found"
- [ ] Test with no feeds
- [ ] Verify appropriate handling

### Network Issues
- [ ] Disconnect network mid-operation
- [ ] Try various API operations
- [ ] Verify error notifications appear
- [ ] Verify application doesn't crash
- [ ] Reconnect and verify recovery

### Large Data Sets
- [ ] Test with 100+ entries
- [ ] Verify smooth scrolling
- [ ] Verify navigation performance
- [ ] Test grouping with many feeds
- [ ] Verify collapse/expand performance

### Long Content
- [ ] Open entry with very long content
- [ ] Verify scrolling works smoothly
- [ ] Verify no rendering issues
- [ ] Test with entries containing:
  - [ ] Long URLs
  - [ ] Special characters
  - [ ] Unicode characters
  - [ ] Code blocks
  - [ ] Images (markdown links)
  - [ ] Tables

### Concurrent Operations
- [ ] Refresh feeds while browsing entries
- [ ] Toggle star while viewing entry
- [ ] Navigate between entries quickly
- [ ] Verify no race conditions
- [ ] Verify state consistency

---

## 16. Visual and UI Consistency

### Color Themes
- [ ] Verify unread entries show in configured unread_color
- [ ] Verify read entries show in configured read_color
- [ ] Verify starred entries show star icon (★ or ☆)
- [ ] Verify status icons (● for unread, ○ for read)
- [ ] Verify feed headers bold and visible
- [ ] Verify category headers in cyan with [CATEGORY] prefix

### Layout and Formatting
- [ ] Verify header displays properly
- [ ] Verify footer shows relevant key bindings
- [ ] Verify text wrapping works correctly
- [ ] Verify no text overflow
- [ ] Verify separator lines display correctly

### Responsiveness
- [ ] Resize terminal window
- [ ] Verify layout adapts
- [ ] Verify no display corruption
- [ ] Test various terminal sizes (small, medium, large)

---

## 17. Performance Testing

### Loading Performance
- [ ] Measure startup time
- [ ] Measure time to load 100 entries
- [ ] Measure time to load 500+ entries
- [ ] Note any significant delays

### Sorting Performance
- [ ] Cycle through sort modes with large dataset
- [ ] Verify no lag or freezing
- [ ] Measure time for each sort operation

### Grouping Performance
- [ ] Toggle grouping with many feeds
- [ ] Collapse/expand all with many feeds
- [ ] Navigate in grouped mode
- [ ] Verify smooth performance

### API Response Times
- [ ] Mark entries as read/unread
- [ ] Toggle star status
- [ ] Refresh feeds
- [ ] Note response times for each operation

---

## 18. Data Integrity

### State Persistence
- [ ] Star an entry
- [ ] Restart application
- [ ] Verify entry still starred
- [ ] Mark entry as read
- [ ] Restart application
- [ ] Verify entry still read

### Multi-Instance Behavior
- [ ] Open miniflux-tui in two terminals
- [ ] Mark entry as read in one instance
- [ ] Refresh in other instance
- [ ] Verify state syncs via server

### Sync with Web Interface
- [ ] Mark entry as read in TUI
- [ ] Check Miniflux web interface
- [ ] Verify status updated
- [ ] Star entry in web interface
- [ ] Refresh TUI
- [ ] Verify status updated

---

## 19. Accessibility

### Keyboard-Only Operation
- [ ] Perform all operations without mouse
- [ ] Verify all functions accessible via keyboard
- [ ] Verify key bindings intuitive

### Terminal Compatibility
- [ ] Test in different terminal emulators:
  - [ ] GNOME Terminal
  - [ ] Konsole
  - [ ] iTerm2 (macOS)
  - [ ] Terminal.app (macOS)
  - [ ] Windows Terminal
  - [ ] PuTTY
- [ ] Verify rendering correct in each

---

## 20. Documentation Verification

### README Accuracy
- [ ] Follow installation instructions
- [ ] Verify all steps work as documented
- [ ] Verify screenshots/examples accurate

### Help Screen Accuracy
- [ ] Compare key bindings in help screen to actual behavior
- [ ] Verify all listed shortcuts work
- [ ] Verify no undocumented shortcuts missing

### Configuration Documentation
- [ ] Verify all config options documented
- [ ] Verify default values correct
- [ ] Verify examples work

---

## Test Results Summary

**Tester Name:** ______________________
**Date:** ______________________
**Version Tested:** ______________________
**Platform:** ______________________
**Python Version:** ______________________

**Overall Result:** [ ] Pass  [ ] Fail  [ ] Pass with Issues

**Critical Issues Found:**
1.
2.
3.

**Minor Issues Found:**
1.
2.
3.

**Improvement Suggestions:**
1.
2.
3.

**Additional Notes:**


---

## Checklist Summary

- **Total Test Items:** ~300+
- **Estimated Testing Time:** 2-4 hours for complete coverage
- **Priority:** High = Core functionality, Medium = Important features, Low = Edge cases

### Recommended Testing Order

1. Configuration and Setup (15 min)
2. Application Launch and Entry List Navigation (20 min)
3. Entry Reader Screen (20 min)
4. Status Management (mark read/star) (15 min)
5. Sorting and Grouping (30 min)
6. Help and Status Screens (15 min)
7. Filtering and Refresh (20 min)
8. Edge Cases and Error Handling (30 min)
9. Performance and Visual Consistency (20 min)
10. Documentation Verification (10 min)

---

**End of Checklist**
