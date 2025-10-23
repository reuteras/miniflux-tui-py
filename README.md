# miniflux-tui-py

A Python TUI (Terminal User Interface) client for the Miniflux self-hosted RSS reader with enhanced feed sorting and filtering capabilities.

## Features

- View unread and starred feed entries
- Star/unstar entries
- Mark entries as read/unread
- Refresh feeds
- Open entries in browser
- Fetch original article content
- **Sort entries by feed name** (key feature!)
- **Group entries by feed**
- **Filter by specific feed**
- Fast, async API client
- Customizable themes

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
- s - Cycle sort mode (feed/date/status)
- g - Toggle grouping by feed
- f - Filter by feed
- r - Refresh entries
- ? - Show keyboard help
- q - Quit

### Entry Reader View
- Up/Down or k/j - Scroll
- PageUp/PageDown - Fast scroll
- u - Mark as unread
- * - Toggle starred
- o - Open in browser
- f - Fetch original content
- n - Next entry
- p - Previous entry
- b - Back to list
- ? - Show keyboard help

## Development

```bash
# Install development dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run ruff check .
```

## Project Structure

```bash
miniflux-tui-py/
├── miniflux_tui/
│   ├── api/
│   │   ├── client.py        # Miniflux API client
│   │   └── models.py        # Data models (Feed, Entry)
│   ├── ui/
│   │   ├── app.py           # Main TUI application
│   │   └── screens/         # TUI screens
│   ├── config.py            # Configuration loading
│   └── main.py              # CLI entry point
├── pyproject.toml
└── README.md
```

## Why Python?

This project is a Python reimplementation of cliflux (Rust), created to:

- Simplify maintenance and contribution
- Add enhanced feed sorting and filtering features
- Leverage Python's rich ecosystem for TUI development
- Provide faster prototyping for new features

## License

MIT License - see LICENSE file for details

## Related Projects

- cliflux - Original Rust TUI client for Miniflux
- Miniflux - The RSS reader this client connects to
