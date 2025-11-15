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
        with suppress(NoMatches, NoScreen):
            self.query_one(HeaderTitle).update(self.format_title())

    def _on_mount(self, _: Mount) -> None:
        """Called when the Header is mounted, with improved exception handling.

        This override calls the parent's _on_mount but wraps it in exception
        handling to catch NoMatches errors that occur on Windows when HeaderTitle
        isn't ready yet due to async timing differences.

        The parent's _on_mount creates async callbacks that may raise NoMatches
        before the child HeaderTitle widget is fully initialized. By catching
        these exceptions here, we allow the Header to continue functioning.
        """
        try:
            # Call parent's _on_mount to set up standard watchers and callbacks
            super()._on_mount(_)
        except NoMatches:
            # Suppress NoMatches that happen during initialization
            # This can occur on Windows Python 3.12 due to async timing
            pass
        except NoScreen:
            # Also suppress NoScreen errors that might occur during mount
            pass

        # Ensure initial title is set using our safe implementation
        # This will catch any remaining NoMatches/NoScreen errors
        with suppress(NoMatches, NoScreen):
            self.set_title()
