"""Miniflux API client."""

import httpx
from typing import List, Optional

from .models import Entry


class MinifluxClient:
    """Async client for interacting with Miniflux API."""

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
            allow_invalid_certs: Whether to allow invalid SSL certificates
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Set up headers with API key
        headers = {"X-Auth-Token": api_key}

        # Create async HTTP client
        self.client = httpx.AsyncClient(
            headers=headers,
            verify=not allow_invalid_certs,
            timeout=timeout,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

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
        url = f"{self.base_url}/v1/entries"
        params = {
            "status": "unread",
            "order": "published_at",
            "direction": "desc",
            "limit": limit,
            "offset": offset,
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return [Entry.from_dict(entry) for entry in data.get("entries", [])]

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
        url = f"{self.base_url}/v1/entries"
        params = {
            "starred": "true",
            "order": "published_at",
            "direction": "desc",
            "limit": limit,
            "offset": offset,
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return [Entry.from_dict(entry) for entry in data.get("entries", [])]

    async def change_entry_status(
        self, entry_id: int, status: str
    ) -> None:
        """
        Change the read status of an entry.

        Args:
            entry_id: ID of the entry
            status: New status ("read" or "unread")
        """
        url = f"{self.base_url}/v1/entries"
        payload = {"status": status, "entry_ids": [entry_id]}

        response = await self.client.put(url, json=payload)
        response.raise_for_status()

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
        url = f"{self.base_url}/v1/entries/{entry_id}/bookmark"

        response = await self.client.put(url)
        response.raise_for_status()

    async def save_entry(self, entry_id: int) -> None:
        """
        Save an entry for later.

        Args:
            entry_id: ID of the entry
        """
        url = f"{self.base_url}/v1/entries/{entry_id}/save"

        response = await self.client.post(url)
        response.raise_for_status()

    async def mark_all_as_read(self, entry_ids: List[int]) -> None:
        """
        Mark multiple entries as read.

        Args:
            entry_ids: List of entry IDs to mark as read
        """
        url = f"{self.base_url}/v1/entries"
        payload = {"status": "read", "entry_ids": entry_ids}

        response = await self.client.put(url, json=payload)
        response.raise_for_status()

    async def refresh_all_feeds(self) -> None:
        """Trigger a refresh of all feeds."""
        url = f"{self.base_url}/v1/feeds/refresh"

        response = await self.client.put(url)
        response.raise_for_status()

    async def fetch_original_content(self, entry_id: int) -> str:
        """
        Fetch the original content of an entry.

        Args:
            entry_id: ID of the entry

        Returns:
            Original content HTML
        """
        url = f"{self.base_url}/v1/entries/{entry_id}/fetch-content"

        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()

        return data.get("content", "")
