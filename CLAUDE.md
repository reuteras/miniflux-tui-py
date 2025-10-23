# CLAUDE.md - miniflux-tui-py Project Guide

This document provides context about the miniflux-tui-py project for Claude Code.

## Project Overview

**miniflux-tui-py** is a Python Terminal User Interface (TUI) client for [Miniflux](https://miniflux.app) - a self-hosted RSS reader. It provides a keyboard-driven interface to browse, read, and manage RSS feeds directly from the terminal.

- **Language**: Python 3.11+
- **Framework**: Textual (TUI framework)
- **Status**: Alpha (v0.1.0)
- **License**: MIT
- **Author**: Peter Reuterås

This is a Python reimplementation of [cliflux](https://github.com/spencerwi/cliflux) (original Rust implementation).

## Directory Structure

```
miniflux-tui-py/
├── miniflux_tui/                    # Main package
│   ├── __init__.py
│   ├── main.py                      # Entry point & CLI argument handling
│   ├── config.py                    # Configuration management
│   ├── api/
│   │   ├── client.py                # Async Miniflux API wrapper
│   │   └── models.py                # Data models (Entry, Feed)
│   └── ui/
│       ├── app.py                   # Main Textual App
│       └── screens/
│           ├── entry_list.py        # Entry list with sorting/grouping
│           ├── entry_reader.py      # Entry detail view
│           └── help.py              # Help/keyboard shortcuts
├── pyproject.toml                   # Project metadata & dependencies
├── README.md                         # User documentation
└── .editorconfig, .pre-commit-config.yaml, etc.
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
- **Navigation**: `j`/`k` (or arrow keys) to navigate; uses ListView's built-in cursor movement
- **Stored state**: `self.sorted_entries` tracks currently sorted order for proper J/K navigation in entry reader
- **Key bindings**:
    - `j/k` - cursor down/up
    - `enter` - select entry
    - `m` - toggle read/unread
    - `*` - toggle starred
    - `s` - cycle sort mode
    - `g` - toggle group by feed

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
```
config.py (load/validate)
    → app.py (create MinifluxTUI)
    → client.py (async API calls)
    → models.py (Entry/Feed objects)
    → screens (display & user interaction)
```

## Setup & Development

### Installation
```bash
# Install uv package manager (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/reuteras/miniflux-tui-py.git
cd miniflux-tui-py
uv sync  # Install dependencies

# Create config (interactive)
uv run miniflux-tui --init

# Run application
uv run miniflux-tui
```

### Common Commands
```bash
uv sync                      # Install dependencies
uv run miniflux-tui          # Run app
uv run miniflux-tui --init   # Create config
uv run ruff check .          # Lint code
uv run ruff format .         # Format code
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
- **Tools**: ruff (linting & formatting), pylint (additional checking)
- **Pre-commit hooks**: Enforces syntax, security checks, and formatting

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

**Development**:
- `pylint>=4.0.2` - Code linting
- `ruff>=0.6.0` - Fast linter & formatter

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

## Recent Changes

Recent modifications include:
- Fixed entry ordering when using grouping (g key) - now uses `sorted_entries` consistently
- Fixed j/k navigation - simplified to use ListView's native methods
- Entry reader refactoring for better content display

## Testing & Quality Assurance

- No automated tests currently (pytest removed per commit history)
- Use `ruff check .` for linting before commits
- Use `.pre-commit-config.yaml` hooks for automated checks
- Test manually with different Miniflux instances

## Troubleshooting

**Keys don't work**: Check bindings list in screen class - must have matching `action_*` method.

**Navigation jumps around**: Verify `current_index` and `entry_list` are passed correctly to entry reader from entry list.

**Config not found**: Run `uv run miniflux-tui --init` to create default config in correct OS-specific location.

**API errors**: Check network connectivity and API key in config; verify Miniflux server is accessible.

## References

- [Textual Documentation](https://textual.textualize.io/)
- [Miniflux Project](https://miniflux.app)
- [Original cliflux (Rust)](https://github.com/spencerwi/cliflux)
