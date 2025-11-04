"""Loading screen with ASCII art."""

from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Static

ASCII_ART = r"""
    ___  ________   ____      ________   ________   __     __  __  __
   /   |/  /  _/  |/ /  /____/_  ____/  / ____/ /  / /    / / / / / /
  / /| / // //    / /  /___  / / __/   / /_  / /  / /    / / / / / /
 / / |  // // /| / /  ___  / / /___   / __/ / /__/ /___ / /_/ / / /
/_/  |_/___/_/ |_/_/  ____/  /_____/  /_/   /_____/_____/ \____/ /_/
                    /____/

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
