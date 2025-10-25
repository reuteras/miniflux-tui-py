# miniflux-tui-py

<div align="center">
  <img src="assets/logo.png" alt="miniflux-tui-py logo" width="128" height="128">
</div>

A Python Terminal User Interface (TUI) client for [Miniflux](https://miniflux.app) - a self-hosted RSS reader. This tool provides a keyboard-driven interface to browse, read, and manage RSS feeds directly from the terminal.

## Features

- **Keyboard-driven navigation** - Vim-style keybindings for efficient browsing
- **Multiple view modes** - Group by feed, sort by date/feed/status
- **Feed management** - Mark entries as read/unread, star/unstar favorites
- **Collapsible feed groups** - Expand/collapse feeds to focus on what matters
- **Responsive layout** - Optimized for terminal viewing
- **Secure configuration** - Support for self-signed certificates and custom API keys

## Quick Start

### Installation

```bash
pip install miniflux-tui-py
```

### Configuration

Create your configuration with:

```bash
miniflux-tui --init
```

This will prompt you for your Miniflux server URL and API key.

### Running

```bash
miniflux-tui
```

## Key Bindings

| Key | Action |
|-----|--------|
| `j` / `k` | Navigate down/up |
| `Enter` | Open entry |
| `m` | Mark as read/unread |
| `*` | Toggle star |
| `s` | Cycle sort mode |
| `g` | Toggle group by feed |
| `l` / `h` | Expand/collapse feed |
| `r` | Refresh entries |
| `u` | Show unread entries |
| `t` | Show starred entries |
| `?` | Show help |
| `q` | Quit |

## Documentation

- [Installation Guide](installation.md)
- [Configuration](configuration.md)
- [Usage Guide](usage.md)
- [Contributing](contributing.md)
- [API Reference](api/client.md)

## Requirements

- Python 3.11 or later
- A running Miniflux instance
- Terminal with 24+ colors (for best experience)

## License

MIT License - see LICENSE file for details

## Author

Peter Reuterås ([@reuteras](https://github.com/reuteras))
