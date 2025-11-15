# SPDX-License-Identifier: MIT
"""Safe Textual widgets with improved platform compatibility.

These widgets wrap or extend Textual's built-in widgets to handle
platform-specific issues (e.g., Windows widget lifecycle timing issues).
"""

from contextlib import suppress

from textual.css.query import NoMatches
from textual.dom import NoScreen
from textual.events import Mount
from textual.widgets._header import Header, HeaderTitle


class SafeHeader(Header):
    """Header widget with Windows-compatible widget lifecycle handling.

    Textual's Header widget on Windows sometimes fails to query HeaderTitle
    during _on_mount and set_title due to async timing differences between
    platforms. The default Header only catches NoScreen but not NoMatches.

    This subclass overrides set_title to catch both NoScreen AND NoMatches,
    allowing the Header to function correctly on all platforms.

    The HeaderTitle widget's text may not be updated immediately on Windows,
    but the Header will continue to function without raising exceptions.
    """

    def set_title(self) -> None:
        """Set header title with Windows-compatible exception handling.

        Overrides the base Header.set_title to catch NoMatches exceptions
        that occur on Windows when HeaderTitle isn't ready yet.
        """
        # Suppress both NoMatches (Windows timing) and NoScreen (context issues)
        # This handles the case where the parent's async watchers fire before
        # HeaderTitle is fully initialized, particularly on Windows Python 3.12
        with suppress(NoMatches, NoScreen):
            self.query_one(HeaderTitle).update(self.format_title())

    def _on_mount(self, _: Mount) -> None:
        """Called when the Header is mounted, with improved exception handling.

        The parent Header's _on_mount sets up async watchers that can raise
        NoMatches exceptions before HeaderTitle is ready on Windows. We call
        the parent's _on_mount but suppress all exceptions, since our safe
        set_title method handles the actual title updates.
        """
        # Call parent's _on_mount which sets up watchers
        # These may raise exceptions on Windows Python 3.12 before
        # HeaderTitle is initialized, but we suppress them since
        # our set_title() override handles exceptions safely
        with suppress(Exception):
            super()._on_mount(_)

        # Ensure title is set safely after parent setup
        # Use call_later to defer to next event loop iteration
        self.call_later(self.set_title)
