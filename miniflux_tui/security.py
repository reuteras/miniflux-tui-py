# SPDX-License-Identifier: MIT
"""Security utilities for input validation and sanitization."""

import ipaddress
import re
import socket
from urllib.parse import urlparse


def _check_url_basic_validity(url: str) -> str | None:
    """Check URL length and emptiness.

    Args:
        url: The URL to validate

    Returns:
        Error message if invalid, None if valid
    """
    if len(url) > 2048:
        return "URL too long (max 2048 characters)"
    if not url.strip():
        return "URL cannot be empty"
    return None


def _check_url_scheme(parsed) -> str | None:
    """Check that URL uses allowed scheme (HTTP/HTTPS).

    Args:
        parsed: Parsed URL from urlparse

    Returns:
        Error message if invalid, None if valid
    """
    if parsed.scheme not in ["http", "https"]:
        return "Only HTTP and HTTPS URLs are allowed"
    if not parsed.netloc:
        return "URL must have a valid hostname"
    return None


def _check_url_hostname(parsed) -> str | None:
    """Check that hostname is not local or private.

    Args:
        parsed: Parsed URL from urlparse

    Returns:
        Error message if invalid, None if valid
    """
    # Use parsed.hostname which correctly strips IPv6 brackets and lowercases.
    # parsed.netloc.split(":") is wrong for IPv6 (e.g. "[fd00::1]" → "[fd00").
    hostname = parsed.hostname or ""

    # Block localhost by name
    if hostname == "localhost":
        return "Cannot add local URLs (localhost)"

    # Block all private/reserved IP addresses (covers loopback, ULA, link-local,
    # multicast, carrier-grade NAT, etc.) using the stdlib ipaddress module.
    if _is_private_ip(hostname):
        return "Cannot add private network URLs"

    return None


# RFC 6598 Shared Address Space (100.64.0.0/10) is used for carrier-grade NAT
# and is not classified by Python's ipaddress as is_private / is_reserved in
# Python 3.13. Check it explicitly.
_ADDITIONAL_RESERVED_NETWORKS: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] = (ipaddress.IPv4Network("100.64.0.0/10"),)


def _is_private_ip(hostname: str) -> bool:
    """Check if hostname is a private or reserved IP address.

    Uses the stdlib ipaddress module instead of regex patterns so that
    IPv4-mapped IPv6, ULA (fd00::/8), multicast, carrier-grade NAT, and
    other reserved ranges are all covered correctly.

    Args:
        hostname: The hostname/IP to check (IPv6 brackets already stripped
            by urlparse.hostname)

    Returns:
        True if hostname is a private/reserved IP, False otherwise
    """
    addr = _parse_ip_literal(hostname)
    if addr is None:
        # Not an IP literal — it is a hostname. Callers that fetch from this
        # machine resolve it via hostname_resolves_to_private().
        return False
    if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_multicast or addr.is_reserved or addr.is_unspecified:
        return True
    return any(addr in net for net in _ADDITIONAL_RESERVED_NETWORKS)


_LEGACY_IPV4_RE = re.compile(r"[0-9a-fA-Fx.]+")


def _parse_ip_literal(hostname: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """Parse an IP literal, including legacy IPv4 spellings resolvers accept.

    ``ipaddress`` only understands dotted-quad IPv4, but resolvers treat
    ``2130706433``, ``0x7f000001``, ``127.1`` and ``0177.0.0.1`` as
    127.0.0.1 via ``inet_aton``. Parse those too so they cannot bypass the
    private-range check.
    """
    try:
        return ipaddress.ip_address(hostname)
    except ValueError:
        pass
    if hostname and _LEGACY_IPV4_RE.fullmatch(hostname):
        try:
            return ipaddress.IPv4Address(socket.inet_aton(hostname))
        except OSError:
            return None
    return None


def _check_url_suspicious_content(url: str) -> str | None:
    """Check for control characters and suspicious patterns.

    Args:
        url: The URL to validate

    Returns:
        Error message if invalid, None if valid
    """
    # Check for control characters
    if any(ord(c) < 32 for c in url):
        return "URL contains invalid control characters"

    # Check for newlines (header injection)
    if "\n" in url or "\r" in url:
        return "URL contains invalid characters (newlines)"

    # Check for characters that are never valid in a URL and null bytes
    if _has_suspicious_patterns(url):
        return "URL contains suspicious characters"

    return None


def _has_suspicious_patterns(url: str) -> bool:
    """Check if URL contains suspicious patterns.

    URLs are sent to the Miniflux API as JSON and never reach a shell, so
    legitimate query-string characters such as ``&``, ``;`` and ``$`` are
    allowed. Angle brackets, backticks, whitespace and encoded null bytes are
    never valid in a URL and indicate injected text.

    Args:
        url: The URL to validate

    Returns:
        True if suspicious patterns found, False otherwise
    """
    suspicious_patterns = [
        r"[`<>\s]",
        r"%00",  # Null byte
    ]
    return any(re.search(pattern, url) for pattern in suspicious_patterns)


def hostname_resolves_to_private(url: str) -> bool:
    """Return True if the URL's host resolves to any private or reserved address.

    Used for fetches performed from the user's machine, where a public-looking
    hostname may point at loopback, link-local or LAN addresses (DNS rebinding,
    ``*.localtest.me`` style names, split-horizon DNS). Resolution failures are
    treated as unsafe.

    Args:
        url: The URL whose host should be resolved

    Returns:
        True if unsafe (private, reserved or unresolvable), False if all
        resolved addresses are public
    """
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return True
    if _is_private_ip(hostname):
        return True
    try:
        infos = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80), proto=socket.IPPROTO_TCP)
    except (socket.gaierror, UnicodeError, OSError):
        return True
    if not infos:
        return True
    return any(_is_private_ip(str(info[4][0])) for info in infos)


def validate_feed_url(url: str) -> tuple[bool, str]:
    """Validate and sanitize feed URL for SSRF prevention.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Basic validation
    error = _check_url_basic_validity(url)
    if error:
        return False, error

    # Parse URL (urlparse doesn't raise exceptions, just returns parsed components)
    parsed = urlparse(url)

    # Protocol validation
    error = _check_url_scheme(parsed)
    if error:
        return False, error

    # Hostname validation
    error = _check_url_hostname(parsed)
    if error:
        return False, error

    # Suspicious content validation
    error = _check_url_suspicious_content(url)
    if error:
        return False, error

    return True, ""


def sanitize_error_message(error: Exception, operation: str) -> str:
    """Sanitize error messages before displaying to user.

    Prevents information disclosure by mapping exception types to generic messages.

    Args:
        error: The caught exception
        operation: Description of what was being done (e.g., "adding feed")

    Returns:
        Safe error message for display to user
    """
    error_type = type(error).__name__

    # Map specific exception types to safe messages
    safe_messages = {
        "ValueError": f"Invalid input for {operation}",
        "TimeoutError": f"Request timed out during {operation}",
        "ConnectionError": f"Network error during {operation}",
        "PermissionError": f"Permission denied for {operation}",
        "OSError": f"System error during {operation}",
        "RuntimeError": f"Unable to complete {operation}",
    }

    # Return mapped message or generic fallback
    return safe_messages.get(error_type, f"Failed to complete {operation}")
