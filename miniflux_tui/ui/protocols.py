"""Type protocols shared across UI components."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class EntryApiClientProtocol(Protocol):
    """Subset of Miniflux API client operations used by UI screens."""

    async def mark_as_read(self, entry_id: int) -> None: ...

    async def mark_as_unread(self, entry_id: int) -> None: ...

    async def toggle_starred(self, entry_id: int) -> None: ...

    async def save_entry(self, entry_id: int) -> None: ...

    async def fetch_original_content(self, entry_id: int) -> str: ...


@runtime_checkable
class EntryReaderAppProtocol(Protocol):
    """Capabilities required from the TUI application by entry reader screens."""

    client: EntryApiClientProtocol | None

    def pop_screen(self) -> None: ...

    def push_screen(self, screen: str) -> None: ...

    def exit(self) -> None: ...
