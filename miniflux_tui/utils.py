# SPDX-License-Identifier: MIT
"""Utility functions and helpers for miniflux-tui."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from importlib import metadata
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

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


def extract_images_from_html(html_content: str, base_url: str | None = None) -> list[str]:
    """Extract image URLs from HTML content.

    Args:
        html_content: HTML content to parse
        base_url: Base URL for resolving relative image paths

    Returns:
        List of absolute image URLs found in the HTML
    """
    if not html_content:
        return []

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        image_urls = []

        # Find all img tags
        for img in soup.find_all("img"):
            src = img.get("src")
            # Ensure src is a string (BeautifulSoup can return various types)
            if src and isinstance(src, str):
                # Resolve relative URLs if base_url is provided
                if base_url and not bool(urlparse(src).netloc):
                    src = urljoin(base_url, src)
                image_urls.append(src)

        return image_urls
    except Exception:
        return []


def extract_images_from_markdown(markdown_content: str) -> list[str]:
    """Extract image URLs from Markdown content.

    Args:
        markdown_content: Markdown content to parse

    Returns:
        List of image URLs found in the markdown
    """
    if not markdown_content:
        return []

    # Match markdown image syntax: ![alt](url)
    pattern = r"!\[.*?\]\((.*?)\)"
    matches = re.findall(pattern, markdown_content)
    return [url for url in matches if url]


def is_valid_image_url(url: str) -> bool:
    """Check if URL appears to be a valid image URL.

    Args:
        url: URL to validate

    Returns:
        True if URL looks like a valid image URL
    """
    if not url:
        return False

    parsed = urlparse(url.strip())

    # Must have http/https scheme
    if parsed.scheme not in {"http", "https"}:
        return False

    # Must have a hostname - some URLs don't have extensions but are still images (e.g., CDN URLs)
    return bool(parsed.netloc)
