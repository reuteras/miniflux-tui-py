# Full Application Integration Tests

## Overview

Comprehensive end-to-end integration tests added in `tests/test_app_full_integration.py` that verify complete user workflows with realistic data scenarios.

## Test Data Structure

### Realistic Fixtures

**4 Categories:**
- Tech (3 feeds)
- News (3 feeds)
- Entertainment (2 feeds)
- Science (2 feeds)

**10 Feeds across categories:**
1. TechCrunch (10 entries: 5 unread, 3 starred)
2. The Verge (8 entries: 4 unread, 2 starred)
3. Ars Technica (5 entries: 2 unread, 1 starred)
4. Reuters (7 entries: 6 unread, 0 starred)
5. BBC News (3 entries: 1 unread, 1 starred)
6. The Guardian (6 entries: 3 unread, 2 starred)
7. Variety (4 entries: 2 unread, 1 starred)
8. Hollywood Reporter (2 entries: 1 unread, 0 starred)
9. Science Daily (9 entries: 7 unread, 3 starred)
10. Nature (1 entry: 1 unread, 1 starred)

**Total Entries: 55**
- **32 unread entries**
- **14 starred entries**
- **Entry distribution: 1-10 entries per feed**

### Test Coverage

#### 1. Full App Startup Tests (TestFullAppStartup)
✅ **test_app_starts_with_cursor_on_first_entry**
- Verifies app loads entries correctly
- Checks first entry is "TechCrunch Article 1"
- Validates cursor position

✅ **test_app_loads_correct_number_of_unread_entries**
- Verifies exactly 32 unread entries load
- Validates entry count matches fixture data

#### 2. Group Mode Tests (TestGroupModeWithRealisticData)
✅ **test_group_mode_organizes_by_feed**
- Tests grouping entries by feed name
- Verifies entries remain accessible when grouped
- Validates group mode flag is set

✅ **test_toggle_group_mode**
- Tests toggling group mode on/off
- Verifies state changes correctly
- Tests returning to original state

✅ **test_grouped_entries_maintain_feed_order**
- Tests grouped + sorted by feed
- Verifies sorted_entries list is populated
- Validates feed ordering logic

#### 3. Sorting Mode Tests (TestSortingModesWithRealisticData)
✅ **test_date_sort_mode**
- Tests date sorting (newest first)
- Verifies entries sorted by published_at
- Validates first entry is newest

✅ **test_feed_sort_mode**
- Tests alphabetical sorting by feed name
- Verifies feed name ordering

✅ **test_status_sort_mode**
- Tests status sorting (unread first)
- Validates sorting by entry status

✅ **test_cycle_through_sort_modes**
- Tests cycling: date → feed → status → date
- Verifies each sort mode transition
- Validates cycle completion

#### 4. Navigation Tests (TestNavigationWithRealisticData)
✅ **test_cursor_navigation_through_entries**
- Tests j/k navigation (cursor up/down)
- Verifies navigation actions execute without errors

✅ **test_navigation_in_grouped_mode**
- Tests navigation when feeds are grouped
- Verifies cursor movement through grouped entries

#### 5. Filtering Tests (TestFilteringWithRealisticData)
✅ **test_filter_unread_only**
- Tests filtering to show only unread entries
- Verifies all filtered entries are unread

✅ **test_filter_starred_only**
- Tests filtering to show only starred entries
- Verifies exactly 14 starred entries
- Validates all filtered entries are starred

#### 6. Complex Scenario Tests (TestComplexScenarios)
✅ **test_grouped_and_sorted_together**
- Tests group mode + feed sort combined
- Verifies both features work together
- Validates sorted_entries populated

✅ **test_entry_counts_per_feed**
- Validates entry distribution per feed
- Checks expected unread counts:
  - TechCrunch: 5, The Verge: 4, Ars Technica: 2
  - Reuters: 6, BBC News: 1, The Guardian: 3
  - Variety: 2, Hollywood Reporter: 1
  - Science Daily: 7, Nature: 1

✅ **test_switching_between_unread_and_starred_views**
- Tests view switching: unread → starred → unread
- Verifies counts: 32 unread, 14 starred
- Validates state maintained between switches

## Test Results

```bash
$ uv run pytest tests/test_app_full_integration.py -v

============================== 16 passed in 5.49s ==============================
```

**All 16 tests passing ✅**

## Key Features Tested

### ✅ Data Loading
- Unread entries loaded correctly (32)
- Starred entries loaded correctly (14)
- Entry distribution across feeds verified

### ✅ User Interface
- Cursor positioning
- Entry list display
- Screen navigation

### ✅ Sorting & Grouping
- Date sort (newest first)
- Feed sort (alphabetical)
- Status sort (unread first)
- Group by feed
- Combined grouping + sorting

### ✅ Filtering
- Unread-only filter
- Starred-only filter
- View switching

### ✅ Navigation
- Cursor movement (j/k keys)
- Navigation in grouped mode
- Navigation through sorted entries

## Test Methodology

### Mocking Strategy

Tests use proper mocking to isolate app behavior:

```python
# Mock client with realistic data
app.client = full_integration_client  # Fixture with 55 entries
app.notify = MagicMock()
app.is_screen_installed = MagicMock(return_value=False)

# Load entries
await app.load_entries("unread")

# Verify behavior
assert len(app.entries) == 32
```

### Fixture Design

**Fixtures are reusable and composable:**
- `realistic_categories` → 4 categories
- `realistic_feeds` → 10 feeds (references categories)
- `realistic_entries` → 55 entries (references feeds)
- `full_integration_client` → Mocked client (returns realistic data)
- `full_integration_config` → Test configuration

