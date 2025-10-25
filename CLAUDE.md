# CLAUDE.md - miniflux-tui-py Project Guide

This document provides context about the miniflux-tui-py project for Claude Code.

## Project Overview

**miniflux-tui-py** is a Python Terminal User Interface (TUI) client for [Miniflux](https://miniflux.app) - a self-hosted RSS reader. It provides a keyboard-driven interface to browse, read, and manage RSS feeds directly from the terminal.

- **Language**: Python 3.11+
- **Framework**: Textual (TUI framework)
- **Status**: Alpha (v0.1.1)
- **License**: MIT
- **Author**: Peter Reuterås
- **PyPI**: Available at https://pypi.org/project/miniflux-tui-py/
- **Docs**: https://reuteras.github.io/miniflux-tui-py/

This is a Python reimplementation of [cliflux](https://github.com/spencerwi/cliflux) (original Rust implementation).

## Directory Structure

```bash
miniflux-tui-py/
├── miniflux_tui/                    # Main package
│   ├── __init__.py
│   ├── main.py                      # Entry point & CLI argument handling
│   ├── config.py                    # Configuration management
│   ├── constants.py                 # Application constants
│   ├── performance.py               # Performance optimization utilities
│   ├── utils.py                     # Helper utilities
│   ├── api/
│   │   ├── client.py                # Async Miniflux API wrapper
│   │   └── models.py                # Data models (Entry, Feed)
│   └── ui/
│       ├── app.py                   # Main Textual App
│       └── screens/
│           ├── entry_list.py        # Entry list with sorting/grouping
│           ├── entry_reader.py      # Entry detail view
│           └── help.py              # Help/keyboard shortcuts
├── tests/                           # Test suite
│   ├── conftest.py
│   ├── test_*.py                    # Test files
├── docs/                            # MkDocs documentation
│   ├── index.md
│   ├── installation.md
│   ├── configuration.md
│   ├── usage.md
│   ├── contributing.md
│   └── api/
│       ├── client.md
│       ├── models.md
│       └── screens.md
├── .github/
│   ├── workflows/
│   │   ├── test.yml                 # Run tests on push (Python 3.11-3.13)
│   │   ├── publish.yml              # Publish to PyPI on git tags
│   │   └── docs-deploy.yml          # Deploy docs to GitHub Pages
│   ├── dependabot.yml               # Automated dependency updates
│   └── CODEOWNERS                   # Code review requirements
├── pyproject.toml                   # Project metadata & dependencies
├── mkdocs.yml                       # MkDocs configuration
├── CHANGELOG.md                     # Release notes (Keep a Changelog format)
├── CONTRIBUTING.md                  # Contributing guidelines
├── CODE_OF_CONDUCT.md               # Community guidelines
├── SECURITY.md                      # Vulnerability reporting
├── AUTHORS.md                       # Contributor credits
├── README.md                         # User documentation
├── LICENSE                          # MIT License
└── .pre-commit-config.yaml          # Pre-commit hooks
```

## Key Files & Responsibilities

### Core Files

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point; handles `--init`, `--check-config`; runs async app |
| `config.py` | Config loading/saving with platform-specific paths (XDG, macOS, Windows) |
| `api/client.py` | Async wrapper around official miniflux Python library |
| `api/models.py` | Dataclasses: `Entry`, `Feed` with helper properties |
| `ui/app.py` | Main `MinifluxTUI` Textual App; screen management; entry loading |
| `ui/screens/entry_list.py` | Entry list screen with sorting, grouping, navigation |
| `ui/screens/entry_reader.py` | Entry detail view with HTML→Markdown conversion |

### Recent Modifications (Key Behaviors)

#### entry_list.py
- **Sorting modes**: "date" (newest first), "feed" (alphabetical + date), "status" (unread first)
- **Grouping**: When enabled (`g` key), groups by feed title and sorts by published date within each feed
- **Grouped mode navigation**: Uses CSS-based hiding to preserve cursor position
  - All entries are always in the list (structure never changes)
  - Collapsed entries have "collapsed" CSS class (display: none)
  - j/k navigation skips hidden entries automatically
  - Cursor position naturally preserved during expand/collapse
- **Navigation**: `j`/`k` (or arrow keys) to navigate; skips hidden entries
- **Stored state**: `self.sorted_entries` tracks currently sorted order for proper J/K navigation in entry reader
- **Filtering**: `u` (unread only), `t` (starred only)
- **Key bindings**:
  - `j/k` - cursor down/up (skips hidden entries)
  - `enter` - select entry
  - `m` - toggle read/unread
  - `*` - toggle starred
  - `e` - save entry
  - `s` - cycle sort mode
  - `g` - toggle group by feed
  - `l/h` - expand/collapse feed
  - `r/,` - refresh entries
  - `u` - show unread only
  - `t` - show starred only

#### entry_reader.py
- **Display**: Shows entry title, feed name, publish date, URL, and HTML content (converted to Markdown)
- **Navigation**: `J/K` (uppercase) to navigate between entries in current list order
- **Actions**: Mark unread, toggle starred, open in browser, fetch original content
- **Critical fix**: Uses `entry_list` parameter passed from entry_list screen for correct navigation order

## Architecture Patterns

### Async/Await Pattern
- UI is synchronous (Textual), API calls are async
- `api/client.py` converts sync miniflux calls to async using `run_in_executor`
- Screen actions marked with `async def` when making API calls

### Screen Navigation
- `EntryListScreen` → User selects entry → `push_entry_reader(entry, entry_list, current_index)`
- Entry reader can navigate with J/K using the `entry_list` passed at open time
- Back button pops screen and returns to entry list

### Data Flow
```bash
config.py (load/validate)
  → app.py (create MinifluxTUI)
  → client.py (async API calls)
  → models.py (Entry/Feed objects)
  → screens (display & user interaction)
```

## Setup & Development

### Installation

#### Option 1: From PyPI (Recommended for users)
```bash
uv pip install miniflux-tui-py

# Create config
miniflux-tui --init

# Run application
miniflux-tui
```

#### Option 2: From Source (Recommended for development)
```bash
# Install uv package manager (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/reuteras/miniflux-tui-py.git
cd miniflux-tui-py
uv sync --all-groups  # Install all dependencies including dev and docs tools

# Create config (interactive)
uv run miniflux-tui --init

# Run application
uv run miniflux-tui
```

### Git Workflow (CRITICAL)

**⚠️ NEVER push directly to main branch.** The main branch is protected and enforces:
1. All changes must come through pull requests
2. All CI checks (tests, linting, type checking) must pass
3. Code review may be required before merging
4. Only up-to-date branches can be merged

**All development must follow this workflow:**

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# 2. Make changes locally
# (Edit files, make improvements)

# 3. Test your changes before committing
uv run ruff check .              # Lint
uv run ruff format .             # Format
uv run pyright                   # Type check
uv run pytest tests              # Run tests

# 4. Commit with clear message
git add .
git commit -m "Description of changes"

# 5. Push to origin (never directly to main)
git push origin feature/your-feature-name

# 6. Create a Pull Request on GitHub
# - Click "New Pull Request" on the repository
# - CI will automatically run all checks
# - Wait for review and approval

# 7. After PR is merged, clean up
git checkout main
git pull origin main
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

**Why this workflow?**
- Ensures code quality through automated CI checks
- Enables peer review of changes
- Maintains clear commit history
- Prevents accidental pushes that break the main branch
- Allows safe rollback if needed

### GitHub Branch Protection Rules (main branch)

The main branch has protection rules enabled via GitHub Settings. These prevent direct pushes and enforce quality standards:

**To configure branch protection on main:**

1. Go to **Settings** → **Branches** → **Add rule**
2. Apply to `main` branch
3. Enable these settings:
  - ✅ **Require a pull request before merging**
    - Require approvals: 0 (adjust if peer review needed)
    - Dismiss stale pull request approvals when new commits are pushed: ✓
  - ✅ **Require status checks to pass before merging**
    - Require branches to be up to date before merging: ✓
    - Select required checks: All CI checks (test, docs-deploy)
  - ✅ **Include administrators** (optional, for consistency)
  - ✅ **Restrict who can push to matching branches** (optional, admin-only)

These settings ensure:
- No one can push directly to main (must use PRs)
- All CI tests and checks must pass
- PRs cannot be merged until branch is up-to-date
- Stale reviews are dismissed when new commits are pushed

### Common Commands
```bash
uv sync --all-groups             # Install all dependencies (dev + docs)
uv run miniflux-tui              # Run app
uv run miniflux-tui --init       # Create config
uv run ruff check .              # Lint code
uv run ruff format .             # Format code
uv run pyright                   # Type check
uv run pytest tests              # Run tests
uv run mkdocs serve              # Preview docs locally
```

### Configuration (TOML Format)

Location varies by OS:
- Linux: `~/.config/miniflux-tui/config.toml`
- macOS: `~/Library/Application Support/miniflux-tui/config.toml`
- Windows: `%APPDATA%\miniflux-tui\config.toml`

Example:
```toml
server_url = "https://miniflux.example.com"
api_key = "your-api-key-here"
allow_invalid_certs = false

[theme]
unread_color = "cyan"
read_color = "gray"

[sorting]
default_sort = "date"       # "date", "feed", or "status"
default_group_by_feed = false
```

## Code Style & Standards

- **Line length**: 140 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes
- **Linting**: ruff (fast Python linter & formatter)
- **Type checking**: pyright (strict type checking)
- **Testing**: pytest with coverage tracking
- **Pre-commit hooks**: Enforces syntax, security checks, formatting, and type checking
- **CI/CD**: GitHub Actions runs all checks on push (not PR)
- **Documentation**: MkDocs with Material theme, auto-deployed to GitHub Pages

## Important Implementation Details

### Entry List Ordering Issue (FIXED)
**Problem**: When grouping entries by feed, J/K navigation didn't follow visual order.

**Root cause**: `entry_list.py` was passing unsorted `self.entries` to entry reader instead of the sorted version.

**Solution**:
- Added `self.sorted_entries` to track current sort order
- Pass `self.sorted_entries` to entry reader for correct J/K navigation
- Find entry index in sorted list, not original list

### Cursor Navigation (FIXED)
**Problem**: `j/k` keys didn't work in entry list.

**Root cause**: `action_cursor_down/up` tried to use `self.app.set_focus()` on nested ListItems (invalid widget hierarchy).

**Solution**: Delegate directly to ListView's `action_cursor_down()` and `action_cursor_up()` methods.

## Common Tasks

### Adding a New Keyboard Binding
1. Add `Binding` tuple to `BINDINGS` list in the screen class
2. Create `action_*` method in the same screen
3. For API calls, mark as `async def` and await the call

Example:
```python
BINDINGS = [
    Binding("x", "do_something", "Do Something"),
]

async def action_do_something(self):
    """Description."""
    if hasattr(self.app, "client"):
        await self.app.client.some_api_call()
```

### Adding a New Screen
1. Create file in `ui/screens/`
2. Extend `Screen` class from textual
3. Implement `compose()` for UI layout
4. Add bindings and action methods
5. Push screen from app: `self.app.push_screen(MyScreen())`

### Modifying Entry Display
- Entry list: Edit `EntryListItem` in `entry_list.py`
- Entry detail: Edit `compose()` and `refresh_screen()` in `entry_reader.py`
- Remember to keep data model in sync via `api/models.py`

## Dependencies

**Runtime**:
- `textual>=0.82.0` - TUI framework
- `miniflux>=0.0.11` - Official Miniflux API client
- `html2text>=2024.2.26` - HTML to Markdown conversion
- `tomli>=2.0.1` - TOML parsing (Python <3.11)

**Development** (included with `uv sync`):
- `ruff>=0.6.0` - Fast linter & formatter
- `pyright>=1.1.0` - Static type checker
- `pytest>=8.0.0` - Testing framework
- `pytest-asyncio>=0.23.0` - Async test support
- `pytest-cov>=4.0.0` - Coverage reporting
- `pylint>=4.0.2` - Additional code linting

**Documentation** (included with `uv sync` or `pip install .[docs]`):
- `mkdocs>=1.5.0` - Documentation generator
- `mkdocs-material>=9.4.0` - Material theme for MkDocs
- `mkdocstrings[python]>=0.23.0` - Auto-generate API docs from docstrings

## Known Patterns & Conventions

### Screen Initialization
Screens receive data via constructor params, not global state:
```python
def __init__(self, entry: Entry, entry_list: list, current_index: int, **kwargs):
    super().__init__(**kwargs)
    self.entry = entry
    self.entry_list = entry_list
    self.current_index = current_index
```

### Async API Calls
Always check for app.client before calling:
```python
async def action_mark_read(self):
    if hasattr(self.app, "client") and self.app.client:
        await self.app.client.mark_as_read(self.entry.id)
```

### State Updates
- Screens update local data model (`entry.is_read = True`)
- Call API to persist changes
- Call `_populate_list()` or `refresh_screen()` to update UI

## Recent Changes (v0.1.1)

Major improvements in October 2025:
- **Grouped mode navigation fixed**: CSS-based hiding instead of list rebuilding
  - Cursor position now preserved during expand/collapse
  - j/k navigation automatically skips hidden entries
- **PyPI package infrastructure**: Published to PyPI with OIDC secure publishing
- **Comprehensive documentation**: MkDocs site with installation, usage, and API reference
- **GitHub Actions CI/CD**:
  - Automated testing on Python 3.11, 3.12, 3.13
  - Type checking with pyright
  - Test coverage tracking with codecov
  - Auto-deploy docs to GitHub Pages
  - Auto-publish to PyPI on version tags
- **Professional tooling**:
  - Pre-commit hooks with pyright type checking
  - Standard community files (CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY)
  - Dependabot for automated dependency updates
- **Code quality**:
  - Added constants.py for centralized configuration
  - Added performance.py for optimization tracking
  - Added utils.py for helper functions
  - Incremental refresh for better performance

## Testing & Quality Assurance

- **Automated CI/CD**: GitHub Actions runs on every push
  - Tests Python 3.11, 3.12, 3.13
  - Minimum 60% test coverage required
  - Type checking with pyright
  - Linting with ruff
- **Pre-commit hooks**: Enforces quality before commit
  - ruff linting and formatting
  - pyright type checking
  - YAML validation
  - Security checks
- **Manual testing**: Test with different Miniflux instances and feed sizes
- **Test suite**: Basic pytest coverage in tests/ directory

## Troubleshooting

**Keys don't work**: Check bindings list in screen class - must have matching `action_*` method.

**Navigation jumps around**: Verify `current_index` and `entry_list` are passed correctly to entry reader from entry list.

**Config not found**: Run `uv run miniflux-tui --init` to create default config in correct OS-specific location.

**API errors**: Check network connectivity and API key in config; verify Miniflux server is accessible.

## References

- [Textual Documentation](https://textual.textualize.io/)
- [Miniflux Project](https://miniflux.app)
- [Original cliflux (Rust)](https://github.com/spencerwi/cliflux)
