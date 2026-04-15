"""
Behavioral snapshot tests for markpickle.

These tests capture the CURRENT behavior of markpickle as of pre-1.0.
When behavior intentionally changes (especially table heuristics), update
these tests and document the break in the changelog.

No mocks. Real serialization/deserialization only.
"""

from __future__ import annotations

import datetime
import io
import json

import pytest

import markpickle
from markpickle import Config

# ---------------------------------------------------------------------------
# Scalar serialization
# ---------------------------------------------------------------------------


class TestSerializeScalars:
    def test_string(self):
        assert markpickle.dumps("hello") == "hello"

    def test_empty_string(self):
        assert markpickle.dumps("") == ""

    def test_int(self):
        assert markpickle.dumps(42) == "42"

    def test_zero(self):
        assert markpickle.dumps(0) == "0"

    def test_negative_int(self):
        assert markpickle.dumps(-7) == "-7"

    def test_float(self):
        assert markpickle.dumps(3.14) == "3.14"

    def test_negative_float(self):
        assert markpickle.dumps(-2.5) == "-2.5"

    def test_bool_true(self):
        assert markpickle.dumps(True) == "True"

    def test_bool_false(self):
        assert markpickle.dumps(False) == "False"

    def test_none(self):
        assert markpickle.dumps(None) == ""

    def test_date(self):
        assert markpickle.dumps(datetime.date(2024, 1, 15)) == "2024-01-15"

    def test_datetime_preserves_time(self):
        """Fixed in 2.0.0: datetime now serializes with time component."""
        result = markpickle.dumps(datetime.datetime(2024, 1, 15, 10, 30, 45))
        assert result == "2024-01-15 10:30:45"

    def test_bytes_as_data_url(self):
        result = markpickle.dumps(b"hello bytes")
        assert result.startswith("![bytes](data:image/png;base64,")
        assert result.endswith(")")


# ---------------------------------------------------------------------------
# Scalar deserialization
# ---------------------------------------------------------------------------


class TestDeserializeScalars:
    def test_string(self):
        assert markpickle.loads("hello") == "hello"

    def test_int(self):
        assert markpickle.loads("42") == 42

    def test_zero(self):
        assert markpickle.loads("0") == 0

    def test_float(self):
        assert markpickle.loads("3.14") == 3.14

    def test_negative_int(self):
        """Fixed in 2.0.0: negative ints now deserialize as int."""
        assert markpickle.loads("-5") == -5
        assert isinstance(markpickle.loads("-5"), int)

    def test_negative_float(self):
        assert markpickle.loads("-3.14") == -3.14

    def test_bool_true(self):
        assert markpickle.loads("True") is True

    def test_bool_true_lowercase(self):
        assert markpickle.loads("true") is True

    def test_bool_false(self):
        assert markpickle.loads("False") is False

    def test_bool_false_lowercase(self):
        assert markpickle.loads("false") is False

    def test_none(self):
        assert markpickle.loads("None") is None

    def test_date(self):
        assert markpickle.loads("2024-01-15") == datetime.date(2024, 1, 15)

    def test_empty_string(self):
        assert markpickle.loads("") == ""

    def test_two_paragraphs_become_tuple(self):
        """Two separate paragraphs deserialize as a tuple."""
        result = markpickle.loads("hello\n\nworld\n")
        assert result == ("hello", "world")


# ---------------------------------------------------------------------------
# Scalar deserialization with config
# ---------------------------------------------------------------------------


