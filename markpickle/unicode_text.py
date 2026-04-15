"""
Unicode Mathematical Alphanumeric Symbols for preserving bold/italic/monospace
through round-tripping.

Uses Unicode blocks:
- Bold: U+1D400-1D419 (A-Z), U+1D41A-1D433 (a-z), U+1D7CE-1D7D7 (0-9)
- Italic: U+1D434-1D44D (A-Z), U+1D44E-1D467 (a-z)
- Bold Italic: U+1D468-1D481 (A-Z), U+1D482-1D49B (a-z)
- Monospace: U+1D670-1D689 (A-Z), U+1D68A-1D6A3 (a-z), U+1D7F6-1D7FF (0-9)
"""

from __future__ import annotations

import re

# Build translation tables
_BOLD_UPPER = {ord("A") + i: 0x1D400 + i for i in range(26)}
_BOLD_LOWER = {ord("a") + i: 0x1D41A + i for i in range(26)}
_BOLD_DIGITS = {ord("0") + i: 0x1D7CE + i for i in range(10)}
BOLD_TABLE = {**_BOLD_UPPER, **_BOLD_LOWER, **_BOLD_DIGITS}

_ITALIC_UPPER = {ord("A") + i: 0x1D434 + i for i in range(26)}
_ITALIC_LOWER = {ord("a") + i: 0x1D44E + i for i in range(26)}
# h is special in italic: U+210E (Planck constant)
_ITALIC_LOWER[ord("h")] = 0x210E
ITALIC_TABLE = {**_ITALIC_UPPER, **_ITALIC_LOWER}

_MONO_UPPER = {ord("A") + i: 0x1D670 + i for i in range(26)}
_MONO_LOWER = {ord("a") + i: 0x1D68A + i for i in range(26)}
_MONO_DIGITS = {ord("0") + i: 0x1D7F6 + i for i in range(10)}
MONO_TABLE = {**_MONO_UPPER, **_MONO_LOWER, **_MONO_DIGITS}

# Reverse tables for detection
_REVERSE_BOLD = {v: k for k, v in BOLD_TABLE.items()}
_REVERSE_ITALIC = {v: k for k, v in ITALIC_TABLE.items()}
_REVERSE_MONO = {v: k for k, v in MONO_TABLE.items()}


def to_bold(text: str) -> str:
    """Convert ASCII text to Unicode bold mathematical symbols."""
    return text.translate(BOLD_TABLE)


def to_italic(text: str) -> str:
    """Convert ASCII text to Unicode italic mathematical symbols."""
    return text.translate(ITALIC_TABLE)


def to_monospace(text: str) -> str:
    """Convert ASCII text to Unicode monospace mathematical symbols."""
    return text.translate(MONO_TABLE)


def from_bold(text: str) -> str:
    """Convert Unicode bold mathematical symbols back to ASCII."""
    return text.translate(_REVERSE_BOLD)


def from_italic(text: str) -> str:
    """Convert Unicode italic mathematical symbols back to ASCII."""
    return text.translate(_REVERSE_ITALIC)


def from_monospace(text: str) -> str:
    """Convert Unicode monospace mathematical symbols back to ASCII."""
    return text.translate(_REVERSE_MONO)


def _is_in_range(ch: str, table: dict[int, int]) -> bool:
    """Check if a character is in a Unicode math range (values of a forward table)."""
    return ord(ch) in set(table.values())


def _detect_run(text: str, reverse_table: dict[int, int]) -> bool:
    """Check if any characters in text are from the given Unicode range."""
    return any(ord(c) in reverse_table for c in text)


def unicode_to_markdown(text: str) -> str:
    """Convert Unicode math-styled characters back to markdown formatting.

    Detects runs of bold/italic/monospace Unicode characters and wraps them
    in the appropriate markdown formatting.
    """
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        cp = ord(ch)

        if cp in _REVERSE_BOLD:
            # Collect bold run
            run = []
            while i < len(text) and ord(text[i]) in _REVERSE_BOLD:
                run.append(chr(_REVERSE_BOLD[ord(text[i])]))
                i += 1
            result.append(f"**{''.join(run)}**")
        elif cp in _REVERSE_ITALIC:
            # Collect italic run
            run = []
            while i < len(text) and ord(text[i]) in _REVERSE_ITALIC:
                run.append(chr(_REVERSE_ITALIC[ord(text[i])]))
                i += 1
            result.append(f"*{''.join(run)}*")
        elif cp in _REVERSE_MONO:
            # Collect monospace run
            run = []
            while i < len(text) and ord(text[i]) in _REVERSE_MONO:
                run.append(chr(_REVERSE_MONO[ord(text[i])]))
                i += 1
            result.append(f"`{''.join(run)}`")
        else:
            result.append(ch)
            i += 1

    return "".join(result)


def markdown_inline_to_unicode(text: str) -> str:
    """Convert inline markdown formatting to Unicode math symbols.

    **bold** -> Unicode bold
    *italic* -> Unicode italic
    `code` -> Unicode monospace
    """
    # Process bold first (** before *)
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: to_bold(m.group(1)), text)
    text = re.sub(r"\*(.+?)\*", lambda m: to_italic(m.group(1)), text)
    text = re.sub(r"`(.+?)`", lambda m: to_monospace(m.group(1)), text)
    return text


def has_unicode_formatting(text: str) -> bool:
    """Check if a string contains any Unicode math-styled characters."""
    return _detect_run(text, _REVERSE_BOLD) or _detect_run(text, _REVERSE_ITALIC) or _detect_run(text, _REVERSE_MONO)
