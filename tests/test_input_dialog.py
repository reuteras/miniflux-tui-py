"""Tests for InputDialog screen."""

from textual.app import App, ComposeResult

from miniflux_tui.ui.screens.input_dialog import InputDialog


class SimpleApp(App):
    """Simple test app for InputDialog."""

    def compose(self) -> ComposeResult:
        """Compose the app."""
        yield InputDialog(
            title="Test Dialog",
            label="Test Input:",
            value="",
        )


class TestInputDialogInitialization:
    """Test InputDialog initialization."""

    def test_input_dialog_creation(self) -> None:
        """Test creating an InputDialog."""
        dialog = InputDialog(
            title="Test",
            label="Enter text:",
        )
        assert dialog.dialog_title == "Test"
        assert dialog.dialog_label == "Enter text:"
        assert dialog.initial_value == ""

    def test_input_dialog_with_initial_value(self) -> None:
        """Test InputDialog with initial value."""
        dialog = InputDialog(
            title="Test",
            label="URL:",
            value="https://example.com",
        )
        assert dialog.initial_value == "https://example.com"

    def test_input_dialog_with_callbacks(self) -> None:
        """Test InputDialog with callback functions."""
        submit_called = False
        cancel_called = False

        def on_submit(value: str) -> None:
            nonlocal submit_called
            submit_called = True
            assert value == "test"

        def on_cancel() -> None:
            nonlocal cancel_called
            cancel_called = True

        dialog = InputDialog(
            title="Test",
            label="Input:",
            on_submit=on_submit,
            on_cancel=on_cancel,
        )
        assert dialog.on_submit is not None
        assert dialog.on_cancel is not None


class TestInputDialogCompose:
    """Test InputDialog composition."""

    def test_input_dialog_has_bindings(self) -> None:
        """Test InputDialog has proper key bindings."""
        dialog = InputDialog(
            title="Test",
            label="Input:",
        )
        binding_keys = [b.key for b in dialog.BINDINGS]
        assert "enter" in binding_keys
        assert "escape" in binding_keys


class TestInputDialogActions:
    """Test InputDialog actions."""

    def test_input_dialog_action_submit_with_callback(self) -> None:
        """Test submit action with callback."""
        submitted_value = None

        def on_submit(value: str) -> None:
            nonlocal submitted_value
            submitted_value = value

        dialog = InputDialog(
            title="Test",
            label="Input:",
            on_submit=on_submit,
        )
        # Verify callback is set and callable
        assert dialog.on_submit is not None
        assert callable(dialog.on_submit)

    def test_input_dialog_action_cancel_with_callback(self) -> None:
        """Test cancel action with callback."""
        cancel_called = False

        def on_cancel() -> None:
            nonlocal cancel_called
            cancel_called = True

        dialog = InputDialog(
            title="Test",
            label="Input:",
            on_cancel=on_cancel,
        )
        # Verify callback is set and callable
        assert dialog.on_cancel is not None
        assert callable(dialog.on_cancel)

    def test_input_dialog_submit_without_callback(self) -> None:
        """Test submit action without callback doesn't error."""
        dialog = InputDialog(
            title="Test",
            label="Input:",
            on_submit=None,
        )
        assert dialog.on_submit is None

    def test_input_dialog_cancel_without_callback(self) -> None:
        """Test cancel action without callback doesn't error."""
        dialog = InputDialog(
            title="Test",
            label="Input:",
            on_cancel=None,
        )
        assert dialog.on_cancel is None


class TestInputDialogCSS:
    """Test InputDialog CSS styling."""

    def test_input_dialog_has_css(self) -> None:
        """Test InputDialog has CSS defined."""
        dialog = InputDialog(
            title="Test",
            label="Input:",
        )
        assert dialog.CSS is not None
        assert len(dialog.CSS) > 0
        assert "InputDialog" in dialog.CSS


class TestInputDialogIntegration:
    """Integration tests for InputDialog."""

    def test_input_dialog_bindings_structure(self) -> None:
        """Test InputDialog bindings are properly structured."""
        dialog = InputDialog(
            title="Test",
            label="Input:",
        )
        assert len(dialog.BINDINGS) == 2
        assert all(binding.key in ["enter", "escape"] for binding in dialog.BINDINGS)

    def test_input_dialog_with_none_callbacks(self) -> None:
        """Test InputDialog works with None callbacks."""
        dialog = InputDialog(
            title="Test",
            label="Input:",
            on_submit=None,
            on_cancel=None,
        )
        assert dialog.on_submit is None
        assert dialog.on_cancel is None

    def test_input_dialog_empty_initial_value(self) -> None:
        """Test InputDialog with empty initial value."""
        dialog = InputDialog(
            title="Test",
            label="Input:",
            value="",
        )
        assert dialog.initial_value == ""

    def test_input_dialog_multiline_label(self) -> None:
        """Test InputDialog with multiline label."""
        dialog = InputDialog(
            title="Test",
            label="Enter feed URL\nOr website URL:",
            value="",
        )
        assert "\n" in dialog.dialog_label

    def test_input_dialog_special_characters_in_value(self) -> None:
        """Test InputDialog with special characters in value."""
        special_url = "https://example.com/path?query=value&other=123"
        dialog = InputDialog(
            title="Test",
            label="URL:",
            value=special_url,
        )
        assert dialog.initial_value == special_url

    def test_input_dialog_long_title_and_label(self) -> None:
        """Test InputDialog with very long title and label."""
        long_title = "This is a very long dialog title that might wrap to multiple lines"
        long_label = "This is a very long label that describes what input is expected from the user"
        dialog = InputDialog(
            title=long_title,
            label=long_label,
        )
        assert dialog.dialog_title == long_title
        assert dialog.dialog_label == long_label