class TestDeserializeScalarsConfig:
    def test_no_inference_int_stays_string(self):
        c = Config()
        c.infer_scalar_types = False
        assert markpickle.loads("42", config=c) == "42"

    def test_no_inference_float_stays_string(self):
        c = Config()
        c.infer_scalar_types = False
        assert markpickle.loads("3.14", config=c) == "3.14"

    def test_no_inference_negative_stays_string(self):
        c = Config()
        c.infer_scalar_types = False
        assert markpickle.loads("-5", config=c) == "-5"

    def test_no_inference_bool_returns_string(self):
        """Fixed in 2.0.0: infer_scalar_types=False now truly returns strings for everything."""
        c = Config()
        c.infer_scalar_types = False
        assert markpickle.loads("True", config=c) == "True"

    def test_no_inference_none_returns_string(self):
        """Fixed in 2.0.0: infer_scalar_types=False now truly returns strings for everything."""
        c = Config()
        c.infer_scalar_types = False
        assert markpickle.loads("None", config=c) == "None"

    def test_no_inference_date_returns_string(self):
        """Fixed in 2.0.0: infer_scalar_types=False now truly returns strings for everything."""
        c = Config()
        c.infer_scalar_types = False
        assert markpickle.loads("2024-01-15", config=c) == "2024-01-15"

    def test_custom_true_values(self):
        c = Config()
        c.true_values = ["True", "true", "yes"]
        assert markpickle.loads("yes", config=c) is True

    def test_custom_false_values(self):
        c = Config()
        c.false_values = ["False", "false", "no"]
        assert markpickle.loads("no", config=c) is False

    def test_none_values_config_now_works(self):
        """Fixed in 2.0.0: none_values list is now consulted during deserialization."""
        c = Config()
        c.none_values = ["None", "nil", "null", "N/A"]
        assert markpickle.loads("null", config=c) is None
        assert markpickle.loads("N/A", config=c) is None
        assert markpickle.loads("None", config=c) is None

    def test_none_string_still_works(self):
        """none_string still controls None detection alongside none_values."""
        c = Config()
        c.none_string = "null"
        assert markpickle.loads("null", config=c) is None
        # "None" is in default none_values, so it still works
        assert markpickle.loads("None", config=c) is None

    def test_empty_string_is_dict(self):
        c = Config()
        c.empty_string_is = {}
        assert markpickle.loads("", config=c) == {}

    def test_empty_string_is_list(self):
        c = Config()
        c.empty_string_is = []
        assert markpickle.loads("", config=c) == []


# ---------------------------------------------------------------------------
# Serialize config options
# ---------------------------------------------------------------------------


class TestSerializeConfig:
    def test_force_final_newline(self):
        c = Config()
        c.serialize_force_final_newline = True
        assert markpickle.dumps("hello", config=c) == "hello\n"

    def test_none_string_custom(self):
        c = Config()
        c.none_string = "null"
        # None serializes to empty string regardless of none_string
        # (none_string is used by render_scalar, but dump() short-circuits None)
        assert markpickle.dumps(None, config=c) == ""

    def test_bullet_style_asterisk(self):
        c = Config()
        c.list_bullet_style = "*"
        assert markpickle.dumps(["a", "b"], config=c) == "* a\n* b\n"

    def test_bullet_style_plus(self):
        c = Config()
        c.list_bullet_style = "+"
        assert markpickle.dumps(["a", "b"], config=c) == "+ a\n+ b\n"

    def test_date_format_custom(self):
        c = Config()
        c.serialize_date_format = "%d/%m/%Y"
        assert markpickle.dumps(datetime.date(2024, 1, 15), config=c) == "15/01/2024"

    def test_bytes_mime_type(self):
        c = Config()
        c.serialize_bytes_mime_type = "application/octet-stream"
        result = markpickle.dumps(b"data", config=c)
        assert "application/octet-stream" in result

    def test_default_callback(self):
        result = markpickle.dumps({1, 2, 3}, default=str)
        assert result == str({1, 2, 3})


# ---------------------------------------------------------------------------
# List serialization
# ---------------------------------------------------------------------------


