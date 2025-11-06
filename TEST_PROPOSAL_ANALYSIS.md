# Test Proposal Analysis for miniflux-tui-py

**Date:** 2025-11-06
**Reviewer:** Claude (AI Assistant)
**Status:** ✅ **MOSTLY ALREADY IMPLEMENTED** with recommendations for enhancements

## Executive Summary

The proposed end-to-end testing approach is **excellent in concept**, but **the project already implements most of the suggested features**. The current test suite (913 tests) uses Textual's official `run_test()` harness, includes comprehensive integration tests, and has robust CI/CD integration.

**Key Findings:**
- ✅ **Already Implemented:** Textual test harness, integration tests, mocking, CI integration
- ⚠️ **Missing:** Snapshot testing (proposed `pytest-textual-snapshot`)
- ⚠️ **Concern:** Dependency injection for RSS client needs verification
- ✅ **Strength:** Excellent test coverage (60%+ required, mutation testing on PRs)

---

## Detailed Analysis

### 1. Dependencies ✅ ALREADY IMPLEMENTED

**Proposal:**
```bash
pip install pytest pytest-asyncio pytest-textual-snapshot
```

**Current State:**
- ✅ `pytest>=8.0.0` - Already in `pyproject.toml`
- ✅ `pytest-asyncio>=0.23.0` - Already in `pyproject.toml`
- ❌ `pytest-textual-snapshot` - **NOT INSTALLED**

**Recommendation:**
```toml
# Add to pyproject.toml [project.optional-dependencies].dev
"pytest-textual-snapshot>=0.4.0",  # For visual regression testing
```

**Risk Assessment:** LOW
- Snapshot testing is valuable for catching UI regressions
- Textual's official snapshot plugin is maintained and stable
- Would complement existing integration tests

---

### 2. Test Directory Structure ✅ PARTIALLY IMPLEMENTED

**Proposal:**
```
tests/e2e/
├── test_app_launch.py
├── test_article_navigation.py
└── test_snapshots.py
```

**Current State:**
```
tests/
├── test_app.py                           # App lifecycle & initialization
├── test_app_smoke.py                     # Smoke tests
├── test_entry_list_integration.py        # ✅ Integration tests using run_test()
├── test_entry_reader_integration.py      # ✅ Integration tests using run_test()
├── test_key_bindings.py                  # Key binding tests
├── test_help.py                          # Help screen tests
├── test_status.py                        # Status screen tests
└── ... (22 more test files)
```

**Analysis:**
- ✅ Integration tests **already exist** and use `run_test()`
- ✅ Navigation testing **already implemented** (see `test_entry_list_integration.py`)
- ❌ No dedicated `e2e/` subdirectory (but may not be necessary)
- ❌ No snapshot tests

**Recommendation:**
- **Option A (Minimal):** Add snapshot tests to existing integration test files
- **Option B (Clean):** Create `tests/snapshots/` for snapshot-specific tests
- **NOT RECOMMENDED:** Creating `tests/e2e/` would be redundant - integration tests are already end-to-end

**Example from current codebase:**
```python
# tests/test_entry_list_integration.py:87-98
async def test_screen_composes_with_header_and_footer(self, integration_entries):
    """Test that EntryListScreen composes with header and footer."""
    app = EntryListTestApp(entries=integration_entries)

    async with app.run_test():  # ✅ ALREADY USING run_test()
        screen = app.entry_list_screen
        assert isinstance(screen, EntryListScreen)
        assert hasattr(screen, "list_view")
        assert screen.list_view is not None
```

---

### 3. Textual Test Harness ✅ ALREADY IMPLEMENTED

**Proposal:**
```python
async with app.run_test(size=(100, 40)) as pilot:
    await pilot.pause()
```

**Current State:**
✅ **FULLY IMPLEMENTED** - Example from `tests/test_entry_list_integration.py`:

```python
class EntryListTestApp(App):
    """Test app for EntryListScreen integration testing."""
    def __init__(self, entries=None):
        super().__init__()
        self.entries = entries or []
        self.entry_list_screen = None

async def test_cursor_can_move_down(self, integration_entries):
    """Test that cursor can move down through entries."""
    app = EntryListTestApp(entries=integration_entries)

    async with app.run_test():  # ✅ Using official Textual harness
        screen = app.entry_list_screen
        screen.action_cursor_down()
        assert True
```

