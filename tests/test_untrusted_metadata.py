# SPDX-License-Identifier: MIT
"""Regression tests for untrusted metadata handling (Finding 1 & 2)."""

from textual.content import Content

from miniflux_tui.ui.screens.entry_reader import EntryReaderScreen
from miniflux_tui.utils import strip_control_chars


def test_strip_control_chars_removes_escape_keeps_tab_newline():
    # \r (CR) and \x1b (ESC) are stripped; printable chars including [2J are kept
    assert strip_control_chars("a\tb\nc\rd\x1b[2Je") == "a\tb\ncd[2Je"
    assert strip_control_chars(None) == ""


def test_strip_control_chars_removes_c1_range():
    assert strip_control_chars("\x7f\x80\x9f") == ""
    assert strip_control_chars("ok\x00null\x01soh") == "oknullsoh"


def test_markup_injection_is_neutralized():
    for hostile in ["foo [/] bar", "[Video] x", "A[@click=app.quit]X[/]", "[b]b[/b] [red]r"]:
        content = Content.from_markup("[cyan]ICON $title[/cyan]", title=strip_control_chars(hostile))
        # Exactly one span -> only the trusted [cyan] style was applied.
        assert len(content.spans) == 1
        # The hostile markup survives as literal text in the output.
        assert hostile.replace("\x1b", "") in content.plain


def test_sanitizer_strips_terminal_escapes():
    out = EntryReaderScreen._sanitize_feed_html("<p>before \x1b[2J\x1b]0;evil after</p>")
    assert "\x1b" not in out
