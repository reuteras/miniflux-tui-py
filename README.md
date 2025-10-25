# miniflux-tui-py

<div align="center">
  <img src="assets/logo-256.png" alt="miniflux-tui-py logo" width="128" height="128">
</div>

[![PyPI version](https://badge.fury.io/py/miniflux-tui-py.svg)](https://badge.fury.io/py/miniflux-tui-py)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Status](https://github.com/reuteras/miniflux-tui-py/workflows/Test/badge.svg)](https://github.com/reuteras/miniflux-tui-py/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/reuteras/miniflux-tui-py/graph/badge.svg)](https://codecov.io/gh/reuteras/miniflux-tui-py)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://reuteras.github.io/miniflux-tui-py/)

A [Python](https://www.python.org) TUI (Terminal User Interface) client for the Miniflux self-hosted RSS reader built with [textual](https://github.com/textualize/textual/).

## Installation

### From PyPI (Recommended with uv)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install miniflux-tui-py
uv tool install miniflux-tui-py

# Create configuration
miniflux-tui --init

# Run the application
miniflux-tui
```

### Alternative: Using pip

```bash
pip install miniflux-tui-py
miniflux-tui --init
miniflux-tui
```

### From Source (For Developers)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/reuteras/miniflux-tui-py.git
cd miniflux-tui-py

# Install all dependencies (including dev and docs)
uv sync --all-groups

# Create default configuration
uv run miniflux-tui --init

# Run the application
uv run miniflux-tui
```

## Documentation

Full documentation is available at [reuteras.github.io/miniflux-tui-py](https://reuteras.github.io/miniflux-tui-py/)

- [Installation Guide](https://reuteras.github.io/miniflux-tui-py/installation/)
- [Configuration](https://reuteras.github.io/miniflux-tui-py/configuration/)
- [Usage Guide](https://reuteras.github.io/miniflux-tui-py/usage/)
- [Contributing](https://reuteras.github.io/miniflux-tui-py/contributing/)

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

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Setting up your development environment
- Running tests and checks
- Submitting pull requests

## Development

```bash
# Install all development dependencies
uv sync --all-groups

# Lint code
uv run ruff check .

# Type check
uv run pyright miniflux_tui tests

# Run tests
uv run pytest tests --cov=miniflux_tui

# Preview documentation locally
uv run mkdocs serve
```

## Why Python?

This project is a Python implementation of [cliflux](https://github.com/spencerwi/cliflux) (Rust), created since I don't now Rust and wanted to do some changes to that code.

## License

MIT License - see LICENSE file for details.

## Related Projects

- [cliflux](https://github.com/spencerwi/cliflux) - Original Rust TUI client for Miniflux that inspired this tool.
- [Miniflux](https://miniflux.app) is a minimalist and opinionated feed reader.
- [textual](https://github.com/textualize/textual/)