class TestSerializeLists:
    def test_empty_list(self):
        assert markpickle.dumps([]) == ""

    def test_string_list(self):
        assert markpickle.dumps(["a", "b", "c"]) == "- a\n- b\n- c\n"

    def test_int_list(self):
        assert markpickle.dumps([1, 2, 3]) == "- 1\n- 2\n- 3\n"

    def test_mixed_type_list(self):
        result = markpickle.dumps(["hello", "42", "True"])
        assert result == "- hello\n- 42\n- True\n"

    def test_nested_list_flattens_indent(self):
        """Nested lists use indentation."""
        result = markpickle.dumps([[1, 2], [3, 4]])
        # Known quirk: nested lists are indented but not wrapped in parent bullets
        assert result == "  - 1\n  - 2\n  - 3\n  - 4\n"

    def test_list_of_dicts_becomes_table(self):
        result = markpickle.dumps([{"a": "1", "b": "2"}, {"a": "3", "b": "4"}])
        assert "| a | b |" in result
        assert "| 1 | 2 |" in result
        assert "| 3 | 4 |" in result

    def test_list_of_dicts_no_table(self):
        c = Config()
        c.serialize_child_dict_as_table = False
        result = markpickle.dumps([{"a": "1"}, {"a": "2"}], config=c)
        # Without tables, dicts in lists use bullet style
        assert "|" not in result


# ---------------------------------------------------------------------------
# List deserialization
# ---------------------------------------------------------------------------


class TestDeserializeLists:
    def test_string_list(self):
        assert markpickle.loads("- a\n- b\n- c\n") == ["a", "b", "c"]

    def test_int_list(self):
        assert markpickle.loads("- 1\n- 2\n- 3\n") == [1, 2, 3]

    def test_nested_list(self):
        assert markpickle.loads("- a\n  - b\n  - c\n") == ["a", ["b", "c"]]

    def test_mixed_type_list(self):
        result = markpickle.loads("- hello\n- 42\n- True\n- 2024-01-15\n")
        assert result == ["hello", 42, True, datetime.date(2024, 1, 15)]


# ---------------------------------------------------------------------------
# Dict serialization
# ---------------------------------------------------------------------------


class TestSerializeDicts:
    def test_empty_dict(self):
        assert markpickle.dumps({}) == ""

    def test_single_key(self):
        assert markpickle.dumps({"key": "val"}) == "# key\n\nval\n"

    def test_multiple_keys(self):
        result = markpickle.dumps({"a": "1", "b": "2"})
        assert result == "# a\n\n1\n\n# b\n\n2\n"

    def test_dict_with_list_values(self):
        result = markpickle.dumps({"fruits": ["apple", "banana"], "vegs": ["carrot"]})
        assert result == "- fruits\n  - apple\n  - banana\n- vegs\n  - carrot\n"

    def test_nested_dict_becomes_table(self):
        """With default config, a child dict becomes a table."""
        result = markpickle.dumps({"cat": {"name": "Ringo", "species": "Felix"}})
        assert "# cat" in result
        assert "| name" in result
        assert "| Ringo" in result

    def test_nested_dict_no_table(self):
        """With serialize_child_dict_as_table=False, child dict recurses with deeper ATX headers."""
        c = Config()
        c.serialize_child_dict_as_table = False
        result = markpickle.dumps({"cat": {"name": "Ringo", "species": "Felix"}}, config=c)
        assert "# cat" in result
        assert "## name" in result
        assert "Ringo" in result

    def test_no_headers_mode(self):
        c = Config()
        c.serialize_headers_are_dict_keys = False
        result = markpickle.dumps({"a": "1", "b": "2"}, config=c)
        assert result == "- a : 1\n- b : 2\n"


# ---------------------------------------------------------------------------
# Dict deserialization
# ---------------------------------------------------------------------------


