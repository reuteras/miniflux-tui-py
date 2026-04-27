# SPDX-License-Identifier: MIT
"""Security utilities for input validation and sanitization."""

import ipaddress
import re
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
    try:
        addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_multicast or addr.is_reserved or addr.is_unspecified:
            return True
        return any(addr in net for net in _ADDITIONAL_RESERVED_NETWORKS)
    except ValueError:
        # Not a valid IP literal — it is a hostname; DNS-based access is
        # controlled server-side by Miniflux itself.
        return False


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

    # Check for shell metacharacters and null bytes
    if _has_suspicious_patterns(url):
        return "URL contains suspicious characters"

    return None


def _has_suspicious_patterns(url: str) -> bool:
    """Check if URL contains suspicious patterns.

    Args:
        url: The URL to validate

    Returns:
        True if suspicious patterns found, False otherwise
    """
    suspicious_patterns = [
        r"[;|&$`<>]",  # Shell metacharacters
        r"%00",  # Null byte
    ]
    return any(re.search(pattern, url) for pattern in suspicious_patterns)


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
