# Test Coverage Analysis

## Overall Coverage: 71% (2488 statements, 721 missing)

## Areas Needing Tests (Prioritized by Impact)

### 🔴 Critical - 0% Coverage (Protocol/Interface Files)
1. **miniflux_tui/ui/app_protocol.py** - 0% (25/25 lines missing)
  - Protocol definitions not tested
  - These are interfaces, may not need direct tests

2. **miniflux_tui/ui/base_screen.py** - 0% (8/8 lines missing)
  - Base screen class not tested
  - Should test screen lifecycle methods

### 🟠 High Priority - Low Coverage (<50%)
3. **miniflux_tui/ui/screens/entry_history.py** - 19% (21/26 lines missing)
  - Our new history screen!
  - Should add integration tests for on_mount() behavior
  - Test API call and error handling

4. **miniflux_tui/ui/screens/settings_management.py** - 26% (80/108 lines missing)
  - Settings UI not tested
  - Should test settings load/save/validation

5. **miniflux_tui/ui/screens/category_management.py** - 44% (71/127 lines missing)
  - Category CRUD operations not well tested
  - Should test create/edit/delete flows

6. **miniflux_tui/ui/screens/feed_management.py** - 43% (69/122 lines missing)
  - Feed management UI not well tested
  - Should test feed CRUD operations

### 🟡 Medium Priority - Moderate Coverage (50-75%)
7. **miniflux_tui/ui/screens/confirm_dialog.py** - 60% (19/48 lines missing)
  - Dialog interactions not fully tested
  - Should test confirm/cancel flows

8. **miniflux_tui/ui/screens/input_dialog.py** - 57% (22/51 lines missing)
  - Input validation not fully tested
  - Should test input validation and submission

9. **miniflux_tui/ui/screens/entry_reader.py** - 64% (76/210 lines missing)
  - Entry reading/display not fully tested
  - Should test keyboard shortcuts, scrolling, actions

10. **miniflux_tui/ui/protocols.py** - 64% (8/22 lines missing)
  - Protocol definitions partially tested

11. **miniflux_tui/api/client.py** - 72% (31/110 lines missing)
  - Missing tests for:
    - get_read_entries() (our history feature!)
    - get_categories()
    - create_category()
    - update_category()
    - delete_category()
    - get_category_entries()
    - Error handling paths

12. **miniflux_tui/ui/screens/entry_list.py** - 73% (198/726 lines missing)
  - Large file with many untested paths
  - Missing tests for:
    - Search functionality
    - Filter toggling
    - Scroll position restoration
    - Error states
    - Edge cases in grouping/sorting

### 🟢 Low Priority - Good Coverage (>75%)
13. **miniflux_tui/ui/screens/help.py** - 80% (22/111 lines missing)
14. **miniflux_tui/ui/app.py** - 80% (37/181 lines missing)
15. **miniflux_tui/main.py** - 91% (8/89 lines missing)
16. **miniflux_tui/ui/screens/status.py** - 92% (10/130 lines missing)
17. **miniflux_tui/security.py** - 92% (3/36 lines missing)
18. **miniflux_tui/utils.py** - 94% (4/68 lines missing)
19. **miniflux_tui/config.py** - 95% (8/157 lines missing)
20. **miniflux_tui/api/models.py** - 98% (1/47 lines missing)

### ✅ Excellent Coverage (100%)
- miniflux_tui/constants.py
- miniflux_tui/performance.py
- All __init__.py files

## Recommendations

### Phase 1: Critical Gaps (Immediate)
- [ ] Add integration tests for `entry_history.py` (our new feature!)
- [ ] Test `get_read_entries()` in `api/client.py`
- [ ] Add basic tests for `base_screen.py` lifecycle

### Phase 2: UI Screens (Short-term)
- [ ] Test settings management (load/save/validation)
- [ ] Test category management (CRUD operations)
- [ ] Test feed management (CRUD operations)
- [ ] Test dialogs (confirm/input flows)

### Phase 3: Entry Management (Medium-term)
- [ ] Test entry reader keyboard shortcuts and actions
- [ ] Test entry list search functionality
- [ ] Test entry list filter toggling
- [ ] Test scroll position restoration

### Phase 4: Edge Cases (Long-term)
- [ ] Test error handling paths in all UI screens
- [ ] Test network error recovery
- [ ] Test concurrent operations
- [ ] Test edge cases in sorting/grouping

## Quick Wins (Easy to Add)
1. Test `get_read_entries()` - Just added this for history!
2. Test `EntryHistoryScreen.on_mount()` - Integration test
3. Test settings validation - Unit tests for config
4. Test dialog confirm/cancel - Simple UI tests
