"""Loading screen with ASCII art."""

from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Static

ASCII_ART = r"""
                  _       _  __ _                _         _
   _ __ ___  (_)_ __ (_)/ _| |_   ___  __  | |_ _   _(_)
  | '_ ` _ \ | | '_ \| | |_| | | | \ \/ /  | __| | | | |
  | | | | | || | | | | |  _| | |_| |>  < _ | |_| |_| | |
  |_| |_| |_||_|_| |_|_|_| |_|\__,_/_/\_(_) \__|\__,_|_|

                        version 0.5.4

                   ~ Loading your feeds ~
"""


class LoadingScreen(Screen):
    """A loading screen with ASCII art."""

    CSS = """
    LoadingScreen {
        align: center middle;
        background: $surface;
    }

    LoadingScreen Static {
        width: auto;
        height: auto;
        color: $accent;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the loading screen layout."""
        with Center(), Middle():
            yield Static(ASCII_ART)
