# SPDX-License-Identifier: MIT
"""Data models for Miniflux API.

The server is semi-trusted: it is the user's own instance, but the records it
returns originate from arbitrary feeds. Parsing is therefore tolerant of
missing or oddly typed fields so that one bad record cannot abort loading the
whole list. Only the ``id`` fields are required.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

_EPOCH = datetime.fromtimestamp(0, tz=UTC)


def _as_str(value: Any, default: str = "") -> str:
    """Coerce an API value to ``str``, mapping ``None`` to ``default``."""
    if value is None:
        return default
    return value if isinstance(value, str) else str(value)


def _as_int(value: Any, default: int = 0) -> int:
    """Coerce an API value to ``int`` without raising on bad input."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_optional_int(value: Any) -> int | None:
    """Coerce an API value to ``int`` or ``None``."""
    if value is None:
        return None
    result = _as_int(value, default=-1)
    return None if result < 0 else result


def _as_bool(value: Any, default: bool = False) -> bool:
    """Coerce an API value to ``bool``."""
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return bool(value)


def _parse_datetime(value: Any) -> datetime:
    """Parse an ISO-8601 timestamp, falling back to the Unix epoch on bad input."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if not isinstance(value, str) or not value:
        return _EPOCH
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return _EPOCH
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


@dataclass
class Category:
    """Represents a Miniflux category."""

    id: int
    title: str

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        """Create a Category from API response data."""
        return cls(
            id=_as_int(data["id"]),
            title=_as_str(data.get("title")),
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
            id=_as_int(data["id"]),
            user_id=_as_int(data.get("user_id")),
            entry_id=_as_int(data.get("entry_id")),
            url=_as_str(data.get("url")),
            mime_type=_as_str(data.get("mime_type")),
            size=_as_int(data.get("size")),
            media_progression=_as_int(data.get("media_progression")),
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
    description: str = ""  # User-provided description or notes for the feed
    parsing_error_message: str = ""
    parsing_error_count: int = 0
    checked_at: str | None = None
    disabled: bool = False
    # Network settings
    username: str = ""
    password: str = ""
    user_agent: str = ""
    proxy_url: str = ""
    ignore_https_errors: bool = False
    # Rules & filtering (API uses blocklist_rules and keeplist_rules, not blocking_rules and keep_rules)
    scraper_rules: str = ""
    rewrite_rules: str = ""
    blocklist_rules: str = ""
    keeplist_rules: str = ""
    # Feed behavior options
    hide_globally: bool = False
    no_media_player: bool = False
    # Additional feed settings
    crawler: bool = False
    ignore_http_cache: bool = False
    fetch_via_proxy: bool = False
    check_interval: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Feed":
        """Create a Feed from API response data."""
        checked_at = data.get("checked_at")
        return cls(
            id=_as_int(data["id"]),
            title=_as_str(data.get("title")),
            site_url=_as_str(data.get("site_url")),
            feed_url=_as_str(data.get("feed_url")),
            category_id=_as_optional_int(data.get("category_id")),
            description=_as_str(data.get("description")),
            parsing_error_message=_as_str(data.get("parsing_error_message")),
            parsing_error_count=_as_int(data.get("parsing_error_count")),
            checked_at=_as_str(checked_at) if checked_at is not None else None,
            disabled=_as_bool(data.get("disabled")),
            username=_as_str(data.get("username")),
            password=_as_str(data.get("password")),
            user_agent=_as_str(data.get("user_agent")),
            proxy_url=_as_str(data.get("proxy_url")),
            ignore_https_errors=_as_bool(data.get("ignore_https_errors")),
            scraper_rules=_as_str(data.get("scraper_rules")),
            rewrite_rules=_as_str(data.get("rewrite_rules")),
            blocklist_rules=_as_str(data.get("blocklist_rules")),
            keeplist_rules=_as_str(data.get("keeplist_rules")),
            hide_globally=_as_bool(data.get("hide_globally")),
            no_media_player=_as_bool(data.get("no_media_player")),
            crawler=_as_bool(data.get("crawler")),
            ignore_http_cache=_as_bool(data.get("ignore_http_cache")),
            fetch_via_proxy=_as_bool(data.get("fetch_via_proxy")),
            check_interval=_as_optional_int(data.get("check_interval")),
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
        """Create an Entry from API response data.

        Raises:
            KeyError: If the entry or its feed has no ``id``
            TypeError: If ``feed`` or ``enclosures`` have the wrong shape
        """
        # Parse enclosures if present; skip malformed ones rather than fail the entry
        enclosures: list[Enclosure] | None = None
        raw_enclosures = data.get("enclosures")
        if isinstance(raw_enclosures, list) and raw_enclosures:
            enclosures = []
            for raw in raw_enclosures:
                if isinstance(raw, dict) and "id" in raw:
                    enclosures.append(Enclosure.from_dict(raw))

        feed_data = data.get("feed")
        feed_id = _as_int(data.get("feed_id"), default=-1)
        if not isinstance(feed_data, dict):
            if feed_id < 0:
                msg = "feed"
                raise KeyError(msg)
            feed_data = {"id": feed_id}
        feed = Feed.from_dict(feed_data)

        original_content = data.get("original_content")
        return cls(
            id=_as_int(data["id"]),
            feed_id=feed.id if feed_id < 0 else feed_id,
            title=_as_str(data.get("title")),
            url=_as_str(data.get("url")),
            content=_as_str(data.get("content")),
            feed=feed,
            status=_as_str(data.get("status"), default="unread"),
            starred=_as_bool(data.get("starred")),
            published_at=_parse_datetime(data.get("published_at")),
            original_content=_as_str(original_content) if original_content is not None else None,
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
