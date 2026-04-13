"""
Validation tests for items in docs/TODO.md.

Each test documents whether the TODO item is:
  - CONFIRMED BUG: the test demonstrates the failure
  - OBE / ALREADY WORKS: marked xfail or just passes
  - WORKS PARTIALLY: some cases work, others don't
"""

from __future__ import annotations

import markpickle
from markpickle import dumps, loads, loads_all

# ---------------------------------------------------------------------------
# Bug: "Doesn't deserialize python nested dict to ATX headers, except 1st level"
# STATUS: CONFIRMED - default config serializes nested dict as TABLE (not ATX),
#         and that table round-trips to list-of-dict, not the original nested dict.
# ---------------------------------------------------------------------------


def test_nested_dict_roundtrip_default_config_fails():
    """Default config serializes nested dict as a table, not ATX headers.
    Round-trip fails: {outer: {k: v}} -> [{'k': 'v'}] (list-of-dict from table)."""
    data = {"outer": {"inner1": "val1", "inner2": "val2"}}
    serialized = dumps(data)
    deserialized = loads(serialized)
    # This is the WRONG result - it comes back as a list-of-dict (from table parsing)
    assert deserialized == {"outer": [{"inner1": "val1", "inner2": "val2"}]}
    assert deserialized != data  # bug confirmed


def test_nested_dict_atx_roundtrip_works_when_handwritten():
    """ATX-header nested dict CAN be deserialized correctly from hand-written markdown."""
    md = "# outer\n\n## inner1\n\nval1\n\n## inner2\n\nval2\n"
    result = loads(md)
    assert result == {"outer": {"inner1": "val1", "inner2": "val2"}}


# ---------------------------------------------------------------------------
# Bug: "loads_all is just broken"
# STATUS: CONFIRMED - returns empty strings, not the document content
# ---------------------------------------------------------------------------


def test_loads_all_correct():
    """loads_all should return all three documents (integers with default infer_scalar_types=True)."""
    marks = "1\n---\n2\n---\n3\n"
    result = list(loads_all(marks))
    assert result == [1, 2, 3]


def test_loads_all_dict_documents():
    """loads_all should handle dict documents separated by ---."""
    marks = "# a\n\nhello\n---\n# b\n\nworld\n"
    result = list(loads_all(marks))
    assert result == [{"a": "hello"}, {"b": "world"}]


# ---------------------------------------------------------------------------
# Bug: "test_dodgy failing (whitespace handling?)"
# STATUS: CONFIRMED - paragraph content after ## heading with trailing spaces returns None
# ---------------------------------------------------------------------------


def test_dodgy_atx_paragraph_with_trailing_spaces():
    """ATX nested heading: paragraph with markdown linebreak (two trailing spaces) should parse to joined text."""
    config = markpickle.Config()
    # "a  \nb" is a markdown hard linebreak (two spaces before \n)
    marks = "\n# stuff \n\n## Test\n  \na  \nb\n\n"
    result = loads(marks, config=config)
    assert result == {"stuff": {"Test": "a b"}}


# ---------------------------------------------------------------------------
# Bug: "nested lists failing again"
# STATUS: PARTIALLY CONFIRMED
#   - list-of-lists (all nested): loses outer structure entirely (flattened)
#   - mixed list with nested sublist: WORKS fine
# ---------------------------------------------------------------------------


def test_list_of_lists_flattened_on_serialize():
    """A list that IS entirely sublists loses its outer structure when serialized."""
    data = [[1, 2], [3, 4]]
    serialized = dumps(data)
    deserialized = loads(serialized)
    # Serialized as flat indented list, outer container lost:
    assert deserialized != data  # bug confirmed
    assert deserialized == [1, 2, 3, 4]  # actual (wrong) result


def test_mixed_list_with_sublist_works():
    """A mixed list [str, [str, str], str] round-trips correctly."""
    data = ["a", ["b", "c"], "d"]
    serialized = dumps(data)
    deserialized = loads(serialized)
    assert deserialized == data  # this works fine


