"""
Tests for DOM-style deserialization (markpickle.dom_deserialize).
"""
from __future__ import annotations

import io

import markpickle
from markpickle.dom_deserialize import load_as_dom, loads_as_dom

# ---------------------------------------------------------------------------
# Headings
# ---------------------------------------------------------------------------


def test_h1():
    result = loads_as_dom("# Title\n")
    assert result == [{"tag": "h1", "text": "Title"}]


def test_h2():
    result = loads_as_dom("## Section\n")
    assert result == [{"tag": "h2", "text": "Section"}]


def test_h6():
    result = loads_as_dom("###### Deep\n")
    assert result == [{"tag": "h6", "text": "Deep"}]


def test_multiple_headings():
    result = loads_as_dom("# Title\n\n## Section\n\n### Sub\n")
    tags = [n["tag"] for n in result]
    assert tags == ["h1", "h2", "h3"]
    assert result[0]["text"] == "Title"
    assert result[2]["text"] == "Sub"


# ---------------------------------------------------------------------------
# Paragraphs
# ---------------------------------------------------------------------------


def test_paragraph():
    result = loads_as_dom("Hello world.\n")
    assert result == [{"tag": "p", "text": "Hello world."}]


def test_paragraph_with_bold():
    result = loads_as_dom("Hello **bold** world.\n")
    assert result[0]["tag"] == "p"
    assert "bold" in result[0]["text"]
    assert "Hello" in result[0]["text"]


def test_heading_then_paragraph():
    result = loads_as_dom("# Title\n\nSome text.\n")
    assert result[0] == {"tag": "h1", "text": "Title"}
    assert result[1] == {"tag": "p", "text": "Some text."}


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------


def test_unordered_list():
    result = loads_as_dom("- alpha\n- beta\n- gamma\n")
    assert len(result) == 1
    node = result[0]
    assert node["tag"] == "ul"
    assert node["items"] == ["alpha", "beta", "gamma"]


def test_ordered_list():
    result = loads_as_dom("1. first\n2. second\n3. third\n")
    assert len(result) == 1
    node = result[0]
    assert node["tag"] == "ol"
    assert node["items"] == ["first", "second", "third"]


def test_nested_list():
    md = "- outer\n  - inner one\n  - inner two\n"
    result = loads_as_dom(md)
    assert result[0]["tag"] == "ul"
    # outer item is "outer", second item is a nested ul
    items = result[0]["items"]
    assert items[0] == "outer"
    nested = items[1]
    assert nested["tag"] == "ul"
    assert "inner one" in nested["items"]


# ---------------------------------------------------------------------------
# Code blocks
# ---------------------------------------------------------------------------


def test_code_block():
    md = "```python\nprint('hi')\n```\n"
    result = loads_as_dom(md)
    assert result[0]["tag"] == "code"
    assert "print" in result[0]["text"]
    assert result[0]["language"] == "python"


def test_indented_code_block():
    md = "    plain code\n"
    result = loads_as_dom(md)
    assert result[0]["tag"] == "code"
    assert result[0]["language"] is None


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


def test_table():
    md = "| name | age |\n| ---- | --- |\n| Alice | 30 |\n| Bob | 25 |\n"
    result = loads_as_dom(md)
    assert result[0]["tag"] == "table"
    assert result[0]["headers"] == ["name", "age"]
    assert ["Alice", "30"] in result[0]["rows"]
    assert ["Bob", "25"] in result[0]["rows"]


# ---------------------------------------------------------------------------
# Definition lists
# ---------------------------------------------------------------------------


def test_definition_list():
    md = "term\n:   definition\n"
    result = loads_as_dom(md)
    assert result[0]["tag"] == "dl"
    assert result[0]["items"][0] == {"term": "term", "definition": "definition"}


# ---------------------------------------------------------------------------
# Horizontal rule
# ---------------------------------------------------------------------------


def test_hr():
    md = "---\n"
    result = loads_as_dom(md)
    hr_nodes = [n for n in result if n["tag"] == "hr"]
    assert len(hr_nodes) == 1


# ---------------------------------------------------------------------------
# Mixed document
# ---------------------------------------------------------------------------


def test_mixed_document():
    md = "# Main\n\nIntro paragraph.\n\n## Items\n\n- one\n- two\n"
    result = loads_as_dom(md)
    tags = [n["tag"] for n in result]
    assert "h1" in tags
    assert "p" in tags
    assert "h2" in tags
    assert "ul" in tags


# ---------------------------------------------------------------------------
# load_as_dom (stream version)
# ---------------------------------------------------------------------------


def test_load_as_dom_stream():
    stream = io.StringIO("# Hello\n\nWorld.\n")
    result = load_as_dom(stream)
    assert result[0] == {"tag": "h1", "text": "Hello"}
    assert result[1] == {"tag": "p", "text": "World."}


# ---------------------------------------------------------------------------
# Exported from top-level markpickle
# ---------------------------------------------------------------------------


def test_exported_from_markpickle():
    assert hasattr(markpickle, "loads_as_dom")
    assert hasattr(markpickle, "load_as_dom")
    result = markpickle.loads_as_dom("# Hi\n")
    assert result[0]["tag"] == "h1"


# ---------------------------------------------------------------------------
# Empty / edge cases
# ---------------------------------------------------------------------------


def test_empty_string():
    result = loads_as_dom("")
    assert result == []


def test_only_newlines():
    result = loads_as_dom("\n\n\n")
    assert result == []
