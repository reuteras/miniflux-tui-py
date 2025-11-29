# SPDX-License-Identifier: MIT
"""Miniflux GUI package - entry point shim for Briefcase.

This package exists to satisfy Briefcase's requirement that the sources list
contains a package matching the app name (miniflux-gui -> miniflux_gui).
"""

from miniflux_tui.gui.app import main

__version__ = "0.7.3"
__all__ = ["main"]