class TestDeserializeDicts:
    def test_single_key(self):
        assert markpickle.loads("# key\n\nval\n") == {"key": "val"}

    def test_multiple_keys(self):
        result = markpickle.loads("# a\n\n1\n\n# b\n\n2\n")
        assert result == {"a": 1, "b": 2}

    def test_nested_dict_via_headers(self):
        md = "# cat\n\n## name\n\nRingo\n\n## species\n\nFelix\n"
        result = markpickle.loads(md)
        assert result == {"cat": {"name": "Ringo", "species": "Felix"}}

    def test_h2_only_headers(self):
        """Headers that start at h2 still form a dict."""
        md = "## a\n\nfoo\n\n## b\n\nbar\n"
        result = markpickle.loads(md)
        assert result == {"a": "foo", "b": "bar"}

    def test_three_level_nesting_works(self):
        """Fixed in 2.0.0: 3-level ATX nesting now works."""
        md = "# a\n\n## b\n\n### c\n\ndeep\n"
        result = markpickle.loads(md)
        assert result == {"a": {"b": {"c": "deep"}}}

    def test_missing_top_key_added(self):
        """When doc has headers but no initial h1, a Missing Key is inserted."""
        result = markpickle.loads("some text\n\n# header\n\nvalue\n")
        assert "Missing Key" in result
        assert result["header"] == "value"

    def test_missing_top_key_disabled(self):
        c = Config()
        c.deserialized_add_missing_key = False
        result = markpickle.loads("## sub\n\nval\n", config=c)
        assert result == {"sub": "val"}

    def test_custom_missing_key_name(self):
        c = Config()
        c.deserialized_missing_key_name = "Untitled"
        result = markpickle.loads("some text\n\n# header\n\nvalue\n", config=c)
        assert "Untitled" in result

    def test_definition_list(self):
        result = markpickle.loads("Apple\n:   A fruit\n")
        assert result == {"Apple": "A fruit"}

    def test_dict_with_list_value(self):
        md = "# fruits\n\n- apple\n- banana\n"
        result = markpickle.loads(md)
        assert result == {"fruits": ["apple", "banana"]}


# ---------------------------------------------------------------------------
# Table serialization
# ---------------------------------------------------------------------------


class TestSerializeTables:
    def test_list_of_dicts_to_table(self):
        data = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        result = markpickle.dumps(data)
        lines = result.strip().split("\n")
        assert len(lines) == 4  # header, separator, 2 data rows
        assert "| name" in lines[0]
        assert "| age" in lines[0]
        assert "| ---" in lines[1] or "| -" in lines[1]
        assert "Alice" in lines[2]
        assert "Bob" in lines[3]

    def test_single_row_table(self):
        data = [{"x": "1"}]
        result = markpickle.dumps(data)
        lines = result.strip().split("\n")
        assert len(lines) == 3  # header, separator, 1 row

    def test_child_dict_as_table(self):
        """A dict value that is itself a flat dict becomes a table under its header."""
        data = {"section": {"a": "1", "b": "2"}}
        result = markpickle.dumps(data)
        assert "# section" in result
        assert "|" in result

    def test_tabulate_style(self):
        c = Config()
        c.serialize_child_dict_as_table = True
        c.serialize_tables_tabulate_style = True
        result = markpickle.dumps({"h": {"a": "1", "b": "2"}}, config=c)
        assert "# h" in result
        assert "|" in result


# ---------------------------------------------------------------------------
# Table deserialization
# ---------------------------------------------------------------------------


class TestDeserializeTables:
    def test_table_to_list_of_dicts(self):
        md = "| a | b |\n| - | - |\n| 1 | 2 |\n| 3 | 4 |\n"
        result = markpickle.loads(md)
        # Cell values are inferred: "1" becomes int 1
        assert result == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]

    def test_table_to_list_of_lists(self):
        c = Config()
        c.tables_become_list_of_lists = True
        md = "| a | b |\n| - | - |\n| 1 | 2 |\n"
        result = markpickle.loads(md, config=c)
        assert result == [["a", "b"], ["1", "2"]]

    def test_table_duplicate_headers_raises(self):
        md = "| a | a |\n| - | - |\n| 1 | 2 |\n"
        with pytest.raises(ValueError, match="Duplicate"):
            markpickle.loads(md)

    def test_table_duplicate_headers_ok_as_lists(self):
        """Duplicate headers are fine in list-of-lists mode."""
        c = Config()
        c.tables_become_list_of_lists = True
        md = "| a | a |\n| - | - |\n| 1 | 2 |\n"
        result = markpickle.loads(md, config=c)
        assert result == [["a", "a"], ["1", "2"]]

    def test_table_empty_header(self):
        md = "| a |   | b |\n| - | - | - |\n| 1 | 2 | 3 |\n"
        result = markpickle.loads(md)
        # Cell values are inferred: "1" becomes int 1
        assert result == [{"a": 1, "": 2, "b": 3}]

    def test_table_multiword_headers(self):
        md = "| first name | last name |\n| ---------- | --------- |\n| Alice | Smith |\n"
        result = markpickle.loads(md)
        assert result == [{"first name": "Alice", "last name": "Smith"}]

    def test_pandas_style_alignment(self):
        """Tables with colon alignment markers parse correctly."""
        c = Config()
        c.tables_become_list_of_lists = True
        md = "| weekday   |   temp |\n" "|:----------|-------:|\n" "| monday    |     20 |\n"
        result = markpickle.loads(md, config=c)
        assert result == [["weekday", "temp"], ["monday", "20"]]

    def test_table_under_header(self):
        """A table nested under a header becomes a dict key -> list-of-dicts."""
        md = "# cat\n\n| name  | species |\n| ----- | ------- |\n| Ringo | Felix   |\n"
        result = markpickle.loads(md)
        assert result == {"cat": [{"name": "Ringo", "species": "Felix"}]}


