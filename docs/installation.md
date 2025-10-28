# Installation

## Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip
- A running Miniflux instance (see [miniflux.app](https://miniflux.app))

## From PyPI (Recommended with uv)

The recommended way to install miniflux-tui-py is using [uv](https://docs.astral.sh/uv/), which is faster and more reliable:

```bash
# Install uv - see https://docs.astral.sh/uv/getting-started/installation/
# On macOS/Linux: brew install uv
# On Windows: choco install uv

# Install miniflux-tui-py
uv tool install miniflux-tui-py

# Run the application
miniflux-tui
```

### Alternative: Using pip

If you prefer using pip:

```bash
pip install miniflux-tui-py
miniflux-tui
```

## From Source (For Development)

To install from source for development:

```bash
# Clone the repository
git clone https://github.com/reuteras/miniflux-tui-py.git
cd miniflux-tui-py

# Install all dependencies (including dev and docs)
uv sync --all-groups

# Run the application
uv run miniflux-tui
```

## Container Image (Docker or Podman)

A signed container image is published to GitHub Container Registry on every push to `main` and for releases. To use it:

```bash
# Pull the image
docker pull ghcr.io/reuteras/miniflux-tui:latest

# Create a configuration directory on the host if it does not exist
mkdir -p ~/.config/miniflux-tui

# Generate a configuration file
docker run --rm -it \
  -v ~/.config/miniflux-tui:/home/miniflux/.config/miniflux-tui \
  ghcr.io/reuteras/miniflux-tui:latest \
  --init

# Launch the TUI with the shared configuration
docker run --rm -it \
  -v ~/.config/miniflux-tui:/home/miniflux/.config/miniflux-tui \
  ghcr.io/reuteras/miniflux-tui:latest
```

The build workflow signs the image with [Sigstore Cosign](https://docs.sigstore.dev/cosign/overview/). You can verify the signature using GitHub's OIDC identity:

```bash
cosign verify ghcr.io/reuteras/miniflux-tui:latest
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
- **macOS**: `~/.config/miniflux-tui/config.toml`
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
# With uv (recommended)
uv tool upgrade miniflux-tui-py
```

Or with pip:

```bash
pip install --upgrade miniflux-tui-py
```
