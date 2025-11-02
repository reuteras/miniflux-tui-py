"""Configuration management for Miniflux TUI."""

from __future__ import annotations

import os
import shlex
import subprocess  # nosec B404
import sys
import tomllib
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from textwrap import dedent


def _normalize_command(command: Sequence[str] | str) -> tuple[str, ...]:
    """Normalize a command into a tuple of executable arguments."""
    if isinstance(command, str):
        parts = shlex.split(command, posix=(os.name != "nt"))
    elif isinstance(command, Sequence):
        parts = list(command)
    else:
        msg = "Command must be provided as a string or list of strings"
        raise TypeError(msg)

    if not parts:
        msg = "Command must contain at least one argument"
        raise ValueError(msg)

    normalized: list[str] = []
    for part in parts:
        if not isinstance(part, str):
            msg = "Command arguments must be strings"
            raise TypeError(msg)
        if not part:
            msg = "Command arguments cannot be empty strings"
            raise ValueError(msg)
        normalized.append(part)

    return tuple(normalized)


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
    elif "password" not in config_dict:
        validations.append(("password" in config_dict, "Missing required field: password"))
    else:
        server_url = config_dict["server_url"]
        password_command = config_dict["password"]

        # Validate server_url
        validations.append(
            (
                isinstance(server_url, str) and server_url.strip(),
                "server_url must be a non-empty string",
            )
        )
        validations.append(
            (
                (server_url.startswith(("http://", "https://")) if isinstance(server_url, str) else False),
                "server_url must start with http:// or https://",
            )
        )

        try:
            _normalize_command(password_command)
            is_valid_password = True
        except (TypeError, ValueError):
            is_valid_password = False

        validations.append(
            (
                is_valid_password,
                "password must be a valid command (string or list of strings)",
            )
        )

        if "api_key" in config_dict:
            validations.append(
                (
                    False,
                    "api_key is no longer supported. Replace it with a password command.",
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
        password: Sequence[str] | str,
        *,
        allow_invalid_certs: bool = False,
        unread_color: str = "cyan",
        read_color: str = "gray",
        default_sort: str = "date",
        default_group_by_feed: bool = False,
        group_collapsed: bool = False,
    ):
        self.server_url = server_url
        self._password_command = _normalize_command(password)
        self._api_key_cache: str | None = None
        self.allow_invalid_certs = allow_invalid_certs
        self.unread_color = unread_color
        self.read_color = read_color
        self.default_sort = default_sort
        self.default_group_by_feed = default_group_by_feed
        self.group_collapsed = group_collapsed

    @property
    def password_command(self) -> tuple[str, ...]:
        """Return the configured command used to retrieve the API token."""
        return self._password_command

    def get_api_key(self, *, refresh: bool = False) -> str:
        """
        Execute the password command and return the Miniflux API token.

        The result is cached. Pass ``refresh=True`` to force re-execution.
        """
        if not refresh and self._api_key_cache is not None:
            return self._api_key_cache

        try:
            # Command originates from a trusted local configuration file.
            completed = subprocess.run(  # nosec B603
                self._password_command,
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError as exc:
            msg = f"Password command failed: {exc}"
            raise RuntimeError(msg) from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            msg = f"Password command exited with status {exc.returncode}"
            if stderr:
                msg = f"{msg}: {stderr}"
            raise RuntimeError(msg) from exc

        api_key = (completed.stdout or "").strip()
        if not api_key:
            msg = "Password command returned empty output"
            raise RuntimeError(msg)

        self._api_key_cache = api_key
        return api_key

    @property
    def api_key(self) -> str:
        """Backward-compatible access to the retrieved API token."""
        return self.get_api_key()

    @classmethod
    def from_file(cls, path: Path) -> Config:
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

        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, TypeError) as exc:
            msg = f"Invalid configuration: {exc}"
            raise ConfigurationError(msg) from exc

        # Validate configuration
        is_valid, error_msg = validate_config(data)
        if not is_valid:
            hint_messages: list[str] = []

            if "Missing required field: password" in error_msg:  # nosec: CWE-208 - Non-cryptographic string comparison
                hint_messages.append(
                    dedent(
                        """
                        This configuration predates the password-command format introduced in v0.4.19.
                        Add a `password` command that returns your Miniflux API token. For example:

                            password = ["op", "read", "op://Personal/Miniflux/API Token"]

                        Alternatively run `miniflux-tui --init` to generate a fresh template and copy
                        your settings across.
                        """
                    ).strip()
                )

            if "api_key" in data:
                hint_messages.append(
                    dedent(
                        """
                        Remove the deprecated `api_key` entry and configure a `password` command instead.
                        The command should output your Miniflux API token, for example:

                            password = ["op", "read", "op://Personal/Miniflux/API Token"]
                        """
                    ).strip()
                )

            msg = f"Invalid configuration: {error_msg}"
            if hint_messages:
                msg = f"{msg}\n\n" + "\n\n".join(hint_messages)

            raise ConfigurationError(msg)

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
            password=data["password"],
            allow_invalid_certs=data.get("allow_invalid_certs", False),
            unread_color=unread_color,
            read_color=read_color,
            default_sort=default_sort,
            default_group_by_feed=default_group_by_feed,
            group_collapsed=group_collapsed,
        )


def _resolve_unix_config_home() -> PurePosixPath:
    """Return the base configuration directory for Unix-like systems."""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return PurePosixPath(xdg_config_home)

    home_env = os.environ.get("HOME")
    if home_env:
        return PurePosixPath(home_env) / ".config"

    try:
        return PurePosixPath(Path.home().as_posix()) / ".config"
    except RuntimeError:
        # Fallback to a sensible default when the home directory cannot be determined
        return PurePosixPath("/home") / ".config"


def get_config_dir() -> Path | PurePosixPath:
    """
    Get the configuration directory for the application.

    Returns:
        Path to config directory
    """
    if sys.platform == "win32":
        # Windows
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "miniflux-tui"

    # Linux, macOS, and other Unix-like systems
    base = _resolve_unix_config_home()
    if os.name == "nt":
        # When running tests on Windows that simulate Unix platforms,
        # preserve POSIX formatting for consistency with Unix expectations.
        return base / "miniflux-tui"

    return Path(base) / "miniflux-tui"


def get_config_file_path() -> Path:
    """
    Get the path to the configuration file.

    Returns:
        Path to config.toml
    """
    return Path(get_config_dir()) / "config.toml"


def create_default_config() -> Path:
    """
    Create a default configuration file.

    Returns:
        Path to the created config file
    """
    config_dir = Path(get_config_dir())
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "config.toml"

    default_config = """# Miniflux TUI Configuration

# Required: Your Miniflux server URL
server_url = "https://miniflux.example.com"

# Required: Command that outputs your Miniflux API token (no secrets stored on disk)
# Replace the example below with a command from your password manager.
# The command should write ONLY the token to stdout without additional text.
password = ["op", "read", "op://Personal/Miniflux/API Token"]

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

    # Always write config using UTF-8 to avoid locale-dependent encoding issues
    with Path.open(config_path, "w", encoding="utf-8") as f:
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


class ConfigurationError(ValueError):
    """Raised when the configuration file is invalid or outdated."""
