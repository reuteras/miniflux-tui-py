# SPDX-License-Identifier: MIT
"""Safe Textual widgets with improved platform compatibility.

These widgets wrap or extend Textual's built-in widgets to handle
platform-specific issues (e.g., Windows widget lifecycle timing issues).
"""

from contextlib import suppress

from textual.css.query import NoMatches
from textual.widgets._header import Header, HeaderTitle


class SafeHeader(Header):
    """Header widget with Windows-compatible widget lifecycle handling.

    Textual's Header widget on Windows sometimes fails to query HeaderTitle
    during _on_mount due to async timing differences between platforms.
    This subclass catches those exceptions gracefully, allowing the Header
    to function correctly on all platforms.

    The HeaderTitle widget's text may not be updated immediately on Windows,
    but the Header will continue to function without raising exceptions.
    """

    def _on_mount(self, _):
        """Called when the Header is mounted, with exception handling."""

        async def set_title() -> None:
            """Set the title with NoMatches exception handling."""
            with suppress(NoMatches):
                self.query_one(HeaderTitle).update(self.format_title())

        self.app.call_later(set_title)
