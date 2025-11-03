# Test Coverage Improvement - Issue #391

This branch tracks work to improve test coverage from 71% to 80%+.

## Phase 1: Critical Areas (In Progress)

### Completed:
- None yet

### In Progress:
- [ ] entry_history.py tests (19% → 80%+)
- [ ] api/client.py get_read_entries() tests
- [ ] base_screen.py lifecycle tests

### Challenges Identified:
1. **Textual Screen Testing**: Screens have read-only  property - requires full app initialization or different mocking strategy
2. **Entry Model Complexity**: Entry requires full Feed object with all fields
3. **Async Worker Testing**: Screens use  which needs proper event loop handling

### Next Steps:
1. Study existing screen tests (e.g., test_entry_list.py) for patterns
2. Create proper fixtures for Entry/Feed models
3. Use Textual's test utilities for screen testing
4. Add API client tests first (easier to test)

## Coverage Target:
- Current: 71% (2488 statements, 721 missing)
- Goal: 80%+ overall
- Priority files: entry_history.py (19%), settings (26%), category mgmt (44%), feed mgmt (43%)

See coverage_analysis.md for full details.
