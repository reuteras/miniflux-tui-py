# Configuration

## Config File Format

The configuration is stored in TOML format. You can edit it manually or use `miniflux-tui --init` to set it up interactively.

## Configuration Options

### Server Settings

```toml
server_url = "https://miniflux.example.com"
api_key = "your-api-key-here"
allow_invalid_certs = false
```

- **server_url**: The URL of your Miniflux instance
- **api_key**: Your Miniflux API token (get this from Settings → API Tokens)
- **allow_invalid_certs**: Set to `true` if your server uses a self-signed certificate (not recommended for production)

### Theme Settings

```toml
[theme]
unread_color = "cyan"
read_color = "gray"
```

Available colors depend on your terminal, but common options include:
- `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
- `bright_*` variants (e.g., `bright_blue`)
- `gray`, `dark_gray`

### Sorting Settings

```toml
[sorting]
default_sort = "date"
default_group_by_feed = false
```

- **default_sort**: Default sort mode on startup
  - `"date"` - Newest entries first (default)
  - `"feed"` - Alphabetically by feed name
  - `"status"` - Unread entries first

- **default_group_by_feed**: Whether to group by feed on startup
  - `false` - Show flat list (default)
  - `true` - Show grouped by feed

## Example Configuration

```toml
server_url = "https://miniflux.example.com"
api_key = "your-secret-api-key"
allow_invalid_certs = false

[theme]
unread_color = "cyan"
read_color = "gray"

[sorting]
default_sort = "date"
default_group_by_feed = true
```

## Configuration File Location

### Linux

The config file is stored in `$XDG_CONFIG_HOME` (defaults to `~/.config`):

```
~/.config/miniflux-tui/config.toml
```

### macOS

The config file is stored in `~/Library/Application Support`:

```
~/Library/Application Support/miniflux-tui/config.toml
```

### Windows

The config file is stored in `%APPDATA%`:

```
%APPDATA%\miniflux-tui\config.toml
```

## Verifying Your Configuration

To check if your configuration is valid without launching the app:

```bash
miniflux-tui --check-config
```

## Troubleshooting

### Configuration not found

Run `miniflux-tui --init` to create a new configuration.

### Cannot connect to server

- Verify your `server_url` is correct (including `https://` or `http://`)
- Check that your Miniflux instance is accessible
- Verify your API key is correct (copy it from Settings → API Tokens)

### SSL certificate errors

If you're using a self-signed certificate, set `allow_invalid_certs = true` in your config. Note: This is only recommended for local development.

### Wrong colors

Not all terminals support all colors. Try using standard colors like `cyan`, `yellow`, `blue`, etc. If colors still don't work, your terminal may not support 24-bit colors.
