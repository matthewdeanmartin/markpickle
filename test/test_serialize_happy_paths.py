from __future__ import annotations
import io
from dataclasses import dataclass
from datetime import date, datetime

import pytest

from markpickle.config_class import Config
from markpickle.serialize import (
    dump,
    dump_all,
    dumps,
    dumps_all,
    render_dict,
    render_scalar,
)


def test_dumps_child_dict_uses_python_table_renderer_when_tabulate_style_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = Config()
    config.serialize_child_dict_as_table = True
    config.serialize_tables_tabulate_style = False

    def fail_if_called(_value):
        raise AssertionError("tabulate renderer should not be used")

    monkeypatch.setattr("markpickle.third_party_tables.to_table_tablulate_style", fail_if_called)

    result = dumps({"section": {"name": "Ada", "role": "admin"}}, config=config)

    assert "# section" in result
    assert "| name | role  |" in result
    assert "| Ada  | admin |" in result


def test_dumps_child_dict_uses_tabulate_renderer_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    config = Config()
    config.serialize_child_dict_as_table = True
    config.serialize_tables_tabulate_style = True

    monkeypatch.setattr(
        "markpickle.third_party_tables.to_table_tablulate_style",
        lambda value: f"| tabulate |\n| ------- |\n| {value['name']} |\n",
    )

    result = dumps({"section": {"name": "Ada"}}, config=config)

    assert "# section" in result
    assert " | tabulate |" in result
    assert " | Ada |" in result


def test_dumps_child_dict_falls_back_to_python_tables_when_tabulate_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = Config()
    config.serialize_child_dict_as_table = True
    config.serialize_tables_tabulate_style = True

    def missing_tabulate(_value):
        raise ImportError("tabulate missing")

    monkeypatch.setattr("markpickle.third_party_tables.to_table_tablulate_style", missing_tabulate)

    result = dumps({"section": {"name": "Ada", "role": "admin"}}, config=config)

    assert "# section" in result
    assert "| name | role  |" in result
    assert "| Ada  | admin |" in result


def test_dumps_none_returns_empty_string() -> None:
    assert dumps(None) == ""


def test_dumps_top_level_list_of_dicts_uses_python_table_renderer() -> None:
    result = dumps([{"name": "Ada", "age": 30}, {"name": "Grace", "age": 25}])

    assert result == ("| name  | age |\n" "| ----- | --- |\n" "| Ada   | 30  |\n" "| Grace | 25  |\n")


def test_dumps_nested_list_of_dicts_uses_python_table_renderer() -> None:
    result = dumps([[{"name": "Ada"}, {"name": "Grace"}]])

    assert result == "| name  |\n| ----- |\n| Ada   |\n| Grace |\n"


def test_dumps_plain_list_and_dict_list_value_follow_list_paths() -> None:
    assert dumps(["Ada", "Grace"]) == "- Ada\n- Grace\n"
    assert dumps({"team": ["Ada", "Grace"]}) == "- team\n  - Ada\n  - Grace\n"


def test_dumps_nested_dict_without_table_mode_uses_headers() -> None:
    config = Config()
    config.serialize_child_dict_as_table = False

    result = dumps({"section": {"name": "Ada"}}, config=config)

    assert "# section" in result
    assert "## name" in result
    assert "Ada" in result


def test_dumps_list_of_dicts_without_table_mode_uses_nested_dict_rendering() -> None:
    config = Config()
    config.serialize_child_dict_as_table = False

    result = dumps([{"name": "Ada"}], config=config)

    assert result == "  - name : Ada\n"


def test_dumps_all_creates_config_for_default_handler() -> None:
    result = dumps_all([1 + 2j, 3 + 4j], default=lambda _value: "converted")

    assert result == "converted\n---\n\nconverted"


def test_dumps_all_sets_default_on_supplied_config() -> None:
    config = Config()

    result = dumps_all([1 + 2j], config=config, default=lambda _value: "configured")

    assert result == "configured"
    assert config.default is not None


def test_dump_all_sets_default_and_writes_separator() -> None:
    stream = io.StringIO()
    config = Config()

    dump_all([1 + 2j, 3 + 4j], stream, config=config, default=lambda _value: "value")

    assert stream.getvalue() == "value---\n\nvalue"
    assert config.default is not None


def test_dumps_uses_getstate_and_includes_python_type() -> None:
    @dataclass
    class StatefulThing:
        name: str

        def __getstate__(self) -> dict[str, str]:
            return {"name": self.name}

    config = Config()
    config.serialize_include_python_type = True

    result = dumps(StatefulThing("Ada"), config=config)

    assert "# name" in result
    assert "Ada" in result
    assert "# python_type" in result
    assert "StatefulThing" in result


def test_dump_uses_default_config_when_not_supplied() -> None:
    stream = io.StringIO()

    dump("Ada", stream)

    assert stream.getvalue() == "Ada"


def test_dumps_dataclass_uses_class_to_dict_path() -> None:
    @dataclass
    class Person:
        name: str

    result = dumps(Person("Ada"))

    assert "# name" in result
    assert "Ada" in result


def test_dumps_top_level_bytes_use_bytes_renderer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("markpickle.serialize.bytes_to_markdown", lambda _key, _value, _config: "<bytes-top>")

    assert dumps(b"abc") == "<bytes-top>"


def test_render_scalar_uses_bytes_renderer(monkeypatch: pytest.MonkeyPatch) -> None:
    builder = io.StringIO()
    monkeypatch.setattr("markpickle.serialize.bytes_to_markdown", lambda _key, _value, _config: "<bytes>")

    render_scalar(builder, b"abc", Config())

    assert builder.getvalue() == "<bytes>"


def test_render_scalar_uses_default_for_unknown_scalar() -> None:
    builder = io.StringIO()
    config = Config(default=lambda value: f"<{value}>")

    render_scalar(builder, 1 + 2j, config)

    assert builder.getvalue() == "<(1+2j)>"


def test_render_scalar_formats_date_datetime_and_none() -> None:
    config = Config()
    date_builder = io.StringIO()
    datetime_builder = io.StringIO()
    none_builder = io.StringIO()

    render_scalar(date_builder, date(2024, 1, 2), config)
    render_scalar(datetime_builder, datetime(2024, 1, 2, 3, 4, 5), config)
    render_scalar(none_builder, None, config)

    assert date_builder.getvalue() == "2024-01-02"
    assert datetime_builder.getvalue() == "2024-01-02 03:04:05"
    assert none_builder.getvalue() == "None"


def test_render_dict_returns_indent_for_none_value() -> None:
    stream = io.StringIO()

    indent = render_dict(stream, None, Config(), indent=3)

    assert indent == 3
    assert stream.getvalue() == ""