### Benefits Over Isolated Tests

**Previous tests (test_entry_list_integration.py):**
- ✅ Test individual screens in isolation
- ✅ Test specific widget behavior
- ❌ Don't test full data flow through app
- ❌ Use minimal test data (1-3 entries)

**New tests (test_app_full_integration.py):**
- ✅ Test complete user workflows
- ✅ Use realistic data volumes (55 entries)
- ✅ Test interactions between features
- ✅ Verify data flow from API → app → screen
- ✅ Test edge cases (1 entry feed, 10 entry feed)

## Running the Tests

### Run full integration tests only:
```bash
uv run pytest tests/test_app_full_integration.py -v
```

### Run with coverage:
```bash
uv run pytest tests/test_app_full_integration.py --cov=miniflux_tui --cov-report=term-missing
```

### Run all app tests:
```bash
uv run pytest tests/test_app_full_integration.py tests/test_app.py -v
```

### Run entire test suite:
```bash
uv run pytest tests/
```

## Integration with CI/CD

Tests automatically run in CI pipeline (`.github/workflows/test.yml`):
- ✅ Tested on Python 3.11, 3.12, 3.13, 3.14
- ✅ Tested on Ubuntu, macOS, Windows
- ✅ Coverage tracked and reported
- ✅ Mutation testing on PRs

## Maintenance

### Adding New Tests

To add new integration tests:

1. **Use existing fixtures:**
```python
def test_new_feature(full_integration_config, full_integration_client):
    app = MinifluxTuiApp(full_integration_config)
    app.client = full_integration_client
    app.notify = MagicMock()
    app.is_screen_installed = MagicMock(return_value=False)

    await app.load_entries("unread")
    # Test your feature...
```

2. **Or create custom fixtures:**
```python
@pytest.fixture
def custom_entries(realistic_feeds):
    return [
        Entry(id=1, feed_id=1, title="Custom Entry", ...),
    ]
```

### Modifying Test Data

To change test data distribution:

1. Edit `realistic_entries` fixture in `test_app_full_integration.py`
2. Update docstring with new counts
3. Update assertions in tests that check counts

## Future Enhancements

### Potential Additions

1. **Pilot-based navigation tests**
  ```python
  async with app.run_test() as pilot:
      await pilot.press("j", "j", "j")  # Navigate down
      await pilot.press("enter")        # Select entry
      # Verify screen transition
  ```

2. **Snapshot tests** (with pytest-textual-snapshot)
  ```python
  def test_entry_list_snapshot(full_integration_client, snap_compare):
      app = MinifluxTuiApp(config)
      app.entries = realistic_entries
      assert snap_compare(app, terminal_size=(100, 40))
  ```

3. **Performance tests**
  ```python
  def test_large_dataset_performance(benchmark):
      # Create 1000 entries
      # Benchmark sorting, grouping, filtering
  ```

4. **Error scenario tests**
  ```python
  async def test_network_failure_recovery():
      # Simulate API timeout
      # Verify error handling and recovery
  ```

## Cursor Position Tests

In addition to full integration tests, comprehensive cursor position tests were added in `tests/test_cursor_position.py`:

### Test Coverage (11 tests total)

#### Standard Mode (2 tests)
- ✅ Cursor starts at position 0
- ✅ j/k navigation moves cursor correctly

#### Group by Feed Mode (3 tests)
- ✅ Cursor starts at position 0 when grouped
- ✅ Navigation through collapsed groups (documents j/k behavior)
- ✅ Expand/collapse (l/h) maintains cursor position

#### Group by Category Mode (3 tests)
- ✅ Cursor starts at position 0 when grouped by category
- ✅ Navigation through collapsed categories (documents j/k behavior)
- ✅ Expand/collapse maintains cursor position

#### Edge Cases (3 tests)
- ✅ Cursor can navigate to last entry
- ✅ Returning from entry reader maintains position (standard mode)
- ✅ Returning from entry reader maintains position (grouped mode)

### Key Findings

**Navigation Behavior**: j/k keys move through ALL ListView items, including CSS-hidden (collapsed) entries. This is documented Textual ListView behavior - navigation doesn't skip hidden items.

**Cursor Restoration**: When toggling between modes, the app intelligently tries to restore the user's position to keep them at the same entry, even when the list structure changes.

**Test Results:**
```bash
$ uv run pytest tests/test_cursor_position.py -v

============================== 11 passed in 5.89s ==============================
```

## Related Documentation

- [Test Proposal Analysis](TEST_PROPOSAL_ANALYSIS.md) - Detailed testing strategy
- [Testing Recommendations](TESTING_RECOMMENDATIONS.md) - Quick implementation guide
- [Contributing Guide](CONTRIBUTING.md) - Development workflow

## Summary

The new full integration tests provide **comprehensive coverage of real user workflows** with realistic data scenarios:

- ✅ 16 full integration tests covering complete workflows
- ✅ 11 cursor position tests covering all navigation scenarios
- ✅ 55 entries across 10 feeds in 4 categories (realistic test data)
- ✅ Tests verify app startup, sorting, grouping, filtering, navigation
- ✅ All 27 tests passing
- ✅ Integrates with existing test suite
- ✅ Ready for CI/CD pipeline
- ✅ Fixed cursor initialization bug in `_populate_list()`

**Test coverage increased** while **maintaining fast execution** (10 seconds for 27 tests).

---

**Created:** 2025-11-06
**Updated:** 2025-11-07
**Author:** AI Assistant (Claude)
**Status:** ✅ Complete & Passing
