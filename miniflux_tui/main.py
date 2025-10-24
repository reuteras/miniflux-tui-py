"""Main entry point for Miniflux TUI application."""

import argparse
import asyncio
import sys
import traceback

from .config import create_default_config, get_config_file_path, load_config
from .ui.app import run_tui


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="A Python TUI client for Miniflux RSS reader")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create a default configuration file",
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

    # Handle --init flag
    if args.init:
        config_path = create_default_config()
        print(f"Created default configuration file at: {config_path}")
        print("\nPlease edit this file and add your Miniflux server URL and API key.")
        print("You can generate an API key from Settings > API Keys in Miniflux.")
        return 0

    # Handle --check-config flag
    if args.check_config:
        config_path = get_config_file_path()
        if not config_path.exists():
            print(f"Error: Config file not found at {config_path}")
            print("Run 'miniflux-tui --init' to create a default configuration.")
            return 1

        try:
            config = load_config()
            if config:
                print("Configuration loaded successfully!")
                print(f"\nServer URL: {config.server_url}")
                print(f"API Key: {'*' * 20} (hidden)")
                print(f"Allow Invalid Certs: {config.allow_invalid_certs}")
                print("\nTheme:")
                print(f"  Unread Color: {config.unread_color}")
                print(f"  Read Color: {config.read_color}")
                print("\nSorting:")
                print(f"  Default Sort: {config.default_sort}")
                print(f"  Group by Feed: {config.default_group_by_feed}")
                return 0
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return 1

    # Normal application startup
    config = load_config()
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


if __name__ == "__main__":
    sys.exit(main())
