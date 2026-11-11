from __future__ import annotations

import datetime
import urllib.parse

import pytest

import markpickle
from markpickle.deserialize import process_list_of_tokens
from markpickle._mistune_compat import parse_markdown


def test_markdown_link_in_list_becomes_parsed_url():
    result = markpickle.loads("- [site](https://example.com/path?q=1)\n")

    assert result == [urllib.parse.urlparse("https://example.com/path?q=1")]


def test_formatted_list_item_strips_markup_and_infers_value():
    assert markpickle.loads("- **42**\n- *true*\n- `plain text`\n") == [42, True, "plain text"]


def test_list_item_with_nested_code_block_preserves_code_text():
    result = markpickle.loads("- before\n\n  ```\n  code line\n  ```\n")

    assert result[0] == "before"
    assert any("code line" in value for value in result[1:] if isinstance(value, str))


def test_root_markdown_table_can_be_parsed_as_list_of_dicts_with_inferred_values():
    result = markpickle.loads("| count | active |\n| --- | --- |\n| 3 | True |\n")

    assert result == [{"count": 3, "active": True}]


def test_root_markdown_table_can_preserve_string_cells_as_lists():
    config = markpickle.Config()
    config.tables_become_list_of_lists = True

    assert markpickle.loads("| count |\n| --- |\n| 03 |\n", config) == [["count"], ["03"]]


def test_mixed_plain_and_formatted_paragraph_is_joined_as_scalar():
    assert markpickle.loads("plain **bold** text") == "plain  bold  text"


def test_code_block_after_scalar_is_returned_as_separate_tuple_item():
    result = markpickle.loads("intro\n\n```\nbody\n```")

    assert result == ("intro", "body\n")


def test_definition_list_pairs_are_all_preserved():
    assert markpickle.loads("red\n: color\n\nblue\n: color\n") == ({"red": "color"}, {"blue": "color"})


def test_extract_scalar_recognizes_date_but_leaves_invalid_date_text():
    config = markpickle.Config()

    assert markpickle.loads("2024-02-29") == datetime.date(2024, 2, 29)
    assert markpickle.loads("2024-02-30") == "2024-02-30"
    assert markpickle.loads("3.2e2") == 320.0


def test_process_list_of_tokens_rejects_unconsumed_heading():
    tokens = parse_markdown("# leftover")

    with pytest.raises(TypeError, match="Unconsumed header"):
        process_list_of_tokens(tokens, markpickle.Config())
