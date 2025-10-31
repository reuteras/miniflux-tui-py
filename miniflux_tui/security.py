"""Security utilities for input validation and sanitization."""

import re
from urllib.parse import urlparse


def validate_feed_url(url: str) -> tuple[bool, str]:  # noqa: PLR0911, PLR0912
    """Validate and sanitize feed URL for SSRF prevention.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Length check
    if len(url) > 2048:
        return False, "URL too long (max 2048 characters)"

    # Empty check
    if not url.strip():
        return False, "URL cannot be empty"

    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"  # pragma: no cover

    # Protocol whitelist - only HTTP and HTTPS allowed
    if parsed.scheme not in ["http", "https"]:
        return False, "Only HTTP and HTTPS URLs are allowed"

    # Hostname validation
    if not parsed.netloc:
        return False, "URL must have a valid hostname"

    # Extract hostname without port
    hostname = parsed.netloc.split(":")[0].lower()

    # Block localhost/loopback addresses
    if hostname in ["localhost", "127.0.0.1", "::1", "[::1]"]:
        return False, "Cannot add local URLs (localhost)"

    # Block private IP ranges
    private_patterns = [
        r"^192\.168\.",
        r"^10\.",
        r"^172\.(1[6-9]|2[0-9]|3[01])\.",  # 172.16.0.0 - 172.31.255.255
        r"^127\.",  # Loopback
        r"^169\.254\.",  # Link-local
    ]

    for pattern in private_patterns:
        if re.match(pattern, hostname):
            return False, "Cannot add private network URLs"

    # Block IPv6 loopback and link-local
    if hostname.startswith(("fe80:", "[fe80:")):
        return False, "Cannot add link-local IPv6 addresses"

    # Check for control characters or suspicious patterns
    if any(ord(c) < 32 for c in url):
        return False, "URL contains invalid control characters"

    # Check for multiple newlines (header injection attempt)
    if "\n" in url or "\r" in url:
        return False, "URL contains invalid characters (newlines)"

    # Check for suspicious patterns
    suspicious_patterns = [
        r"[;|&$`<>]",  # Shell metacharacters
        r"%00",  # Null byte
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, url):
            return False, "URL contains suspicious characters"

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