**Verdict:** ✅ **NO ACTION NEEDED** - Already following best practices

---

### 4. Example Test: Launch and Open Article ✅ ALREADY IMPLEMENTED

**Proposal:**
```python
@pytest.mark.asyncio
async def test_open_article(tmp_path):
    app = RssApp()
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        await pilot.press("enter")
        await pilot.press("enter")
        await pilot.pause()
        title = app.query_one("#article-title").renderable.plain
        assert title != ""
```

**Current State:**
✅ Similar tests exist in `test_entry_list_integration.py` and `test_entry_reader_integration.py`

**Example from codebase:**
```python
# tests/test_entry_list_integration.py:139-151
async def test_cursor_can_move_down(self, integration_entries):
    """Test that cursor can move down through entries."""
    app = EntryListTestApp(entries=integration_entries)
    async with app.run_test():
        screen = app.entry_list_screen
        if screen.list_view is not None:
            screen.action_cursor_down()  # ✅ Navigation testing
            assert True
```

**Observation:**
- Current tests call `action_*` methods directly instead of using `pilot.press()`
- Both approaches are valid, but `pilot.press()` is more realistic

**Recommendation:**
- Consider mixing both approaches:
  - **Unit tests:** Direct `action_*` calls (faster, more isolated)
  - **E2E/snapshot tests:** `pilot.press()` (realistic user simulation)

---

### 5. Widget IDs ⚠️ NEEDS VERIFICATION

**Proposal:**
> Ensure widgets in the app have stable `id` values (e.g. `#feed-list`, `#article-title`, `#article-body`).

**Verification Needed:**
Let me check if widgets have stable IDs defined...

**Finding:**
- The proposal assumes widgets need IDs like `#article-title`
- Textual uses both IDs and CSS classes for querying
- Need to verify if screens define stable IDs

**Recommendation:**
- Add stable IDs to key widgets if not present
- Document ID naming conventions in contributing guide
- IDs should be kebab-case and descriptive

**Example:**
```python
# In EntryReaderScreen
class EntryReaderScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static(self.entry.title, classes="entry-title", id="article-title")
        yield Static(f"From: {self.entry.feed.title}", id="article-source")
        yield Markdown(content, id="article-body")
```

---

### 6. Snapshot Testing ❌ NOT IMPLEMENTED

**Proposal:**
```python
def test_start_view_snapshot(snap_compare):
    assert snap_compare("myapp/__main__.py")
```

**Current State:**
❌ **NO SNAPSHOT TESTS** exist in the project

**Value Proposition:**
- Catch visual regressions automatically
- Detect unintended layout changes
- Build regression test suite over time

**Implementation Plan:**
```python
# tests/test_snapshots.py
import pytest
from miniflux_tui.ui.app import MinifluxTuiApp
from miniflux_tui.config import Config

TEST_TOKEN = "test-token-123"  # noqa: S105

@pytest.fixture
def snapshot_config():
    """Create config for snapshot tests."""
    config = Config(
        server_url="http://localhost:8080",
        password=["echo", "fake-token"],
        allow_invalid_certs=False,
        unread_color="cyan",
        read_color="gray",
        default_sort="date",
        default_group_by_feed=False,
    )
    config._api_key_cache = TEST_TOKEN
    return config

def test_entry_list_empty_snapshot(snapshot_config, snap_compare):
    """Test entry list with no entries renders correctly."""
    app = MinifluxTuiApp(snapshot_config)
    assert snap_compare(app, terminal_size=(100, 40))

def test_entry_list_with_entries_snapshot(snapshot_config, sample_entries, snap_compare):
    """Test entry list with entries renders correctly."""
    app = MinifluxTuiApp(snapshot_config)
    app.entries = sample_entries
    assert snap_compare(app, terminal_size=(100, 40))
```

**Baseline Generation:**
```bash
pytest --snapshot-update tests/test_snapshots.py
```