# ---------------------------------------------------------------------------
# Round-trip behavior
# ---------------------------------------------------------------------------


class TestRoundTrip:
    """Captures which types survive a dumps->loads cycle and how."""

    def test_string(self):
        assert markpickle.loads(markpickle.dumps("hello")) == "hello"

    def test_int(self):
        assert markpickle.loads(markpickle.dumps(42)) == 42

    def test_zero(self):
        assert markpickle.loads(markpickle.dumps(0)) == 0

    def test_float(self):
        assert markpickle.loads(markpickle.dumps(3.14)) == 3.14

    def test_bool_true(self):
        assert markpickle.loads(markpickle.dumps(True)) is True

    def test_bool_false(self):
        assert markpickle.loads(markpickle.dumps(False)) is False

    def test_date(self):
        d = datetime.date(2024, 1, 15)
        assert markpickle.loads(markpickle.dumps(d)) == d

    def test_string_list(self):
        val = ["a", "b", "c"]
        assert markpickle.loads(markpickle.dumps(val)) == val

    def test_string_dict(self):
        """All-string dicts round-trip cleanly with default config."""
        val = {"key": "val"}
        assert markpickle.loads(markpickle.dumps(val)) == val

    def test_multi_key_dict_values_get_inferred(self):
        """Dict values that look numeric get inferred on round-trip."""
        val = {"a": "1", "b": "2"}
        result = markpickle.loads(markpickle.dumps(val))
        # "1" -> serialized as "1" -> deserialized as int 1
        assert result == {"a": 1, "b": 2}

    def test_multi_key_dict_string_values_survive(self):
        """Non-numeric string values survive round-trip."""
        val = {"name": "Alice", "city": "NYC"}
        assert markpickle.loads(markpickle.dumps(val)) == val

    def test_list_of_dicts_roundtrip(self):
        # String values that look numeric will be inferred back as ints on loads
        val = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        assert markpickle.loads(markpickle.dumps(val)) == val

    def test_nested_dict_roundtrip_becomes_list_of_dicts(self):
        """Known quirk: nested dict serializes as table, deserializes as
        list-of-dicts wrapped in outer dict. NOT the same shape."""
        val = {"cat": {"name": "Ringo", "species": "Felix"}}
        result = markpickle.loads(markpickle.dumps(val))
        # Round-trip changes shape!
        assert result == {"cat": [{"name": "Ringo", "species": "Felix"}]}
        assert result != val

    def test_dict_with_list_values_loses_structure(self):
        """Known quirk: dict with list values loses dict structure on round-trip."""
        val = {"fruits": ["apple", "banana"]}
        md = markpickle.dumps(val)
        result = markpickle.loads(md)
        # Becomes a flat list, not a dict
        assert result == ["fruits", ["apple", "banana"]]
        assert result != val

    def test_bytes_roundtrip(self):
        val = b"hello bytes"
        assert markpickle.loads(markpickle.dumps(val)) == val

    def test_none_roundtrip_fails(self):
        """None serializes to empty string, which deserializes to empty string."""
        assert markpickle.loads(markpickle.dumps(None)) == ""

    def test_empty_dict_roundtrip_fails(self):
        """Empty dict serializes to empty string."""
        assert markpickle.loads(markpickle.dumps({})) == ""

    def test_empty_list_roundtrip_fails(self):
        """Empty list serializes to empty string."""
        assert markpickle.loads(markpickle.dumps([])) == ""


