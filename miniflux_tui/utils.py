"""Utility functions and helpers for miniflux-tui."""

from contextlib import asynccontextmanager


def get_star_icon(is_starred: bool) -> str:
    """Get star icon based on starred status.

    Args:
        is_starred: Whether the entry is starred

    Returns:
        Star icon character (filled or empty)
    """
    return "★" if is_starred else "☆"


def get_status_icon(is_unread: bool) -> str:
    """Get status icon based on read/unread status.

    Args:
        is_unread: Whether the entry is unread

    Returns:
        Status icon character (filled or empty)
    """
    return "●" if is_unread else "○"


@asynccontextmanager
async def api_call(screen, operation_name: str = "Operation"):
    """Context manager for safe API calls with error handling.

    Usage:
        async with api_call(self, "marking entry as read") as client:
            await client.mark_as_read(entry_id)

    Args:
        screen: The screen instance (for notifications and logging)
        operation_name: Name of operation for error messages

    Yields:
        The API client instance
    """
    if not hasattr(screen.app, "client") or not screen.app.client:
        screen.notify("API client not available", severity="error")
        return

    try:
        yield screen.app.client
    except TimeoutError:
        screen.notify(f"Request timeout during {operation_name}", severity="error")
        screen.log(f"Timeout during {operation_name}")
    except ConnectionError:
        screen.notify(f"Connection failed during {operation_name}", severity="error")
        screen.log(f"Connection error during {operation_name}")
    except ValueError as e:
        screen.notify(f"Invalid input during {operation_name}: {e}", severity="error")
        screen.log(f"ValueError during {operation_name}: {e}")
    except Exception as e:
        screen.log(f"Unexpected error during {operation_name}: {e}")
        screen.notify(f"Error during {operation_name}: {e}", severity="error")
