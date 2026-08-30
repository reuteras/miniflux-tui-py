# miniflux-tui-py

<div align="center">
  <img src="assets/logo.png" alt="miniflux-tui-py logo" width="128" height="128">
</div>

A Python Terminal User Interface (TUI) client for [Miniflux](https://miniflux.app) - a self-hosted RSS reader. Keyboard-driven, with vim-style navigation, feed/category management, runtime theme switching, and non-blocking background sync.

**Status:** Production/Stable — see the [feature overview](features/overview.md) for the full list.

## Quick Start

```bash
uv tool install miniflux-tui-py
miniflux-tui --init      # writes a starter config
miniflux-tui             # run it
```

See the [Installation Guide](installation.md) for pip/source installs and Codespaces.

## Documentation

- [Installation Guide](installation.md)
- [Configuration](configuration.md)
- [Usage Guide](usage.md) — including the full keyboard shortcut reference
- [Feature Overview](features/overview.md)
- [Contributing](contributing.md)
- [API Reference](api/client.md)

## Requirements

- Python 3.11+ (tested on 3.11-3.14, 3.15 preview)
- A running Miniflux instance
- Terminal with 24+ colors (for best experience)

## License

MIT License - see LICENSE file for details.

## Author

Peter Reuterås ([@reuteras](https://github.com/reuteras))
