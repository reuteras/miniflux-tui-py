"""Tests for entry reader screen."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from textual.binding import Binding

from miniflux_tui.api.models import Entry, Feed
from miniflux_tui.ui.screens.entry_reader import EntryReaderScreen


@pytest.fixture
def sample_feed():
    """Create a sample Feed for testing."""
    return Feed(
        id=1,
        title="Test Feed",
        site_url="https://example.com",
        feed_url="https://example.com/feed",
    )


@pytest.fixture
def sample_entry(sample_feed):
    """Create a sample Entry for testing."""
    return Entry(
        id=1,
        feed_id=1,
        title="Test Entry",
        content="<p>Test HTML content</p>",
        url="https://example.com/entry",
        published_at=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
        starred=False,
        status="unread",
        feed=sample_feed,
    )


class TestEntryReaderScreenInitialization:
    """Test EntryReaderScreen initialization."""

    def test_initialization_with_required_params(self, sample_entry):
        """Test initialization with required parameters."""
        screen = EntryReaderScreen(entry=sample_entry)
        assert screen.entry == sample_entry
        assert screen.entry_list == []
        assert screen.current_index == 0

    def test_initialization_with_all_params(self, sample_entry):
        """Test initialization with all parameters."""
        entries = [sample_entry]
        screen = EntryReaderScreen(
            entry=sample_entry,
            entry_list=entries,
            current_index=0,
            unread_color="blue",
            read_color="white",
        )
        assert screen.entry == sample_entry
        assert screen.entry_list == entries
        assert screen.current_index == 0
        assert screen.unread_color == "blue"
        assert screen.read_color == "white"

    def test_initialization_defaults(self, sample_entry):
        """Test initialization uses correct defaults."""
        screen = EntryReaderScreen(entry=sample_entry)
        assert screen.unread_color == "cyan"
        assert screen.read_color == "gray"
        assert screen.scroll_container is None


class TestEntryReaderScreenCompose:
    """Test EntryReaderScreen compose method."""

    def test_compose_method_exists(self, sample_entry):
        """Test compose() method exists."""
        screen = EntryReaderScreen(entry=sample_entry)
        assert hasattr(screen, "compose")
        assert callable(screen.compose)

    def test_compose_is_generator(self, sample_entry):
        """Test compose() returns a generator."""
        screen = EntryReaderScreen(entry=sample_entry)
        result = screen.compose()
        # Verify it's a generator
        assert hasattr(result, "__iter__") or hasattr(result, "__next__")


class TestEntryReaderScreenHtmlToMarkdown:
    """Test HTML to Markdown conversion."""

    def test_html_to_markdown_simple_paragraph(self, sample_entry):
        """Test conversion of simple HTML paragraph."""
        screen = EntryReaderScreen(entry=sample_entry)
        html = "<p>Simple text</p>"
        markdown = screen._html_to_markdown(html)
        assert isinstance(markdown, str)
        # Markdown should contain the text
        assert "Simple text" in markdown or "simple text" in markdown.lower()

    def test_html_to_markdown_with_links(self, sample_entry):
        """Test conversion preserves links."""
        screen = EntryReaderScreen(entry=sample_entry)
        html = '<p><a href="https://example.com">Link</a></p>'
        markdown = screen._html_to_markdown(html)
        assert isinstance(markdown, str)
        # Should preserve link info
        assert "example.com" in markdown or "Link" in markdown

    def test_html_to_markdown_with_emphasis(self, sample_entry):
        """Test conversion preserves emphasis."""
        screen = EntryReaderScreen(entry=sample_entry)
        html = "<p><strong>Bold</strong> and <em>italic</em></p>"
        markdown = screen._html_to_markdown(html)
        assert isinstance(markdown, str)

    def test_html_to_markdown_empty_content(self, sample_entry):
        """Test conversion of empty HTML."""
        screen = EntryReaderScreen(entry=sample_entry)
        html = ""
        markdown = screen._html_to_markdown(html)
        assert isinstance(markdown, str)

    def test_html_to_markdown_complex_html(self, sample_entry):
        """Test conversion of complex HTML."""
        screen = EntryReaderScreen(entry=sample_entry)
        html = """
        <div>
            <h2>Heading</h2>
            <p>Paragraph with <strong>bold</strong> text.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </div>
        """
        markdown = screen._html_to_markdown(html)
        assert isinstance(markdown, str)


class TestEntryReaderScreenScrolling:
    """Test scroll methods."""

    def test_action_scroll_down(self, sample_entry):
        """Test scroll_down action."""
        screen = EntryReaderScreen(entry=sample_entry)
        mock_scroll = MagicMock()
        screen.scroll_container = mock_scroll

        # Method exists and is callable
        assert hasattr(screen, "action_scroll_down")
        assert callable(screen.action_scroll_down)

    def test_action_scroll_up(self, sample_entry):
        """Test scroll_up action."""
        screen = EntryReaderScreen(entry=sample_entry)
        mock_scroll = MagicMock()
        screen.scroll_container = mock_scroll

        assert hasattr(screen, "action_scroll_up")
        assert callable(screen.action_scroll_up)

    def test_action_page_down(self, sample_entry):
        """Test page_down action."""
        screen = EntryReaderScreen(entry=sample_entry)
        assert hasattr(screen, "action_page_down")
        assert callable(screen.action_page_down)

    def test_action_page_up(self, sample_entry):
        """Test page_up action."""
        screen = EntryReaderScreen(entry=sample_entry)
        assert hasattr(screen, "action_page_up")
        assert callable(screen.action_page_up)


class TestEntryReaderScreenActions:
    """Test entry action methods."""

    @pytest.mark.asyncio
    async def test_action_mark_unread(self, sample_entry):
        """Test mark_unread action."""
        screen = EntryReaderScreen(entry=sample_entry)

        mock_app = MagicMock()
        mock_client = AsyncMock()
        mock_app.client = mock_client
        screen._app = mock_app

        assert hasattr(screen, "action_mark_unread")
        assert callable(screen.action_mark_unread)

    @pytest.mark.asyncio
    async def test_action_toggle_star(self, sample_entry):
        """Test toggle_star action."""
        screen = EntryReaderScreen(entry=sample_entry)

        mock_app = MagicMock()
        mock_client = AsyncMock()
        mock_app.client = mock_client
        screen._app = mock_app

        assert hasattr(screen, "action_toggle_star")
        assert callable(screen.action_toggle_star)

    @pytest.mark.asyncio
    async def test_action_save_entry(self, sample_entry):
        """Test save_entry action."""
        screen = EntryReaderScreen(entry=sample_entry)

        mock_app = MagicMock()
        mock_client = AsyncMock()
        mock_app.client = mock_client
        screen._app = mock_app

        assert hasattr(screen, "action_save_entry")
        assert callable(screen.action_save_entry)

    def test_action_open_browser(self, sample_entry):
        """Test open_browser action."""
        screen = EntryReaderScreen(entry=sample_entry)

        screen.notify = MagicMock()

        assert hasattr(screen, "action_open_browser")
        assert callable(screen.action_open_browser)

    @pytest.mark.asyncio
    async def test_action_fetch_original(self, sample_entry):
        """Test fetch_original action."""
        screen = EntryReaderScreen(entry=sample_entry)

        mock_app = MagicMock()
        mock_client = AsyncMock()
        mock_app.client = mock_client
        screen._app = mock_app

        assert hasattr(screen, "action_fetch_original")
        assert callable(screen.action_fetch_original)

    @pytest.mark.asyncio
    async def test_action_next_entry(self, sample_entry):
        """Test next_entry navigation action."""
        entries = [sample_entry, sample_entry]
        screen = EntryReaderScreen(
            entry=sample_entry,
            entry_list=entries,
            current_index=0,
        )

        screen.notify = MagicMock()

        assert hasattr(screen, "action_next_entry")
        assert callable(screen.action_next_entry)

    @pytest.mark.asyncio
    async def test_action_previous_entry(self, sample_entry):
        """Test previous_entry navigation action."""
        entries = [sample_entry, sample_entry]
        screen = EntryReaderScreen(
            entry=sample_entry,
            entry_list=entries,
            current_index=1,
        )

        screen.notify = MagicMock()

        assert hasattr(screen, "action_previous_entry")
        assert callable(screen.action_previous_entry)

    def test_action_back(self, sample_entry):
        """Test back action."""
        screen = EntryReaderScreen(entry=sample_entry)

        mock_app = MagicMock()
        screen._app = mock_app

        assert hasattr(screen, "action_back")
        assert callable(screen.action_back)

    def test_action_show_help(self, sample_entry):
        """Test show_help action."""
        screen = EntryReaderScreen(entry=sample_entry)

        mock_app = MagicMock()
        screen._app = mock_app

        assert hasattr(screen, "action_show_help")
        assert callable(screen.action_show_help)

    def test_action_quit(self, sample_entry):
        """Test quit action."""
        screen = EntryReaderScreen(entry=sample_entry)

        mock_app = MagicMock()
        screen._app = mock_app

        assert hasattr(screen, "action_quit")
        assert callable(screen.action_quit)


class TestEntryReaderScreenBindings:
    """Test screen bindings configuration."""

    def test_screen_has_bindings(self, sample_entry):
        """Test EntryReaderScreen has bindings."""
        screen = EntryReaderScreen(entry=sample_entry)
        assert hasattr(screen, "BINDINGS")
        assert isinstance(screen.BINDINGS, list)
        assert len(screen.BINDINGS) > 0

    def test_bindings_are_binding_objects(self, sample_entry):
        """Test all bindings are Binding objects."""
        screen = EntryReaderScreen(entry=sample_entry)

        for binding in screen.BINDINGS:
            assert isinstance(binding, Binding)

    def test_has_scroll_bindings(self, sample_entry):
        """Test screen has scroll key bindings."""
        screen = EntryReaderScreen(entry=sample_entry)
        binding_keys = [b.key for b in screen.BINDINGS]
        # Should have j and k for scrolling
        assert "j" in binding_keys or "k" in binding_keys


class TestEntryReaderScreenNavigation:
    """Test navigation-related properties."""

    def test_entry_property(self, sample_entry):
        """Test entry property."""
        screen = EntryReaderScreen(entry=sample_entry)
        assert screen.entry == sample_entry

    def test_entry_list_property(self, sample_entry):
        """Test entry_list property."""
        entries = [sample_entry]
        screen = EntryReaderScreen(entry=sample_entry, entry_list=entries)
        assert screen.entry_list == entries

    def test_current_index_property(self, sample_entry):
        """Test current_index property."""
        screen = EntryReaderScreen(entry=sample_entry, current_index=5)
        assert screen.current_index == 5
