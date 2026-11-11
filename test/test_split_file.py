from __future__ import annotations

import io

import pytest

from markpickle.split_file_code import is_markdown_separator, split_file


@pytest.mark.parametrize("row", ["---", "- - -", "***", "* * *", "___", "_ _ _"])
def test_recognizes_markdown_horizontal_rules(row):
    assert is_markdown_separator(row, last_row_blank=False)


@pytest.mark.parametrize("row", ["--", "**", "___x", "-*-", "text", ""])
def test_rejects_non_separator_rows(row):
    assert not is_markdown_separator(row, last_row_blank=True)


def test_split_file_discards_separators_and_empty_sections():
    source = io.BytesIO(b"first\n---\n---\nsecond\n***\n")

    assert list(split_file(source)) == ["first\n", "second\n"]


def test_split_file_keeps_blank_lines_and_final_unterminated_section():
    source = io.BytesIO(b"first\n\n---\nlast")

    assert list(split_file(source)) == ["first\n\n", "last"]