# ---------------------------------------------------------------------------
# Stream I/O (dump / load)
# ---------------------------------------------------------------------------


class TestStreamIO:
    def test_dump_to_stream(self):
        s = io.StringIO()
        markpickle.dump(["a", "b"], s)
        s.seek(0)
        assert s.read() == "- a\n- b\n"

    def test_load_from_stream(self):
        s = io.StringIO("- x\n- y\n")
        assert markpickle.load(s) == ["x", "y"]

    def test_dump_load_stream_roundtrip(self):
        val = {"key": "value"}
        s = io.StringIO()
        markpickle.dump(val, s)
        s.seek(0)
        assert markpickle.load(s) == val


# ---------------------------------------------------------------------------
# File I/O with tmp_path
# ---------------------------------------------------------------------------


class TestFileIO:
    def test_dump_load_file(self, tmp_path):
        val = ["hello", "world"]
        f = tmp_path / "test.md"
        with open(f, "w") as fh:
            markpickle.dump(val, fh)
        with open(f) as fh:
            result = markpickle.load(fh)
        assert result == val

    def test_scalar_file_roundtrip(self, tmp_path):
        f = tmp_path / "scalar.md"
        with open(f, "w") as fh:
            markpickle.dump("just a string", fh)
        with open(f) as fh:
            assert markpickle.load(fh) == "just a string"

    def test_dict_file_roundtrip(self, tmp_path):
        val = {"title": "Hello", "body": "World"}
        f = tmp_path / "dict.md"
        with open(f, "w") as fh:
            markpickle.dump(val, fh)
        with open(f) as fh:
            result = markpickle.load(fh)
        assert result == {"title": "Hello", "body": "World"}

    def test_table_file_roundtrip(self, tmp_path):
        val = [{"col1": "a", "col2": "b"}, {"col1": "c", "col2": "d"}]
        f = tmp_path / "table.md"
        with open(f, "w") as fh:
            markpickle.dump(val, fh)
        with open(f) as fh:
            result = markpickle.load(fh)
        assert result == val

    def test_bytes_file_roundtrip(self, tmp_path):
        val = b"binary content here"
        f = tmp_path / "bytes.md"
        with open(f, "w") as fh:
            markpickle.dump(val, fh)
        with open(f) as fh:
            result = markpickle.load(fh)
        assert result == val


# ---------------------------------------------------------------------------
# Multi-document
# ---------------------------------------------------------------------------


class TestMultiDoc:
    def test_dumps_all(self):
        result = markpickle.dumps_all(["hello", "world"])
        assert result == "hello\n---\n\nworld"

    def test_dumps_all_lists(self):
        result = markpickle.dumps_all([["a", "b"], ["c"]])
        assert "---" in result
        assert "- a" in result
        assert "- c" in result

    def test_dump_all_to_stream(self):
        s = io.StringIO()
        markpickle.dump_all(["hello", "world"], s)
        s.seek(0)
        content = s.read()
        assert "hello" in content
        assert "world" in content

    def test_dump_all_scalars_with_separator(self):
        """Fixed in 2.0.0: dump_all now properly emits --- separators."""
        s = io.StringIO()
        markpickle.dump_all(["hello", "world"], s)
        s.seek(0)
        content = s.read()
        assert "---" in content
        assert "hello" in content
        assert "world" in content

    def test_dump_all_stream_with_separators(self):
        """Fixed in 2.0.0: dump_all stream version now emits --- separators."""
        s = io.StringIO()
        markpickle.dump_all([["a", "b"], ["c", "d"]], s)
        s.seek(0)
        content = s.read()
        assert "---" in content

    def test_dumps_all_has_separators(self):
        """dumps_all (string version) correctly emits --- separators."""
        result = markpickle.dumps_all([["a", "b"], ["c", "d"]])
        assert "---" in result
        assert "- a\n- b" in result
        assert "- c\n- d" in result


