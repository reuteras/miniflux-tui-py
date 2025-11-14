# SPDX-License-Identifier: MIT
"""Rules helper screen for displaying Miniflux rule documentation."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from miniflux_tui.docs_fetcher import DocsFetcher

if TYPE_CHECKING:
    from miniflux_tui.docs_cache import DocsCache


class RulesHelperScreen(Screen):
    """Screen for displaying Miniflux rule documentation.

    Shows contextual help for rule configuration fields including:
    - Scraper rules
    - Rewrite rules
    - URL rewrite rules
    - Blocking rules
    - Keep rules

    Attributes:
        rule_type: The type of rule being documented
        docs_cache: Optional session-wide documentation cache
        content: The documentation content to display
    """

    BINDINGS: ClassVar = [
        Binding("escape", "close_helper", "Close", show=True),
    ]

    DEFAULT_CSS: ClassVar[str] = """
    RulesHelperScreen {
        background: $surface;
        color: $text;
    }

    RulesHelperScreen > Header {
        dock: top;
    }

    RulesHelperScreen > Footer {
        dock: bottom;
    }

    #helper-container {
        height: 1fr;
        width: 100%;
    }

    #helper-header {
        width: 100%;
        height: auto;
        padding: 1 2;
        background: $boost;
        border-bottom: solid $primary;
        content-align: left middle;
    }

    #helper-content {
        width: 100%;
        height: 1fr;
        padding: 1 2;
    }

    #helper-content Static {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    #status-message {
        width: 100%;
        height: auto;
        padding: 1 2;
        color: $text-muted;
    }
    """

    def __init__(
        self,
        rule_type: str,
        docs_cache: DocsCache | None = None,
        **kwargs,
    ):
        """Initialize the rules helper screen.

        Args:
            rule_type: Type of rule (scraper_rules, rewrite_rules, etc.)
            docs_cache: Optional session-wide documentation cache
            **kwargs: Additional keyword arguments for Screen
        """
        super().__init__(**kwargs)
        self.rule_type = rule_type
        self.docs_cache = docs_cache
        self.content = ""
        self.fetcher = DocsFetcher()

    def compose(self) -> ComposeResult:
        """Compose the rules helper screen layout.

        Yields:
            Composed widgets for the screen
        """
        yield Header()

        with Container(id="helper-container"):
            yield Static(
                f"Help: {self._get_rule_title()}",
                id="helper-header",
            )

            with VerticalScroll(id="helper-content"):
                yield Static(
                    "Loading documentation...",
                    id="help-text",
                )

        yield Static("", id="status-message")
        yield Footer()

    async def on_mount(self) -> None:
        """Called when screen is mounted.

        Fetch documentation for the rule type.
        """
        try:
            # Try to get from cache first
            if self.docs_cache:
                self.content = await self.docs_cache.get_documentation(self.rule_type)
            else:
                # Fetch directly if no cache
                self.content = await self.fetcher.fetch_snippet(self.rule_type)

            # Update the display
            help_text = self.query_one("#help-text", expect_type=Static)
            help_text.update(self.content)

        except ValueError as e:
            self._show_error(f"Invalid rule type: {e}")
        except TimeoutError:
            self._show_error("Request timeout while fetching documentation")
        except ConnectionError:
            self._show_error("Connection failed while fetching documentation")
        except Exception as e:
            self._show_error(f"Error fetching documentation: {e}")

    def _get_rule_title(self) -> str:
        """Get human-readable title for rule type.

        Returns:
            Formatted rule type title
        """
        titles = {
            "scraper_rules": "Scraper Rules",
            "rewrite_rules": "Rewrite Rules",
            "url_rewrite_rules": "URL Rewrite Rules",
            "blocking_rules": "Blocking Rules",
            "keep_rules": "Keep Rules",
        }
        return titles.get(self.rule_type, self.rule_type)

    async def action_close_helper(self) -> None:
        """Close the helper screen."""
        self.app.pop_screen()

    def _show_error(self, message: str) -> None:
        """Display error message and update content.

        Args:
            message: Error message to display
        """
        help_text = self.query_one("#help-text", expect_type=Static)
        help_text.update(f"Error: {message}")

        status_widget = self.query_one("#status-message", expect_type=Static)
        status_widget.update(message)
        status_widget.styles.color = "red"
