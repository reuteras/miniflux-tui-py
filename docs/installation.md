# Installation

## Prerequisites

- Python 3.11 or later
- pip or uv package manager
- A running Miniflux instance (see [miniflux.app](https://miniflux.app))

## From PyPI

The easiest way to install miniflux-tui-py is from PyPI:

```bash
pip install miniflux-tui-py
```

Or if you use `uv`:

```bash
uv pip install miniflux-tui-py
```

Then run the application:

```bash
miniflux-tui
```

## From Source

To install from source for development:

```bash
# Clone the repository
git clone https://github.com/reuteras/miniflux-tui-py.git
cd miniflux-tui-py

# Install with uv (recommended)
uv sync

# Run the application
uv run miniflux-tui
```

## Setup Your Configuration

Before running the application for the first time, you need to configure it:

```bash
miniflux-tui --init
```

This will:
1. Prompt you for your Miniflux server URL
2. Ask for your API key
3. Optionally configure theme colors and sorting preferences
4. Create the configuration file in your system's config directory

### Configuration File Location

The configuration is saved to a platform-specific location:

- **Linux**: `~/.config/miniflux-tui/config.toml`
- **macOS**: `~/Library/Application Support/miniflux-tui/config.toml`
- **Windows**: `%APPDATA%\miniflux-tui\config.toml`

## Getting Your Miniflux API Key

1. Log in to your Miniflux instance
2. Click on "Settings" (usually in the top right)
3. Go to "API Tokens"
4. Create a new API token or copy an existing one
5. Use this token in the miniflux-tui configuration

## Verifying Installation

To verify your installation is working:

```bash
miniflux-tui --check-config
```

This will validate your configuration without launching the application.

## Updating

To update to the latest version:

```bash
pip install --upgrade miniflux-tui-py
```

Or with uv:

```bash
uv pip install --upgrade miniflux-tui-py
```
