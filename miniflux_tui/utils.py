"""Utility functions and helpers for miniflux-tui."""

from __future__ import annotations

import tomllib
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from importlib import metadata
from pathlib import Path
from typing import Any

PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


def get_app_version() -> str:
    """Return the application version.

    The preferred source for the version is the installed package metadata. This
    works both for editable installs and when the project is installed from a
    wheel. When the metadata isn't available (for example when running the
    source tree directly without installing), the function falls back to reading
    the version from ``pyproject.toml``.

    Returns:
        Version string if it can be determined, otherwise ``"unknown"``.
    """

    last_metadata_error: Exception | None = None

    for distribution_name in _iter_distribution_candidates():
        try:
            return metadata.version(distribution_name)
        except metadata.PackageNotFoundError:
            pass
        except Exception as error:
            # Unexpected metadata errors should not crash the application. Try
            # any remaining candidates before falling back to the file-based
            # lookup instead.
            last_metadata_error = error

    if last_metadata_error is not None:
        return _get_version_from_pyproject()

    return _get_version_from_pyproject()


def _get_version_from_pyproject() -> str:
    """Read the version from ``pyproject.toml`` if it is available."""

    try:
        if PYPROJECT_PATH.exists():
            data = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
            version = data.get("project", {}).get("version")
            if version:
                return str(version)
    except (OSError, tomllib.TOMLDecodeError, AttributeError):
        return "unknown"

    return "unknown"


def _iter_distribution_candidates() -> Iterator[str]:
    """Yield potential distribution names that provide :mod:`miniflux_tui`.

    The canonical distribution name is ``miniflux-tui-py``. When the package is
    installed in editable mode the metadata lookup can, however, vary between
    environments. To make the lookup resilient we ask ``importlib.metadata`` for
    the distributions that provide ``miniflux_tui`` and try those as well.
    """

    seen: set[str] = set()

    def _unique(name: str) -> Iterator[str]:
        if name and name not in seen:
            seen.add(name)
            yield name

    yield from _unique("miniflux-tui-py")

    try:
        packages = metadata.packages_distributions()
    except Exception:
        return

    for candidate in packages.get("miniflux_tui", []) or []:
        yield from _unique(candidate)


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


@contextmanager
def api_call(screen: Any, operation_name: str = "Operation") -> Generator[Any, None, None]:
    """Context manager for safe API calls with error handling.

    Usage:
        with api_call(self, "marking entry as read") as client:
            if client is None:
                return
            await client.mark_as_read(entry_id)

    Args:
        screen: The screen instance (for notifications and logging)
        operation_name: Name of operation for error messages

    Yields:
        The API client instance
    """
    client = getattr(screen.app, "client", None)
    if not client:
        screen.notify("API client not available", severity="error")
        yield None
        return

    try:
        yield client
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
