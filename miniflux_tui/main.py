# SPDX-License-Identifier: MIT
"""Main entry point for Miniflux TUI application."""

import argparse
import asyncio
import sys
import traceback

from .config import (
    Config,
    ConfigurationError,
    create_codespace_config,
    create_default_config,
    get_config_file_path,
    load_config,
)
from .ui.app import run_tui


def _print_config_summary(config: Config) -> None:
    """Display configuration values without revealing secrets."""
    print("Configuration loaded successfully!")
    print(f"\nServer URL: {config.server_url}")
    print("Password command: (hidden)")
    try:
        config.get_api_key(refresh=True)
    except RuntimeError as exc:
        print(f"API token retrieval: FAILED ({exc})")
    else:
        print("API token retrieval: success")
    print(f"Allow Invalid Certs: {config.allow_invalid_certs}")
    print("\nTheme:")
    print(f"  Unread Color: {config.unread_color}")
    print(f"  Read Color: {config.read_color}")
    print("\nSorting:")
    print(f"  Default Sort: {config.default_sort}")
    print(f"  Group by Feed: {config.default_group_by_feed}")


def _handle_init() -> int:
    """Handle the --init CLI flag."""
    config_path = create_default_config()
    print(f"Created default configuration file at: {config_path}")
    print("\nPlease edit this file and add your Miniflux server URL and password command.")
    print("The password command should retrieve your API token from a password manager.")
    return 0


def _handle_init_codespace() -> int:
    """Handle the --init-codespace CLI flag."""
    config_path = create_codespace_config()
    print(f"Created GitHub Codespaces configuration at: {config_path}")
    print("\nThis configuration reads credentials from environment variables.")
    print("\nTo use this configuration, set these secrets in GitHub:")
    print("  1. Go to your repository Settings → Secrets and variables → Codespaces")
    print("  2. Add the following secrets:")
    print("     - MINIFLUX_SERVER_URL: Your Miniflux server URL (e.g., https://miniflux.example.com)")
    print("     - MINIFLUX_API_KEY: Your Miniflux API token")
    print("\nOptional: Using Tailscale for private server access")
    print("  If your Miniflux server is on a private network:")
    print("  1. Add a Codespace secret: TAILSCALE_AUTHKEY (get from https://login.tailscale.com/admin/settings/keys)")
    print("  2. In your codespace, run:")
    print("     curl -fsSL https://tailscale.com/install.sh | sh")
    print("     sudo tailscale up --authkey=$TAILSCALE_AUTHKEY")
    print("  3. Your server will be accessible via its Tailscale hostname")
    print("  4. See https://tailscale.com/kb/1160/github-codespaces for details")
    print("\nThe TUI will start in grouped mode by default for better organization.")
    return 0


def _handle_check_config() -> int:
    """Handle the --check-config CLI flag."""
    config_path = get_config_file_path()
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        print("Run 'miniflux-tui --init' to create a default configuration.")
        return 1

    try:
        config = load_config()
    except ConfigurationError as exc:
        print("Configuration requires attention:\n")
        print(exc)
        print("\nRefer to the release notes or regenerate a template with `miniflux-tui --init`.\n")
        return 1
    except Exception as exc:
        print(f"Error loading configuration: {exc}")
        return 1

    if not config:
        print("Error: Configuration could not be loaded.")
        return 1

    _print_config_summary(config)
    return 0


def _run_application() -> int:
    """Run the main TUI application."""
    try:
        config = load_config()
    except ConfigurationError as exc:
        print("Error loading configuration:\n")
        print(exc)
        print("\nRun 'miniflux-tui --init' to create a fresh configuration template, then migrate your settings.")
        return 1
    except Exception as exc:
        print(f"Error loading configuration: {exc}")
        return 1

    if not config:
        config_path = get_config_file_path()
        print(f"Error: Config file not found at {config_path}")
        print("\nRun 'miniflux-tui --init' to create a default configuration.")
        return 1

    # Start the TUI application

    try:
        asyncio.run(run_tui(config))
        error_code = 0
    except KeyboardInterrupt:
        print("\nGoodbye!")
        error_code = 0
    except Exception as e:
        print(f"\nError running application: {e}")
        traceback.print_exc()
        error_code = 1

    return error_code


def main() -> int:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="A Python TUI client for Miniflux RSS reader")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create a default configuration file",
    )
    parser.add_argument(
        "--init-codespace",
        action="store_true",
        help="Create a configuration file optimized for GitHub Codespaces with environment variable support",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check configuration and display settings",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args()

    if args.init:
        return _handle_init()
    if args.init_codespace:
        return _handle_init_codespace()
    if args.check_config:
        return _handle_check_config()
    return _run_application()


if __name__ == "__main__":
    sys.exit(main())
