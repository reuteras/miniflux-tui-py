"""Miniflux API client wrapper using official miniflux package."""

import asyncio
from collections.abc import Callable
from functools import partial
from typing import TypeVar

from miniflux import Client as MinifluxClientBase

from miniflux_tui.constants import BACKOFF_FACTOR, MAX_RETRIES

from .models import Entry

T = TypeVar("T")


class MinifluxClient:
    """Wrapper around official Miniflux client for our app."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        allow_invalid_certs: bool = False,
        timeout: float = 30.0,
    ):
        """
        Initialize the Miniflux API client.

        Args:
            base_url: Base URL of the Miniflux server
            api_key: API key for authentication
            allow_invalid_certs: Whether to allow invalid SSL certificates (not supported by official client)
            timeout: Request timeout in seconds (not supported by official client)
        """
        self.base_url = base_url.rstrip("/")

        # Create official Miniflux client (synchronous)
        # The official client expects api_key as a keyword argument
        self.client = MinifluxClientBase(base_url, api_key=api_key)

        # Allow invalid certs
        self.allow_invalid_certs: bool = allow_invalid_certs

        # Timeout for network calls
        self.timeout: float = timeout

    async def close(self):
        """Close the HTTP client (no-op for official client)."""

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _run_sync(self, func, *args, **kwargs):
        """Run a synchronous function in an executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    async def _call_with_retry(
        self,
        func: Callable[..., T],
        *args,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = BACKOFF_FACTOR,
        **kwargs,
    ) -> T:
        """Call function with exponential backoff retry logic.

        Automatically retries on network errors (ConnectionError, TimeoutError)
        with exponential backoff. Other exceptions are raised immediately.

        Backoff calculation:
        - Attempt 0: Immediate retry
        - Attempt 1: Wait backoff_factor^1 = 1 second
        - Attempt 2: Wait backoff_factor^2 = 1 second (with factor=1.0)

        Example with backoff_factor=2.0:
        - Attempt 1: Wait 2 seconds
        - Attempt 2: Wait 4 seconds
        - Attempt 3: Wait 8 seconds

        Args:
            func: Synchronous function to call
            *args: Positional arguments for func
            max_retries: Maximum number of retry attempts (default 3)
            backoff_factor: Multiplier for exponential backoff (default 1.0)
            **kwargs: Keyword arguments for func

        Returns:
            Result from func call

        Raises:
            ConnectionError/TimeoutError: Last network error if all retries fail
            Exception: Other exceptions are raised immediately without retry
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Try the function call
                return await self._run_sync(func, *args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                # Transient network errors - retry with backoff
                last_exception = e
                if attempt < max_retries - 1:
                    # Calculate exponential backoff delay
                    wait_time = backoff_factor**attempt
                    await asyncio.sleep(wait_time)
            except Exception:
                # Non-network errors - don't retry, raise immediately
                raise

        # All retries exhausted - raise last exception
        raise last_exception or Exception("Unknown error in retry logic")

    async def get_unread_entries(self, limit: int = 100, offset: int = 0) -> list[Entry]:
        """
        Get unread feed entries with retry logic.

        Args:
            limit: Maximum number of entries to retrieve
            offset: Offset for pagination

        Returns:
            List of unread Entry objects
        """
        response = await self._call_with_retry(
            self.client.get_entries, status=["unread"], limit=limit, offset=offset, order="published_at", direction="desc"
        )

        return [Entry.from_dict(entry) for entry in response.get("entries", [])]

    async def get_starred_entries(self, limit: int = 100, offset: int = 0) -> list[Entry]:
        """
        Get starred feed entries with retry logic.

        Args:
            limit: Maximum number of entries to retrieve
            offset: Offset for pagination

        Returns:
            List of starred Entry objects
        """
        response = await self._call_with_retry(
            self.client.get_entries, starred=True, limit=limit, offset=offset, order="published_at", direction="desc"
        )

        return [Entry.from_dict(entry) for entry in response.get("entries", [])]

    async def change_entry_status(self, entry_id: int, status: str) -> None:
        """
        Change the read status of an entry.

        Args:
            entry_id: ID of the entry
            status: New status ("read" or "unread")
        """
        await self._run_sync(self.client.update_entries, entry_ids=[entry_id], status=status)

    async def mark_as_read(self, entry_id: int) -> None:
        """Mark an entry as read."""
        await self.change_entry_status(entry_id, "read")

    async def mark_as_unread(self, entry_id: int) -> None:
        """Mark an entry as unread."""
        await self.change_entry_status(entry_id, "unread")

    async def toggle_starred(self, entry_id: int) -> None:
        """
        Toggle the starred status of an entry.

        Args:
            entry_id: ID of the entry
        """
        await self._run_sync(self.client.toggle_bookmark, entry_id)

    async def save_entry(self, entry_id: int) -> None:
        """
        Save an entry to third-party service (e.g., Wallabag, Shiori, Shaarli).

        Args:
            entry_id: ID of the entry
        """
        await self._run_sync(self.client.save_entry, entry_id)

    async def mark_all_as_read(self, entry_ids: list[int]) -> None:
        """
        Mark multiple entries as read.

        Args:
            entry_ids: List of entry IDs to mark as read
        """
        await self._run_sync(self.client.update_entries, entry_ids=entry_ids, status="read")

    async def refresh_all_feeds(self) -> None:
        """Trigger a refresh of all feeds."""
        await self._run_sync(self.client.refresh_all_feeds)

    async def fetch_original_content(self, entry_id: int) -> str:
        """
        Fetch the original content of an entry.

        Args:
            entry_id: ID of the entry

        Returns:
            Original content HTML
        """
        response = await self._run_sync(self.client.fetch_entry_content, entry_id)
        return response.get("content", "")