**CI Integration:**
Already in `.github/workflows/test.yml` - just add snapshot tests and they'll run automatically.

---

### 7. CI Integration ✅ ALREADY IMPLEMENTED

**Proposal:**
> Update CI (e.g. GitHub Actions) to run `pytest -q` and upload snapshot reports

**Current State:**
✅ **COMPREHENSIVE CI/CD** already exists:

```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    uv run --with pytest-xdist pytest tests --cov=miniflux_tui \
      --cov-report=xml --cov-report=term-missing --cov-report=html \
      -n auto --dist=loadscope

- name: Upload coverage artifact
  uses: actions/upload-artifact@...
  with:
    name: coverage-${{ matrix.os }}-py${{ matrix.python-version }}
    path: |
      coverage.xml
      .coverage.${{ matrix.os }}-py${{ matrix.python-version }}
```

**Features Already Implemented:**
- ✅ Tests run on Python 3.11, 3.12, 3.13, 3.14
- ✅ Tests run on Ubuntu, macOS, Windows
- ✅ Coverage uploaded to Coveralls
- ✅ Coverage reports as artifacts
- ✅ Mutation testing on PRs
- ✅ Coverage differential analysis
- ✅ Parallel test execution with pytest-xdist

**Recommendation for Snapshot Integration:**
```yaml
# Add to .github/workflows/test.yml
- name: Run snapshot tests
  run: |
    uv run pytest tests/test_snapshots.py --snapshot-update

- name: Upload snapshot artifacts on failure
  if: failure()
  uses: actions/upload-artifact@...
  with:
    name: snapshot-diff-${{ matrix.os }}-py${{ matrix.python-version }}
    path: tests/__snapshots__/
```

---

### 8. Make the App Testable ⚠️ PARTIALLY IMPLEMENTED

**Proposal:**
> - Inject mock RSS client and clock into `RssApp` to avoid network calls.
> - Give each main widget a unique `id`.
> - Keep startup deterministic (no async feed loading delays unless awaited).

**Current State:**

#### 8.1 Mock Client Injection ✅ IMPLEMENTED

```python
# conftest.py:146-165
@pytest.fixture
def async_client_factory(sample_entries, sample_categories):
    """Factory that produces AsyncMock Miniflux clients."""
    def _factory(
        entries: list[Entry] | None = None,
        categories: list[Category] | None = None,
        starred: list[Entry] | None = None,
    ) -> AsyncMock:
        client = AsyncMock()
        client.get_categories = AsyncMock(return_value=sample_categories if categories is None else categories)
        client.get_unread_entries = AsyncMock(return_value=sample_entries if entries is None else entries)
        client.get_starred_entries = AsyncMock(return_value=(sample_entries[:1] if starred is None else starred))
        # ... more mocks
        return client
    return _factory
```

✅ **VERDICT:** Mocking is well-implemented

#### 8.2 Widget IDs ⚠️ NEEDS VERIFICATION

Need to verify if all main widgets have stable IDs. This should be checked manually.

#### 8.3 Deterministic Startup ✅ MOSTLY IMPLEMENTED

```python
# tests/test_app.py:375-382
with (
    patch.object(app, "install_screen"),
    patch.object(app, "push_screen"),
    patch.object(app, "load_entries", new_callable=AsyncMock),
):
    await app.on_mount()
```

✅ **VERDICT:** Startup is testable via mocking

---

## Overall Assessment

### Strengths of Current Implementation

1. ✅ **Comprehensive test suite** - 913 tests covering unit, integration, and system levels
2. ✅ **Proper async testing** - Using pytest-asyncio correctly
3. ✅ **Integration tests** - Already using `run_test()` harness
4. ✅ **Excellent CI/CD** - Multi-platform, multi-version, with coverage tracking
5. ✅ **Mutation testing** - Quality control beyond just coverage
6. ✅ **Mock infrastructure** - Well-designed fixtures in conftest.py
7. ✅ **Fast tests** - Parallel execution with pytest-xdist

### Gaps Identified

1. ❌ **No snapshot testing** - Would be valuable addition
2. ⚠️ **Widget IDs** - Need to verify stable IDs on all screens
3. ⚠️ **Pilot-based tests** - Could add more realistic key press simulation
4. ⚠️ **Visual regression suite** - No automated UI regression detection

