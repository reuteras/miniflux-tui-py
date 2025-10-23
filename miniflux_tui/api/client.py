"""Miniflux API client wrapper using official miniflux package."""

import asyncio
from functools import partial
from miniflux import Client as MinifluxClientBase
from typing import List

from .models import Entry


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

    async def close(self):
        """Close the HTTP client (no-op for official client)."""
        pass

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

    async def get_unread_entries(
        self, limit: int = 100, offset: int = 0
    ) -> List[Entry]:
        """
        Get unread feed entries.

        Args:
            limit: Maximum number of entries to retrieve
            offset: Offset for pagination

        Returns:
            List of unread Entry objects
        """
        # Use official client's get_entries method
        response = await self._run_sync(
            self.client.get_entries,
            status=["unread"],
            limit=limit,
            offset=offset,
            order="published_at",
            direction="desc"
        )

        return [Entry.from_dict(entry) for entry in response.get("entries", [])]

    async def get_starred_entries(
        self, limit: int = 100, offset: int = 0
    ) -> List[Entry]:
        """
        Get starred feed entries.

        Args:
            limit: Maximum number of entries to retrieve
            offset: Offset for pagination

        Returns:
            List of starred Entry objects
        """
        response = await self._run_sync(
            self.client.get_entries,
            starred=True,
            limit=limit,
            offset=offset,
            order="published_at",
            direction="desc"
        )

        return [Entry.from_dict(entry) for entry in response.get("entries", [])]

    async def change_entry_status(
        self, entry_id: int, status: str
    ) -> None:
        """
        Change the read status of an entry.

        Args:
            entry_id: ID of the entry
            status: New status ("read" or "unread")
        """
        await self._run_sync(
            self.client.update_entries,
            entry_ids=[entry_id],
            status=status
        )

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
        await self._run_sync(
            self.client.toggle_bookmark,
            entry_id
        )

    async def save_entry(self, entry_id: int) -> None:
        """
        Save an entry for later.

        Args:
            entry_id: ID of the entry
        """
        # Note: The official client doesn't have a direct save_entry method
        # We'll use toggle_bookmark as a workaround
        await self._run_sync(
            self.client.toggle_bookmark,
            entry_id
        )

    async def mark_all_as_read(self, entry_ids: List[int]) -> None:
        """
        Mark multiple entries as read.

        Args:
            entry_ids: List of entry IDs to mark as read
        """
        await self._run_sync(
            self.client.update_entries,
            entry_ids=entry_ids,
            status="read"
        )

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
        response = await self._run_sync(
            self.client.fetch_entry_content,
            entry_id
        )
        return response.get("content", "")