# ---------------------------------------------------------------------------
# Bug: "Doesn't handle when a scalar/list/etc is wrapped in bold"
# STATUS: PARTIALLY CONFIRMED
#   - bold scalar at root: WORKS (strips formatting)
#   - bold dict value: WORKS (strips formatting)
#   - bold list items: FAILS with NotImplementedError
# ---------------------------------------------------------------------------


def test_bold_root_scalar_works():
    """Bold-wrapped root scalar is stripped and returned as plain text."""
    result = loads("**hello**")
    assert result == "hello"


def test_bold_dict_value_works():
    """Bold-wrapped dict value is stripped and returned as plain text."""
    result = loads("# key\n\n**value**\n")
    assert result == {"key": "value"}


def test_bold_list_items_strips_formatting():
    """Bold-wrapped list items should strip formatting and return plain text."""
    result = loads("- **item1**\n- **item2**\n")
    assert result == ["item1", "item2"]


def test_italic_list_items_strips_formatting():
    """Italic-wrapped list items should strip formatting and return plain text."""
    result = loads("- *item1*\n- *item2*\n")
    assert result == ["item1", "item2"]


def test_bold_and_plain_mixed_list_strips_formatting():
    """List mixing bold and plain items should all return plain text."""
    result = loads("- **bold**\n- plain\n- **also bold**\n")
    assert result == ["bold", "plain", "also bold"]


# ---------------------------------------------------------------------------
# Feature: "support __getstate__()"
# STATUS: ALREADY WORKS - serialize.py checks __getstate__ in dump()
# ---------------------------------------------------------------------------


def test_getstate_already_supported():
    """__getstate__ is already checked in dump() and the dict is serialized."""

    class MyObj:
        def __getstate__(self):
            return {"x": 1, "y": 2}

    result = dumps(MyObj())
    assert result == "# x\n\n1\n\n# y\n\n2\n"


# ---------------------------------------------------------------------------
# Feature: "Treat more mixed content as tuple?"
# STATUS: ALREADY WORKS for para+list+para at root and inside dict values
# ---------------------------------------------------------------------------


def test_mixed_para_list_para_becomes_tuple():
    """Para + list + para at root is already returned as a tuple."""
    md = "First para\n\n- a\n- b\n\nSecond para\n"
    result = loads(md)
    assert result == ("First para", ["a", "b"], "Second para")


def test_mixed_content_inside_dict_value_becomes_tuple():
    """Mixed content under an ATX heading is also a tuple."""
    md = "# section\n\nsome text\n\n- list item\n\nmore text\n"
    result = loads(md)
    assert result == {"section": ("some text", ["list item"], "more text")}


# ---------------------------------------------------------------------------
# "treat multiple paragraphs with strong/bold/etc as one big string"
# STATUS: NOT DONE - currently returns a tuple of (stripped_para1, stripped_para2)
# ---------------------------------------------------------------------------


def test_multi_para_with_bold_returns_tuple_not_string():
    """Two paragraphs (one with bold) return a tuple, not a joined string."""
    md = "**bold start** and some text\n\nMore text after paragraph break\n"
    result = loads(md)
    # Currently returns a tuple; TODO says should be one big string:
    assert isinstance(result, tuple)
    assert result == ("bold start  and some text", "More text after paragraph break")


# ---------------------------------------------------------------------------
# Build: "get hypothesis slow/flaky to pass"
# STATUS: DONE (fixed in previous session)
# The test_hypothesis_roundtrip.py tests now pass reliably.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Data format: columnar dict-of-lists -> table
# STATUS: NOT DONE - serializes each list as a string repr in a table cell
# ---------------------------------------------------------------------------


def test_columnar_dict_of_lists_not_supported():
    """Dict-of-lists (columnar format) does not serialize to a proper row table."""
    data = {
        "data": {
            "Name": ["Alice", "Bob"],
            "Age": [30, 25],
        }
    }
    serialized = dumps(data)
    # Currently puts stringified lists in table cells:
    assert "['Alice', 'Bob']" in serialized  # not the desired row-per-person table
