"""Tests for help screen."""

from textual.screen import Screen

from miniflux_tui.ui.screens.help import HelpScreen


class TestHelpScreenBindings:
    """Test HelpScreen key bindings."""

    def test_help_screen_has_bindings(self):
        """Test HelpScreen has correct bindings."""
        help_screen = HelpScreen()
        assert hasattr(help_screen, "BINDINGS")
        assert isinstance(help_screen.BINDINGS, list)
        assert len(help_screen.BINDINGS) == 2

    def test_help_screen_has_escape_binding(self):
        """Test HelpScreen has Escape key binding."""
        help_screen = HelpScreen()
        escape_bindings = [b for b in help_screen.BINDINGS if b.key == "escape"]
        assert len(escape_bindings) == 1
        assert escape_bindings[0].action == "close"

    def test_help_screen_has_q_binding(self):
        """Test HelpScreen has q key binding."""
        help_screen = HelpScreen()
        q_bindings = [b for b in help_screen.BINDINGS if b.key == "q"]
        assert len(q_bindings) == 1
        assert q_bindings[0].action == "close"


class TestHelpScreenCompose:
    """Test HelpScreen compose method."""

    def test_compose_method_exists(self):
        """Test compose() method exists."""
        help_screen = HelpScreen()
        assert hasattr(help_screen, "compose")
        assert callable(help_screen.compose)

    def test_compose_is_generator(self):
        """Test compose returns a generator/iterable."""
        help_screen = HelpScreen()
        result = help_screen.compose()
        # Verify it's a generator
        assert hasattr(result, "__iter__") or hasattr(result, "__next__")


class TestHelpScreenActionClose:
    """Test HelpScreen action_close method."""

    def test_action_close_method_exists(self):
        """Test action_close method is defined."""
        help_screen = HelpScreen()
        assert hasattr(help_screen, "action_close")
        assert callable(help_screen.action_close)

    def test_action_close_is_callable(self):
        """Test action_close method is callable."""
        help_screen = HelpScreen()
        # Simply verify the method exists and can be called
        assert callable(getattr(help_screen, "action_close", None))


class TestHelpScreenContent:
    """Test HelpScreen content and layout."""

    def test_help_screen_initialization(self):
        """Test HelpScreen can be initialized."""
        help_screen = HelpScreen()
        assert help_screen is not None
        assert isinstance(help_screen, HelpScreen)

    def test_help_screen_is_screen(self):
        """Test HelpScreen is a Textual Screen."""
        help_screen = HelpScreen()
        assert isinstance(help_screen, Screen)

    def test_help_screen_source_code_integrity(self):
        """Test help screen source is properly defined."""
        help_screen = HelpScreen()
        # Verify the class has the expected methods
        assert hasattr(help_screen, "compose")
        assert hasattr(help_screen, "action_close")
        assert hasattr(help_screen, "BINDINGS")
