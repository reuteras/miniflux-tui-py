# AGENT.md - miniflux-tui-py Project Guide

This document provides context about the miniflux-tui-py project for coding agents working via the Codex CLI.

## Project Overview

**miniflux-tui-py** is a Python Terminal User Interface (TUI) client for [Miniflux](https://miniflux.app) - a self-hosted RSS reader. It provides a keyboard-driven interface to browse, read, and manage RSS feeds directly from the terminal.

- **Language**: Python 3.11+
- **Supported Python Versions**: 3.11, 3.12, 3.13, 3.14, 3.15 (preview)
- **Framework**: Textual (TUI framework)
- **Status**: Production/Stable
- **License**: MIT
- **Author**: Peter Reuterås
- **PyPI**: Available at <https://pypi.org/project/miniflux-tui-py/>
- **Docs**: <https://reuteras.github.io/miniflux-tui-py/>
- **Security**: OpenSSF Best Practices, SLSA attestation

This is a Python reimplementation of [cliflux](https://github.com/spencerwi/cliflux) (original Rust implementation).

## Directory Structure

```
miniflux_tui/
├── main.py                      # Entry point; handles --init, --check-config
├── config.py                    # Config loading with platform-specific paths
├── constants.py                 # Application constants
├── performance.py               # Performance utilities
├── utils.py                     # Helper utilities
├── api/
│   ├── client.py                # Async Miniflux API wrapper (run_in_executor)
│   └── models.py                # Dataclasses: Category, Entry, Feed
└── ui/
    ├── app.py                   # Main MinifluxTuiApp; screen management
    └── screens/
        ├── entry_list.py        # Entry list with sorting/grouping
        ├── entry_reader.py      # Entry detail view; HTML→Markdown
        ├── entry_history.py     # Reading history
        ├── category_management.py
        ├── feed_management.py
        ├── feed_settings.py
        ├── settings_management.py
        ├── status.py            # Problematic feeds dashboard
        ├── help.py
        ├── confirm_dialog.py
        ├── input_dialog.py
        ├── settings_edit_dialog.py
        ├── scraping_helper.py
        ├── rules_helper.py
        └── loading.py
tests/                           # pytest suite (conftest.py + test_*.py)
```

## Architecture Patterns

### Async/Await Pattern

- UI is synchronous (Textual), API calls are async
- `api/client.py` converts sync miniflux calls to async using `run_in_executor`
- Screen actions marked with `async def` when making API calls

### Screen Navigation

- `EntryListScreen` → User selects entry → `push_entry_reader(entry, entry_list, current_index)`
- Entry reader can navigate with J/K using the `entry_list` passed at open time
- Back button pops screen and returns to entry list

## Development

### Git Workflow

Direct commits to main are allowed. Feature branches are optional but fine for larger changes.

**Before committing:**

```bash
uv sync --all-groups             # Install all dependencies
uv run ruff check .              # Lint
uv run ruff format .             # Format
uv run pyright                   # Type check
uv run pytest tests              # Run tests
```

**Linting and CI failures:**

When any linter or type checker (ruff, pyright, mypy via the `Lint Code Base` GitHub Action, etc.) reports an error, fix it. Do not spend effort determining which commit or model introduced the error, whether it predates the current change, or whether it's "in scope" for the current task — that investigation is a waste of resources and the answer never changes what needs to happen next. Fix what's reported, verify the fix locally with the relevant tool, and move on. If a genuinely large body of pre-existing errors surfaces (e.g. a linter newly enabled or newly run against untouched files), fix all of them rather than only the files touched by the current change, unless the user says otherwise.

Note: CI runs both `pyright` (this project's primary type checker, see below) and `mypy` via super-linter's `PYTHON_MYPY` check in `.github/workflows/linter.yml`. mypy is not a project dependency (`uv sync` won't install it) — verify with `uv run --with mypy==2.1.0 mypy miniflux_tui tests` before assuming a type-annotation fix is CI-clean. The two checkers disagree on some patterns (e.g. `BINDINGS` list typing on `Screen` subclasses) — a fix for one must not regress the other. Always verify both after touching type annotations.

**Commit message format:**

```bash
git commit -m "feat: Add new feature"
git commit -m "fix: Fix bug in navigation"
git commit -m "docs: Update README"
git commit -m "refactor: Refactor entry list"
git commit -m "chore: Update dependencies"
```

**⚠️ CRITICAL: SSH SIGNING WITH 1PASSWORD**

**If commit signing fails or doesn't work, STOP and WAIT immediately. Do NOT proceed.**

**Never:**
- ❌ Try to disable signing (commit.gpgsign=false)
- ❌ Try to commit without signing
- ❌ Use alternate signing methods
- ❌ Attempt any workaround

**If you get signing errors:**
1. Stop all work

This ensures all commits are verified and trusted.

### Configuration (TOML Format)

- Linux/macOS: `~/.config/miniflux-tui/config.toml`
- Windows: `%APPDATA%\miniflux-tui\config.toml`

Key fields: `server_url`, `api_key`, `allow_invalid_certs`, `[theme]`, `[sorting]`.

## Security Design Principles

This application processes untrusted content from RSS feeds, including feeds from security blogs that may contain malware examples. Security is a top priority.

### Allowlists over blocklists

**Always use allowlists, never blocklists, for HTML sanitization.**

A blocklist enumerates known-bad things (e.g. `dangerous_tags = {"script", "iframe", ...}`). It is inherently incomplete: any new dangerous tag or URL scheme invented after the list was written slips straight through. An allowlist enumerates known-good things; anything not on the list is rejected by default.

Apply this principle to every layer of HTML sanitization:

| Layer       | Wrong (blocklist)                          | Right (allowlist)                           |
|-------------|--------------------------------------------|---------------------------------------------|
| Tags        | `if tag in dangerous_tags: decompose()`    | `if tag not in ALLOWED_TAGS: unwrap()`      |
| URL schemes | `if url.startswith("javascript:"): remove` | `if scheme not in ALLOWED_SCHEMES: remove`  |
| Attributes  | `if attr.startswith("on"): remove`         | `if attr not in ALLOWED_ATTRS[tag]: remove` |

**Existing sanitizers** follow this pattern:

- `miniflux_tui/scraping/analyzer.py` — `_sanitize_html()` uses `ALLOWED_TAGS`, `ALLOWED_ATTRS`, `_ALLOWED_SCHEMES`
- `miniflux_tui/ui/screens/entry_reader.py` — `_sanitize_feed_html()` uses `_FEED_ALLOWED_TAGS`, `_FEED_ALLOWED_ATTRS`, `_FEED_ALLOWED_SCHEMES`
- `miniflux_tui/docs_fetcher.py` — `_sanitize_html()` uses `_DOCS_ALLOWED_TAGS`, `_DOCS_ALLOWED_ATTRS`, `_DOCS_ALLOWED_SCHEMES`

**When adding a new sanitizer:** define an allowlist of permitted tags, per-tag permitted attributes, and permitted URL schemes. Do not add a blocklist of dangerous tags or schemes; the allowlist already rejects everything not explicitly permitted.

### Unwrap vs decompose for non-allowed tags

Non-allowed tags are **unwrapped** (tag markup removed, text content preserved). In a TUI, text content from `<script>` or `<style>` tags is just text — it is never executed. For security blogs that show malware examples, displaying the code as text is the correct behaviour.

### URL scheme allowlist

Permitted schemes for user-facing URLs: `http`, `https`, `mailto`. Relative URLs (no scheme) are always permitted. Everything else — including `javascript:`, `vbscript:`, `data:` — is rejected by the allowlist check (no colon → relative, colon present → scheme must be in the allowlist).

## Code Style & Standards

- **Line length**: 140 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes
- **Markdown**: No bare URLs — use `[text](url)` link syntax
- **Target Python**: 3.11+
- **Linting**: ruff — see `pyproject.toml` for full rule set
- **Type checking**: pyright (standard mode)
- **Testing**: pytest, minimum 60% coverage
- **Commit signing**: Required (SSH with 1Password)

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

### Modifying Entry Display

- Entry list: Edit `EntryListItem` in `entry_list.py`
- Entry detail: Edit `compose()` and `refresh_screen()` in `entry_reader.py`
- Remember to keep data model in sync via `api/models.py`

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

### State Updates

- Screens update local data model (`entry.is_read = True`)
- Call API to persist changes
- Call `_populate_list()` or `refresh_screen()` to update UI

## Release Process for AI Agents

**⚠️ CRITICAL: AI agents should NEVER manually run releases. Releases are maintainer-only operations.**

**NEVER:**
- ❌ Trigger the release workflow
- ❌ Manually edit version in `pyproject.toml` for release
- ❌ Create or push git tags
- ❌ Manually publish to PyPI
- ❌ Create GitHub releases
- ❌ Modify release workflows without maintainer approval

### Conventional Commit Format

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or fixes
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

**Examples:**
```bash
feat: Add category filtering to entry list (#42)
fix: Correct cursor position after feed collapse (#55)
docs: Update installation instructions for Windows
refactor: Extract API retry logic into separate function
test: Add integration tests for feed refresh
```

## Common Development Patterns

### Adding a New Feed Setting
1. Check if the Miniflux API supports the setting (check miniflux Python client)
2. Add field to `Feed` model in `api/models.py`
3. Add UI widget in `feed_settings.py` compose method
4. Add save logic in `action_save()` method
5. Test with real Miniflux server

### Working with Dialogs
Use existing dialog components:
- `ConfirmDialog` - Yes/No confirmations
- `InputDialog` - Text input
- `SettingsEditDialog` - Settings editor

Push dialog and await result:
```python
result = await self.app.push_screen_wait(ConfirmDialog("Are you sure?"))
if result:
    # User confirmed
```

## Troubleshooting

**Keys don't work**: Check bindings list in screen class - must have matching `action_*` method.

**Navigation jumps around**: Verify `current_index` and `entry_list` are passed correctly to entry reader from entry list.

**Config not found**: Run `uv run miniflux-tui --init` to create default config in correct OS-specific location.

**Pre-commit hooks fail**: Run `uv run ruff format .` and `uv run ruff check . --fix` to auto-fix most issues.

**Commit signing fails**: Stop and wait for maintainer.

**Coverage too low**: Add more tests in `tests/`. Use `uv run pytest --cov=miniflux_tui --cov-report=html` to see the report.
