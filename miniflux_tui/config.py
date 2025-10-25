"""Configuration management for Miniflux TUI."""

import os
import sys
import tomllib
from pathlib import Path


def validate_config(config_dict: dict) -> tuple[bool, str]:
    """Validate configuration dictionary.

    Args:
        config_dict: Configuration dictionary to validate

    Returns:
        Tuple of (is_valid, error_message). is_valid is True if config is valid,
        error_message contains details if invalid.
    """
    # Define validation checks as tuples: (condition, error_message)
    validations = []

    # Check required fields
    if "server_url" not in config_dict:
        validations.append(("server_url" in config_dict, "Missing required field: server_url"))
    elif "api_key" not in config_dict:
        validations.append(("api_key" in config_dict, "Missing required field: api_key"))
    else:
        server_url = config_dict["server_url"]
        api_key = config_dict["api_key"]

        # Validate server_url
        validations.append(
            (
                isinstance(server_url, str) and server_url.strip(),
                "server_url must be a non-empty string",
            )
        )
        validations.append(
            (
                (
                    server_url.startswith(("http://", "https://"))
                    if isinstance(server_url, str)
                    else False
                ),
                "server_url must start with http:// or https://",
            )
        )

        # Validate api_key
        validations.append(
            (
                isinstance(api_key, str) and api_key.strip(),
                "api_key must be a non-empty string",
            )
        )
        validations.append(
            (
                (
                    len(api_key.strip()) >= 10 if isinstance(api_key, str) else False
                ),
                "api_key appears to be invalid (too short)",
            )
        )

        # Validate optional sort mode
        sorting = config_dict.get("sorting", {})
        if sorting and "default_sort" in sorting:
            default_sort = sorting["default_sort"]
            valid_sorts = ["date", "feed", "status"]
            validations.append(
                (
                    default_sort in valid_sorts,
                    f"default_sort must be one of: {', '.join(valid_sorts)}",
                )
            )

    # Check all validations
    for condition, error_msg in validations:
        if not condition:
            return False, error_msg

    return True, "Configuration valid"


class Config:
    """Configuration for Miniflux TUI application."""

    def __init__(
        self,
        server_url: str,
        api_key: str,
        allow_invalid_certs: bool = False,
        unread_color: str = "cyan",
        read_color: str = "gray",
        default_sort: str = "date",
        default_group_by_feed: bool = False,
        group_collapsed: bool = False,
    ):
        self.server_url = server_url
        self.api_key = api_key
        self.allow_invalid_certs = allow_invalid_certs
        self.unread_color = unread_color
        self.read_color = read_color
        self.default_sort = default_sort
        self.default_group_by_feed = default_group_by_feed
        self.group_collapsed = group_collapsed

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """
        Load configuration from a TOML file.

        Args:
            path: Path to the configuration file

        Returns:
            Config object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid or missing required fields
        """
        if not path.exists():
            msg = f"Config file not found: {path}"
            raise FileNotFoundError(msg)

        with Path.open(path, "rb") as f:
            data = tomllib.load(f)

        # Validate configuration
        is_valid, error_msg = validate_config(data)
        if not is_valid:
            msg = f"Invalid configuration: {error_msg}"
            raise ValueError(msg)

        # Theme settings
        theme = data.get("theme", {})
        unread_color = theme.get("unread_color", "cyan")
        read_color = theme.get("read_color", "gray")

        # Sorting settings
        sorting = data.get("sorting", {})
        default_sort = sorting.get("default_sort", "date")
        default_group_by_feed = sorting.get("default_group_by_feed", False)
        group_collapsed = sorting.get("group_collapsed", False)

        return cls(
            server_url=data["server_url"],
            api_key=data["api_key"],
            allow_invalid_certs=data.get("allow_invalid_certs", False),
            unread_color=unread_color,
            read_color=read_color,
            default_sort=default_sort,
            default_group_by_feed=default_group_by_feed,
            group_collapsed=group_collapsed,
        )


def get_config_dir() -> Path:
    """
    Get the configuration directory for the application.

    Returns:
        Path to config directory
    """
    if sys.platform == "darwin":
        # macOS
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        # Windows
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        # Linux and other Unix-like systems
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    return base / "miniflux-tui"


def get_config_file_path() -> Path:
    """
    Get the path to the configuration file.

    Returns:
        Path to config.toml
    """
    return get_config_dir() / "config.toml"


def create_default_config() -> Path:
    """
    Create a default configuration file.

    Returns:
        Path to the created config file
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "config.toml"

    default_config = """# Miniflux TUI Configuration

# Required: Your Miniflux server URL
server_url = "https://miniflux.example.com"

# Required: Your Miniflux API key
# Generate this from Settings > API Keys in your Miniflux web interface
api_key = "your-api-key-here"

# Optional: Allow invalid SSL certificates (default: false)
allow_invalid_certs = false

[theme]
# Color for unread entries (default: cyan)
unread_color = "cyan"

# Color for read entries (default: gray)
read_color = "gray"

[sorting]
# Default sort mode: "feed", "date", or "status" (default: date)
default_sort = "date"

# Default grouping by feed (default: false)
default_group_by_feed = false
"""

    with Path.open(config_path, "w") as f:
        f.write(default_config)

    return config_path


def load_config() -> Config | None:
    """
    Load configuration from the default location.

    Returns:
        Config object or None if config doesn't exist
    """
    config_path = get_config_file_path()

    if not config_path.exists():
        return None

    return Config.from_file(config_path)
