# miniflux-tui-py

A [Python](https://www.python.org) TUI (Terminal User Interface) client for the Miniflux self-hosted RSS reader built with [textual](https://github.com/textualize/textual/).

## Installation

This project uses uv for dependency management.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/reuteras/miniflux-tui-py.git
cd miniflux-tui-py

# Install dependencies
uv sync

# Create default configuration
uv run miniflux-tui --init

# Run the application
uv run miniflux-tui
```

## Configuration

Create a configuration file at:

- **Linux**: `~/.config/miniflux-tui/config.toml`
- **macOS**: `~/Library/Application Support/miniflux-tui/config.toml`
- **Windows**: `%APPDATA%\miniflux-tui\config.toml`

Example configuration:

```toml
server_url = "https://miniflux.example.com"
api_key = "your-api-key-here"
allow_invalid_certs = false

[theme]
unread_color = "cyan"
read_color = "gray"

[sorting]
default_sort = "feed"  # Options: "feed", "date", "status"
default_group_by_feed = false
```

To generate an API key for your Miniflux account:
1. Log into your Miniflux server
2. Go to **Settings** -> **API Keys** -> **Create a new API key**

## Keyboard Shortcuts

### Entry List View

- Up/Down or k/j - Navigate entries
- Enter - Open entry
- m - Toggle read/unread
- * - Toggle starred
- e - Save entry to third-party service
- s - Cycle sort mode (feed/date/status)
- g - Toggle grouping by feed
- f - Filter by feed
- r or , - Refresh entries
- ? - Show keyboard help
- q - Quit

### Entry Reader View

- Up/Down or k/j - Scroll
- PageUp/PageDown - Fast scroll
- u - Mark as unread
- * - Toggle starred
- e - Save entry to third-party service
- o - Open in browser
- f - Fetch original content
- J - Next entry
- K - Previous entry
- b - Back to list
- ? - Show keyboard help

## Development

```bash
# Install development dependencies
uv sync --dev

# Lint code
uv run ruff check .
```

## Why Python?

This project is a Python implementation of [cliflux](https://github.com/spencerwi/cliflux) (Rust), created since I don't now Rust and wanted to do some changes to that code.

## License

MIT License - see LICENSE file for details.

## Related Projects

- [cliflux](https://github.com/spencerwi/cliflux) - Original Rust TUI client for Miniflux that inspired this tool.
- [Miniflux](https://miniflux.app) is a minimalist and opinionated feed reader.
- [textual](https://github.com/textualize/textual/)
