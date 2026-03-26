from __future__ import annotations
import builtins
import sys
import types

import pytest

from markpickle import python_to_tables, third_party_tables


def test_parse_table_returns_headers_and_rows() -> None:
    markdown = "| name | age |\n| ---- | --- |\n| Ada | 30 |\n| Grace | 25 |\n"

    result = python_to_tables.parse_table(markdown)

    assert result == [["name", "age"], ("Ada", "30"), ("Grace", "25")]


def test_parse_table_to_lists_returns_rows() -> None:
    markdown = "| left | right |\n| ---- | ----- |\n| up | down |\n"

    result = python_to_tables.parse_table_to_lists(markdown)

    assert result == [["left", "right"], ["up", "down"]]


def test_parse_table_to_list_of_dict_returns_row_dicts() -> None:
    markdown = "| name | age |\n| ---- | --- |\n| Ada | 30 |\n| Grace | 25 |\n"

    result = python_to_tables.parse_table_to_list_of_dict(markdown)

    assert result == [{"name": "Ada", "age": "30"}, {"name": "Grace", "age": "25"}]


def test_dict_to_markdown_supports_headerless_rows() -> None:
    result = python_to_tables.dict_to_markdown({"name": "Ada", "age": 30}, include_header=False)

    assert result == "| Ada  | 30  |\n"


def test_dict_to_markdown_rejects_indent_greater_than_one() -> None:
    with pytest.raises(TypeError, match="remove leading space"):
        python_to_tables.dict_to_markdown({"name": "Ada"}, indent=2)


def test_third_party_tables_uses_tabulate_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_tabulate = types.SimpleNamespace(tabulate=lambda value, tablefmt: f"tablefmt={tablefmt};rows={len(value)}")
    monkeypatch.setitem(sys.modules, "tabulate", fake_tabulate)

    result = third_party_tables.to_table_tablulate_style([{"name": "Ada"}])

    assert result == "tablefmt=github;rows=1"


def test_third_party_tables_raises_helpful_error_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args, **kwargs):
        if name == "tabulate":
            raise ImportError("tabulate missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "tabulate", raising=False)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError, match=r"markpickle\[tables\]"):
        third_party_tables.to_table_tablulate_style([{"name": "Ada"}])