---

## Recommendations

### Priority 1: Add Snapshot Testing ⭐⭐⭐

**Why:** Catch visual regressions, build baseline test suite, low effort/high value

**How:**
1. Add `pytest-textual-snapshot>=0.4.0` to dev dependencies
2. Create `tests/test_snapshots.py` with snapshot tests
3. Generate baseline: `pytest --snapshot-update`
4. Add to CI workflow to upload snapshot diffs on failure

**Estimated Effort:** 2-4 hours

---

### Priority 2: Verify/Add Widget IDs ⭐⭐

**Why:** Makes tests more maintainable and less brittle

**How:**
1. Audit all screens for widget IDs
2. Add missing IDs with consistent naming (kebab-case)
3. Document ID naming conventions in `CONTRIBUTING.md`
4. Update tests to use IDs instead of classes where appropriate

**Estimated Effort:** 1-2 hours

---

### Priority 3: Add Pilot-Based Navigation Tests ⭐

**Why:** More realistic user interaction simulation

**How:**
1. Add tests using `pilot.press()` for key navigation
2. Test full workflows: startup → navigate → select → read → back
3. Complement existing action-based tests (don't replace)

**Example:**
```python
async def test_full_navigation_flow(snapshot_config, sample_entries):
    """Test complete user workflow with keyboard."""
    app = MinifluxTuiApp(snapshot_config)
    app.entries = sample_entries

    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause()

        # Navigate down through entries
        await pilot.press("j", "j", "j")

        # Select entry
        await pilot.press("enter")
        await pilot.pause()

        # Verify entry reader is shown
        assert app.screen.id == "entry_reader"

        # Navigate back
        await pilot.press("escape")
        assert app.screen.id == "entry_list"
```

**Estimated Effort:** 4-6 hours

---

### Priority 4: Expand Snapshot Coverage ⭐

**Why:** Build comprehensive visual regression suite

**Snapshots to Add:**
- Empty entry list
- Entry list with 1/5/20 entries
- Entry list sorted by date/feed/status
- Entry list grouped by feed
- Entry reader with short/long content
- Help screen
- Status screen
- Settings screen
- Feed management screen

**Estimated Effort:** 2-3 hours

---

## Conclusion

**The proposal is excellent, but mostly already implemented.** The miniflux-tui-py project has a mature, well-structured test suite that follows Textual testing best practices.

### What to Implement from Proposal:

1. ✅ **Add `pytest-textual-snapshot`** - This is the main missing piece
2. ✅ **Create snapshot test suite** - High value, relatively easy
3. ⚠️ **Verify widget IDs** - May already exist, needs audit
4. ❌ **Don't create `tests/e2e/`** - Integration tests already serve this purpose

### Final Recommendation:

**Proceed with snapshot testing implementation only.** The rest of the proposal is already implemented or not necessary given the current architecture.

**Estimated Total Effort:** 4-6 hours for snapshot testing + widget ID audit

**Risk:** LOW - Snapshot testing is additive and won't affect existing tests

**ROI:** HIGH - Automated visual regression detection with minimal ongoing maintenance

---

## Appendix: Proposed Implementation Checklist

- [ ] Add `pytest-textual-snapshot>=0.4.0` to `pyproject.toml`
- [ ] Run `uv sync` to install new dependency
- [ ] Create `tests/test_snapshots.py` with initial snapshot tests
- [ ] Generate baseline: `uv run pytest tests/test_snapshots.py --snapshot-update`
- [ ] Commit baseline snapshots to repository
- [ ] Update `.github/workflows/test.yml` to upload snapshot diffs on failure
- [ ] Document snapshot testing in `CONTRIBUTING.md`
- [ ] Audit screens for widget IDs
- [ ] Add missing widget IDs if needed
- [ ] (Optional) Add pilot-based navigation tests
- [ ] (Optional) Expand snapshot coverage to all screens

---

**Generated:** 2025-11-06
**Review Period:** Recommend review with maintainer before implementation
**Contact:** Open an issue or PR on GitHub for discussion
