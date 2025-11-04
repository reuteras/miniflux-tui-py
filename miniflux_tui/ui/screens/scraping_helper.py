"""Scraping rule helper screen for discovering optimal content extraction rules."""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Static

from miniflux_tui.scraping import ContentAnalyzer, SecureFetcher


class ScrapingHelperScreen(Screen):
    """Interactive tool to find and test scraping rules for feed content."""

    BINDINGS = [  # noqa: RUF012
        Binding("escape", "dismiss", "Back", show=True),
        Binding("ctrl+s", "save_rule", "Save Rule", show=True),
        Binding("t", "test_custom", "Test Custom", show=False),
    ]

    CSS = """  # noqa: RUF012
    ScrapingHelperScreen {
        align: center middle;
    }

    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    #url-display {
        margin-bottom: 1;
        color: $accent;
    }

    #status-message {
        height: 3;
        margin-bottom: 1;
        border: solid $primary;
        padding: 1;
    }

    #candidates-container {
        height: 40%;
        border: solid $primary;
        margin-bottom: 1;
    }

    #candidates-title {
        dock: top;
        background: $primary;
        color: $text;
        padding: 0 1;
    }

    #candidates-list {
        height: 1fr;
    }

    #preview-container {
        height: 50%;
        border: solid $secondary;
    }

    #preview-title {
        dock: top;
        background: $secondary;
        color: $text;
        padding: 0 1;
    }

    #preview-scroll {
        height: 1fr;
    }

    #preview-content {
        padding: 1;
    }

    #custom-selector-container {
        margin-bottom: 1;
    }

    .selector-item {
        padding: 0 1;
    }

    .selector-item:hover {
        background: $accent 20%;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(
        self,
        entry_url: str,
        feed_id: int,
        feed_title: str,
        on_save_callback=None,
    ):
        """Initialize scraping helper screen.

        Args:
            entry_url: URL of the entry to analyze
            feed_id: ID of the feed to update
            feed_title: Title of the feed for display
            on_save_callback: Optional callback when rule is saved
        """
        super().__init__()
        self.entry_url = entry_url
        self.feed_id = feed_id
        self.feed_title = feed_title
        self.on_save_callback = on_save_callback
        self.candidates = []
        self.selected_selector = None
        self.analyzer = None
        self.fetcher = None

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()

        with Container(id="main-container"):
            yield Label(f"Feed: {self.feed_title}", id="feed-display")
            yield Label(f"URL: {self.entry_url}", id="url-display")
            yield Static("", id="status-message")

            with Vertical(id="custom-selector-container"):
                yield Label("Custom Selector (optional):")
                with Horizontal():
                    yield Input(
                        placeholder="e.g., article.content, #main, .post",
                        id="custom-selector-input",
                    )
                    yield Button("Test", id="test-custom-btn", variant="primary")

            with Container(id="candidates-container"):
                yield Label("📋 Suggested Selectors", id="candidates-title")
                yield ListView(id="candidates-list")

            with Container(id="preview-container"):
                yield Label("👁 Preview", id="preview-title")
                with VerticalScroll(id="preview-scroll"):
                    yield Static("", id="preview-content")

        yield Footer()

    async def on_mount(self) -> None:
        """Fetch and analyze page when screen loads."""
        await self._fetch_and_analyze()

    async def _fetch_and_analyze(self) -> None:
        """Fetch URL content and analyze for scraping rules."""
        status = self.query_one("#status-message", Static)
        status.update("🔍 Fetching page...")

        try:
            # Create fetcher and fetch content
            self.fetcher = SecureFetcher()
            html = await self.fetcher.fetch(self.entry_url)

            status.update("🔍 Analyzing content...")

            # Analyze HTML
            self.analyzer = ContentAnalyzer(html)
            self.candidates = self.analyzer.find_main_content()

            # Populate candidate list
            candidates_list = self.query_one("#candidates-list", ListView)
            candidates_list.clear()

            if not self.candidates:
                status.update("⚠️  No content candidates found")
                return

            for i, candidate in enumerate(self.candidates, 1):
                score = candidate["score"]
                selector = candidate["selector"]
                elem_count = candidate.get("element_count", 1)
                count_str = f" ({elem_count}x)" if elem_count > 1 else ""

                item = ListItem(
                    Label(f"{i}. ⭐{score:3d} - {selector}{count_str}"),
                    classes="selector-item",
                )
                item.data = candidate  # Store candidate data
                candidates_list.append(item)

            # Auto-select first (best) candidate
            if self.candidates:
                candidates_list.index = 0
                await self._preview_candidate(self.candidates[0])

            status.update(f"✅ Analysis complete - Found {len(self.candidates)} candidates")

        except ValueError as e:
            status.update(f"❌ Invalid URL: {e}")
        except TimeoutError as e:
            status.update(f"⏱️  Timeout: {e}")
        except RuntimeError as e:
            status.update(f"❌ Fetch error: {e}")
        except Exception as e:
            status.update(f"❌ Unexpected error: {e}")

    @on(ListView.Selected, "#candidates-list")
    async def on_candidate_selected(self, event: ListView.Selected) -> None:
        """Handle candidate selection from list."""
        if event.item and hasattr(event.item, "data"):
            await self._preview_candidate(event.item.data)

    async def _preview_candidate(self, candidate: dict) -> None:
        """Preview selected candidate's extracted content.

        Args:
            candidate: Candidate dictionary with selector info
        """
        if not self.analyzer:
            return

        self.selected_selector = candidate["selector"]

        # Extract content with selector
        extracted_html = self.analyzer.extract_with_selector(self.selected_selector)

        # Get element stats
        stats = self.analyzer.get_element_stats(self.selected_selector)

        # Update preview
        preview = self.query_one("#preview-content", Static)

        if not extracted_html:
            preview.update("⚠️  No content matched this selector")
            return

        # Show stats header
        stats_text = (
            f"📊 Stats: {stats['count']} elements, {stats['paragraphs']} paragraphs, {stats['links']} links, {stats['images']} images\n\n"
        )

        # Truncate for preview (first 2000 chars)
        preview_text = extracted_html[:2000]
        if len(extracted_html) > 2000:
            preview_text += "\n\n... (truncated)"

        preview.update(stats_text + preview_text)

    @on(Button.Pressed, "#test-custom-btn")
    async def on_test_custom_button(self) -> None:
        """Test custom CSS selector entered by user."""
        await self.action_test_custom()

    async def action_test_custom(self) -> None:
        """Test custom selector from input field."""
        if not self.analyzer:
            status = self.query_one("#status-message", Static)
            status.update("⚠️  No content loaded yet")
            return

        selector_input = self.query_one("#custom-selector-input", Input)
        custom_selector = selector_input.value.strip()

        if not custom_selector:
            status = self.query_one("#status-message", Static)
            status.update("⚠️  Enter a CSS selector to test")
            return

        # Create custom candidate
        custom_candidate = {
            "selector": custom_selector,
            "score": 0,
            "type": "custom",
            "element_count": 0,
        }

        # Test it
        try:
            stats = self.analyzer.get_element_stats(custom_selector)
            if stats["count"] > 0:
                custom_candidate["element_count"] = stats["count"]
                custom_candidate["score"] = stats["paragraphs"] * 5  # Simple scoring
                await self._preview_candidate(custom_candidate)

                status = self.query_one("#status-message", Static)
                status.update(f"✅ Custom selector matched {stats['count']} elements")
            else:
                preview = self.query_one("#preview-content", Static)
                preview.update("⚠️  Custom selector matched no elements")

                status = self.query_one("#status-message", Static)
                status.update("⚠️  No elements matched")
        except Exception as e:
            status = self.query_one("#status-message", Static)
            status.update(f"❌ Invalid selector: {e}")

    async def action_save_rule(self) -> None:
        """Save selected scraping rule to feed."""
        if not self.selected_selector:
            status = self.query_one("#status-message", Static)
            status.update("⚠️  No selector selected")
            return

        status = self.query_one("#status-message", Static)
        status.update(f"💾 Saving rule: {self.selected_selector}")

        # Call callback if provided
        if self.on_save_callback:
            try:
                await self.on_save_callback(self.feed_id, self.selected_selector)
                status.update(f"✅ Rule saved: {self.selected_selector}")
                # Dismiss screen after short delay
                self.set_timer(2.0, self.action_dismiss)
            except Exception as e:
                status.update(f"❌ Failed to save: {e}")
        else:
            # No callback - just show the rule
            status.update(f"Info: Scraping rule: {self.selected_selector} (no save callback configured)")

    async def action_dismiss(self) -> None:
        """Close the screen and return to previous screen."""
        # Clean up fetcher
        if self.fetcher:
            await self.fetcher.close()

        self.dismiss()
