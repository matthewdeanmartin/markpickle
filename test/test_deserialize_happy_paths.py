from __future__ import annotations
import io

import markpickle
from markpickle.config_class import Config
from markpickle.deserialize import load


def test_load_returns_configured_empty_value_for_empty_stream() -> None:
    config = Config()
    config.empty_string_is = "EMPTY"

    result = load(io.StringIO(""), config=config)

    assert result == "EMPTY"


def test_load_ordered_list_becomes_tuple_when_enabled() -> None:
    config = Config()
    config.ordered_list_as_tuple = True

    result = markpickle.loads("1. first\n2. second\n", config=config)

    assert result == ("first", "second")


def test_load_formatted_paragraph_becomes_plain_scalar() -> None:
    result = markpickle.loads("Cat **and** `Dog`")

    assert result == "Cat  and   Dog"


def test_load_table_can_become_list_of_lists() -> None:
    config = Config()
    config.tables_become_list_of_lists = True
    markdown = "| name | age |\n| --- | --- |\n| Alice | 30 |\n| Bob | 25 |\n"

    result = markpickle.loads(markdown, config=config)

    assert result == [["name", "age"], ["Alice", "30"], ["Bob", "25"]]


def test_load_adds_missing_top_key_when_document_starts_with_intro() -> None:
    markdown = "Intro text.\n\n# Child\n\nvalue\n"

    result = markpickle.loads(markdown)

    assert result == {"Missing Key": "Intro text.", "Child": "value"}


def test_load_applies_object_hook_to_outer_result() -> None:
    markdown = "# Name\n\nRingo\n"

    result = markpickle.loads(markdown, object_hook=lambda obj: {"wrapped": obj})

    assert result == {"wrapped": {"Name": "Ringo"}}


def test_load_all_reads_multiple_documents_from_stream() -> None:
    stream = io.StringIO("alpha\n---\n1. first\n2. second\n")

    result = list(markpickle.deserialize.load_all(stream))

    assert result == ["alpha", ["first", "second"]]
