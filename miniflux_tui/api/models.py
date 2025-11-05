# SPDX-License-Identifier: MIT
"""Data models for Miniflux API."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Category:
    """Represents a Miniflux category."""

    id: int
    title: str

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        """Create a Category from API response data."""
        return cls(
            id=data["id"],
            title=data["title"],
        )


@dataclass
class Enclosure:
    """Represents a media enclosure (image, audio, video) attached to an entry."""

    id: int
    user_id: int
    entry_id: int
    url: str
    mime_type: str
    size: int
    media_progression: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Enclosure":
        """Create an Enclosure from API response data."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            entry_id=data["entry_id"],
            url=data["url"],
            mime_type=data["mime_type"],
            size=data["size"],
            media_progression=data.get("media_progression", 0),
        )

    @property
    def is_image(self) -> bool:
        """Check if this enclosure is an image."""
        return self.mime_type.startswith("image/")


@dataclass
class Feed:
    """Represents a Miniflux feed."""

    id: int
    title: str
    site_url: str
    feed_url: str
    category_id: int | None = None
    parsing_error_message: str = ""
    parsing_error_count: int = 0
    checked_at: str | None = None
    disabled: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "Feed":
        """Create a Feed from API response data."""
        return cls(
            id=data["id"],
            title=data["title"],
            site_url=data["site_url"],
            feed_url=data["feed_url"],
            category_id=data.get("category_id"),
            parsing_error_message=data.get("parsing_error_message", ""),
            parsing_error_count=data.get("parsing_error_count", 0),
            checked_at=data.get("checked_at"),
            disabled=data.get("disabled", False),
        )

    @property
    def has_errors(self) -> bool:
        """Check if feed has parsing errors."""
        return bool(self.parsing_error_message or self.parsing_error_count > 0)


@dataclass
class Entry:
    """Represents a Miniflux feed entry."""

    id: int
    feed_id: int
    title: str
    url: str
    content: str
    feed: Feed
    status: str  # "read" or "unread"
    starred: bool
    published_at: datetime
    original_content: str | None = None
    enclosures: list[Enclosure] | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Entry":
        """Create an Entry from API response data."""
        # Parse enclosures if present
        enclosures = None
        if data.get("enclosures"):
            enclosures = [Enclosure.from_dict(enc) for enc in data["enclosures"]]

        return cls(
            id=data["id"],
            feed_id=data["feed_id"],
            title=data["title"],
            url=data["url"],
            content=data["content"],
            feed=Feed.from_dict(data["feed"]),
            status=data["status"],
            starred=data["starred"],
            published_at=datetime.fromisoformat(data["published_at"].replace("Z", "+00:00")),
            original_content=data.get("original_content"),
            enclosures=enclosures,
        )

    @property
    def is_read(self) -> bool:
        """Check if entry is marked as read."""
        return self.status == "read"

    @property
    def is_unread(self) -> bool:
        """Check if entry is marked as unread."""
        return self.status == "unread"

    @property
    def image_enclosures(self) -> list[Enclosure]:
        """Get all image enclosures for this entry."""
        if not self.enclosures:
            return []
        return [enc for enc in self.enclosures if enc.is_image]
