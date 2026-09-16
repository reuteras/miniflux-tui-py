# SPDX-License-Identifier: MIT
"""Atheris-based fuzz target for the untrusted HTML rendering path.

Feed HTML is the largest attacker-controlled input the TUI handles. This target
drives the sanitizer, the HTML-to-Markdown conversion and link extraction, and
checks that the resulting text can be parsed by Textual's markup engine without
raising, which is what the widgets ultimately do with it.

Run with::

    uv run --group fuzz python fuzz/fuzz_html.py -atheris_runs=100000
"""

from __future__ import annotations

import sys

import atheris

with atheris.instrument_imports():
    from textual.content import Content

    from miniflux_tui.ui.screens.entry_reader import EntryReaderScreen
    from miniflux_tui.utils import escape_markup, strip_control_chars


def test_one_input(data: bytes) -> None:
    """Fuzz entry point: the rendering pipeline must never raise on any HTML."""
    fdp = atheris.FuzzedDataProvider(data)
    html = fdp.ConsumeUnicodeNoSurrogates(4096)

    sanitized = EntryReaderScreen._sanitize_feed_html(html)
    # Sanitized output must be free of terminal control characters
    if strip_control_chars(sanitized) != sanitized:
        msg = "sanitizer leaked control characters"
        raise AssertionError(msg)

    screen = EntryReaderScreen.__new__(EntryReaderScreen)
    markdown = screen._html_to_markdown(html)
    EntryReaderScreen._extract_links(markdown)

    # Anything shown through escape_markup must parse as markup without error
    Content.from_markup(escape_markup(html))


def main() -> None:
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