# ---------------------------------------------------------------------------
# Sugar functions (json <-> markdown)
# ---------------------------------------------------------------------------


class TestSugar:
    def test_json_to_markdown(self):
        j = json.dumps({"a": "1"})
        result = markpickle.convert_json_to_markdown(j)
        assert result == "# a\n\n1\n"

    def test_markdown_to_json(self):
        result = markpickle.convert_markdown_to_json("# a\n\n1\n")
        parsed = json.loads(result)
        assert parsed == {"a": 1}

    def test_json_roundtrip_via_markdown(self):
        original = {"name": "Alice", "city": "NYC"}
        md = markpickle.convert_json_to_markdown(json.dumps(original))
        result = json.loads(markpickle.convert_markdown_to_json(md))
        assert result == original


# ---------------------------------------------------------------------------
# Edge cases and error handling
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_string_with_hash_not_header(self):
        """A string containing # is not treated as a header when it's just a scalar."""
        result = markpickle.dumps("# not a header")
        assert result == "# not a header"

    def test_unsupported_type_raises(self):
        with pytest.raises(NotImplementedError):
            markpickle.dumps(object())

    def test_unsupported_type_with_default(self):
        result = markpickle.dumps(object(), default=lambda x: "fallback")
        assert result == "fallback"

    def test_dict_with_none_value(self):
        """Dict values that are None get serialized."""
        result = markpickle.dumps({"key": None})
        assert "# key" in result
        assert "None" in result

    def test_dict_with_bool_values(self):
        result = markpickle.dumps({"flag": True})
        assert result == "# flag\n\nTrue\n"

    def test_very_long_string(self):
        long_str = "x" * 10000
        assert markpickle.loads(markpickle.dumps(long_str)) == long_str

    def test_string_with_newlines(self):
        """Strings with embedded newlines."""
        val = "line1\nline2"
        result = markpickle.dumps(val)
        assert "line1" in result
        assert "line2" in result

    def test_unicode_string(self):
        val = "hello"
        assert markpickle.loads(markpickle.dumps(val)) == val

    def test_special_markdown_chars_in_string(self):
        """Strings containing markdown special chars."""
        val = "has *bold* and _italic_"
        result = markpickle.dumps(val)
        assert "*bold*" in result

    def test_numeric_string_dict_key(self):
        """Dict keys that are numeric strings."""
        val = {"0": 0}
        assert markpickle.loads(markpickle.dumps(val)) == val

    def test_list_with_single_element(self):
        assert markpickle.dumps(["only"]) == "- only\n"
        assert markpickle.loads("- only\n") == ["only"]

    def test_dict_with_single_key(self):
        val = {"solo": "value"}
        assert markpickle.loads(markpickle.dumps(val)) == val


# ---------------------------------------------------------------------------
# Dataclass / class serialization
# ---------------------------------------------------------------------------


class TestClassSerialization:
    def test_dataclass(self):
        import dataclasses

        @dataclasses.dataclass
        class Point:
            x: int = 1
            y: int = 2

        result = markpickle.dumps(Point())
        assert "# x" in result
        assert "# y" in result
        assert "1" in result
        assert "2" in result

    def test_dataclass_with_python_type(self):
        import dataclasses

        @dataclasses.dataclass
        class Pt:
            x: int = 1

        c = Config()
        c.serialize_include_python_type = True
        result = markpickle.dumps(Pt(), config=c)
        assert "python_type" in result
        assert "Pt" in result

    def test_class_with_dict(self):
        class Animal:
            def __init__(self):
                self.species = "cat"
                self.name = "Whiskers"

        result = markpickle.dumps(Animal())
        assert "species" in result
        assert "cat" in result

    def test_class_with_getstate(self):
        class Custom:
            def __getstate__(self):
                return {"data": "value"}

        result = markpickle.dumps(Custom())
        assert "data" in result
        assert "value" in result


# ---------------------------------------------------------------------------
# Config defaults verification
# ---------------------------------------------------------------------------


