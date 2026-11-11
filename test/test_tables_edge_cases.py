from __future__ import annotations

import pytest

from markpickle.python_to_tables import (
    dict_to_markdown,
    parse_table,
    parse_table_to_list_of_dict,
    parse_table_to_lists,
)


def test_parse_table_to_lists_skips_separator_row_and_trims_cells():
    md = "| name | age |\n| --- | --- |\n| Ada | 37 |\n"

    assert parse_table_to_lists(md) == [["name", "age"], ["Ada", "37"]]


def test_parse_table_to_dicts_rejects_duplicate_headers():
    with pytest.raises(ValueError, match="Duplicate Headings"):
        parse_table_to_list_of_dict("| name | name |\n| --- | --- |\n| Ada | Lovelace |\n")


def test_parse_table_to_lists_rejects_ragged_rows():
    with pytest.raises(ValueError, match="expected 2"):
        parse_table_to_lists("| a | b |\n| --- | --- |\n| only-one |\n")


def test_parse_table_returns_columns_as_tuples():
    assert parse_table("| name | age |\n| --- | --- |\n| Ada | 37 |\n| Grace | 85 |\n") == [
        ["name", "age"],
        ("Ada", "37"),
        ("Grace", "85"),
    ]


def test_dict_to_markdown_can_render_row_without_header():
    assert dict_to_markdown({"name": "Ada"}, include_header=False) == "| Ada  |\n"
