# Testing Enhancement Recommendations

## Summary

Your proposed testing approach is **excellent**, but **90% is already implemented**. The miniflux-tui-py project has a mature test suite (913 tests) with comprehensive integration testing using Textual's official harness.

## What's Already Working ✅

1. **Textual Test Harness** - All integration tests use `async with app.run_test()`
2. **Mock Infrastructure** - Excellent fixtures in `conftest.py` with `async_client_factory`
3. **Integration Tests** - `test_entry_list_integration.py` and `test_entry_reader_integration.py`
4. **CI/CD Pipeline** - Multi-platform testing (Ubuntu/macOS/Windows), Python 3.11-3.14
5. **Coverage Tracking** - 60%+ required, with Coveralls integration
6. **Mutation Testing** - Runs on PRs for test quality assurance
7. **Widget IDs** - Partially implemented (status, settings, dialogs have IDs)

## What to Add ⭐

### 1. Snapshot Testing (High Priority)

**Why:** Catch visual regressions automatically

**Action:**
```bash
# 1. Add dependency
uv add --dev pytest-textual-snapshot

# 2. Create tests/test_snapshots.py
# (See example below)

# 3. Generate baseline
uv run pytest tests/test_snapshots.py --snapshot-update

# 4. Commit snapshots
git add tests/__snapshots__/
git commit -m "test: add snapshot tests for visual regression detection"
```

**Example Test:**
```python
# tests/test_snapshots.py
import pytest
from miniflux_tui.ui.app import MinifluxTuiApp

@pytest.fixture
def snapshot_config():
    from miniflux_tui.config import Config
    config = Config(
        server_url="http://localhost:8080",
        password=["echo", "test-token"],
        allow_invalid_certs=False,
        unread_color="cyan",
        read_color="gray",
        default_sort="date",
        default_group_by_feed=False,
    )
    config._api_key_cache = "test-token-123"
    return config

def test_entry_list_empty(snapshot_config, snap_compare):
    """Snapshot: Entry list with no entries."""
    app = MinifluxTuiApp(snapshot_config)
    assert snap_compare(app, terminal_size=(100, 40))

def test_entry_list_with_entries(snapshot_config, sample_entries, snap_compare):
    """Snapshot: Entry list with sample entries."""
    app = MinifluxTuiApp(snapshot_config)
    app.entries = sample_entries
    assert snap_compare(app, terminal_size=(100, 40))

def test_entry_reader(snapshot_config, sample_entry, snap_compare):
    """Snapshot: Entry reader screen."""
    from miniflux_tui.ui.screens.entry_reader import EntryReaderScreen
    screen = EntryReaderScreen(
        entry=sample_entry,
        unread_color="cyan",
        read_color="gray",
    )
    assert snap_compare(screen, terminal_size=(100, 40))
```

### 2. Complete Widget IDs (Medium Priority)

**Current State:** Partial implementation
- ✅ Status screen, settings, dialogs - Have IDs
- ❌ Entry reader main content - Missing IDs
- ❌ Entry list items - Missing IDs

**Action:**
```python
# miniflux_tui/ui/screens/entry_reader.py
def compose(self) -> ComposeResult:
    yield Header()
    with VerticalScroll():
        # Add IDs here:
        yield Static(title, classes="entry-title", id="entry-title")
        yield Static(meta, classes="entry-meta", id="entry-meta")
        yield Static(url, classes="entry-url", id="entry-url")
        yield Static(CONTENT_SEPARATOR, classes="separator")
        yield Markdown(content, classes="entry-content", id="entry-content")
    yield Footer()
```

### 3. Pilot-Based Navigation Tests (Low Priority)

**Current State:** Tests call `action_*()` directly
**Enhancement:** Add realistic key press simulation

```python
async def test_full_navigation_flow(snapshot_config, sample_entries):
    """Test complete user workflow with keyboard."""
    app = MinifluxTuiApp(snapshot_config)
    app.entries = sample_entries

    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause()

        # Navigate with j/k
        await pilot.press("j", "j", "j")

        # Select entry
        await pilot.press("enter")
        await pilot.pause()

        # Verify navigation
        assert "entry_reader" in str(app.screen)

        # Go back
        await pilot.press("escape")
        assert "entry_list" in str(app.screen)
```

## What NOT to Do ❌

1. **Don't create `tests/e2e/` directory** - Integration tests already serve this purpose
2. **Don't add `pytest` or `pytest-asyncio`** - Already installed
3. **Don't worry about mock client injection** - Already well-implemented
4. **Don't change CI/CD workflow** - Already comprehensive

## Implementation Plan

### Quick Win (2-4 hours)
```bash
# 1. Install snapshot testing
uv add --dev pytest-textual-snapshot

# 2. Create minimal snapshot test file
cat > tests/test_snapshots.py << 'EOF'
"""Snapshot tests for visual regression detection."""
import pytest
from miniflux_tui.ui.app import MinifluxTuiApp
from miniflux_tui.config import Config

@pytest.fixture
def snapshot_config():
    config = Config(
        server_url="http://localhost:8080",
        password=["echo", "test"],
        allow_invalid_certs=False,
        unread_color="cyan",
        read_color="gray",
        default_sort="date",
        default_group_by_feed=False,
    )
    config._api_key_cache = "test-token"
    return config

def test_app_startup(snapshot_config, snap_compare):
    """Snapshot test for app startup screen."""
    app = MinifluxTuiApp(snapshot_config)
    assert snap_compare(app, terminal_size=(100, 40))
EOF

# 3. Generate baseline
uv run pytest tests/test_snapshots.py --snapshot-update

# 4. Verify it works
uv run pytest tests/test_snapshots.py

# 5. Commit
git add tests/test_snapshots.py tests/__snapshots__/
git commit -m "test: add snapshot testing for visual regression detection"
```

### Full Implementation (1-2 days)
1. Add snapshot tests for all screens (6-8 snapshots)
2. Add widget IDs to entry reader and entry list
3. Add pilot-based navigation tests (3-5 scenarios)
4. Update CI to upload snapshot diffs on failure
5. Document in CONTRIBUTING.md

## Questions Answered

### Q: Should we use pytest-textual-snapshot?
**A: YES** - This is the only missing piece from your proposal

### Q: Should we create tests/e2e/?
**A: NO** - Integration tests already cover end-to-end scenarios

### Q: Are widgets testable with IDs?
**A: PARTIALLY** - Some screens have IDs, but entry reader needs them

### Q: Is dependency injection working?
**A: YES** - Excellent mock client factory in conftest.py

### Q: Should we use pilot.press() or action_*() calls?
**A: BOTH** - Direct action calls for unit tests, pilot.press() for e2e/snapshot tests

## Expected Outcomes

After implementing snapshot testing:

1. **Automated visual regression detection** - Layout changes will be caught automatically
2. **Faster PR reviews** - Snapshot diffs show exact UI changes
3. **Better documentation** - Snapshots serve as visual documentation
4. **Reduced manual testing** - No need to manually verify UI after changes

## Resources

- [pytest-textual-snapshot docs](https://github.com/Textualize/pytest-textual-snapshot)
- [Textual testing guide](https://textual.textualize.io/guide/testing/)
- [Current integration tests](tests/test_entry_list_integration.py)

## Contact

For questions or implementation help, open an issue on GitHub or ping the maintainer.

---

**Generated:** 2025-11-06
**Status:** Ready for implementation
**Effort:** 2-4 hours for snapshot testing alone