class TestConfigDefaults:
    """Pin down default config values so changes are intentional."""

    def test_defaults(self):
        c = Config()
        assert c.infer_scalar_types is True
        assert c.true_values == ["True", "true"]
        assert c.false_values == ["False", "false"]
        assert c.none_string == "None"
        assert c.empty_string_is == ""
        assert c.tables_become_list_of_lists is False
        assert c.serialize_headers_are_dict_keys is True
        assert c.serialize_dict_as_table is False
        assert c.serialize_child_dict_as_table is True
        assert c.serialize_tables_tabulate_style is False
        assert c.serialize_force_final_newline is False
        assert c.serialize_bytes_mime_type == "image/png"
        assert c.serialize_date_format == "%Y-%m-%d"
        assert c.serialized_datetime_format == "%Y-%m-%d %H:%M:%S"
        assert c.list_bullet_style == "-"
        assert c.serialize_include_python_type is False
        assert c.serialize_images_to_pillow is False
        assert c.default is None
        assert c.deserialized_add_missing_key is True
        assert c.deserialized_missing_key_name == "Missing Key"


# ---------------------------------------------------------------------------
# Known broken behaviors (document them, mark as known)
# ---------------------------------------------------------------------------


class TestKnownQuirks:
    """Tests that document known quirks/limitations. These are NOT bugs to fix
    silently - they're behavior people might depend on. When changing these,
    bump the major version."""

    def test_datetime_preserves_time_component(self):
        """Fixed in 2.0.0: datetime.datetime now serializes with time."""
        dt_result = markpickle.dumps(datetime.datetime(2024, 1, 15, 10, 30, 0))
        d_result = markpickle.dumps(datetime.date(2024, 1, 15))
        assert dt_result == "2024-01-15 10:30:00"
        assert d_result == "2024-01-15"
        assert dt_result != d_result

    def test_negative_int_deserializes_as_int(self):
        """Fixed in 2.0.0: negative numbers now deserialize as int."""
        result = markpickle.loads("-42")
        assert result == -42
        assert isinstance(result, int)

    def test_nested_dict_table_roundtrip_shape_change(self):
        """dict -> table -> list-of-dicts. Shape changes."""
        original = {"k": {"a": "1", "b": "2"}}
        result = markpickle.loads(markpickle.dumps(original))
        assert result != original
        assert isinstance(result["k"], list)

    def test_dict_list_values_lose_keys(self):
        """Dict with list values becomes a flat list."""
        original = {"items": ["x", "y"]}
        md = markpickle.dumps(original)
        result = markpickle.loads(md)
        assert result != original

    def test_infer_scalar_types_false_returns_strings(self):
        """Fixed in 2.0.0: infer_scalar_types=False now truly returns all strings."""
        c = Config()
        c.infer_scalar_types = False
        assert markpickle.loads("True", config=c) == "True"
        assert markpickle.loads("False", config=c) == "False"
        assert markpickle.loads("None", config=c) == "None"

    def test_date_respects_infer_scalar_types_flag(self):
        """Fixed in 2.0.0: infer_scalar_types=False now skips date inference too."""
        c = Config()
        c.infer_scalar_types = False
        assert markpickle.loads("2024-01-15", config=c) == "2024-01-15"

    def test_triple_nested_dict_works(self):
        """Fixed in 2.0.0: Three levels of ATX header nesting now works."""
        result = markpickle.loads("# a\n\n## b\n\n### c\n\nval\n")
        assert result == {"a": {"b": {"c": "val"}}}

    def test_empty_values_no_roundtrip(self):
        """None, empty dict, empty list all serialize to empty string."""
        assert markpickle.dumps(None) == ""
        assert markpickle.dumps({}) == ""
        assert markpickle.dumps([]) == ""

    def test_nested_list_loses_structure(self):
        """Nested list serialization flattens the nesting."""
        original = [[1, 2], [3, 4]]
        md = markpickle.dumps(original)
        result = markpickle.loads(md)
        # Goes from [[1,2],[3,4]] -> flat or re-nested differently
        assert result != original
