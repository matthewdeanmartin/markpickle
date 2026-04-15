"""
Tests for file-based config loading (markpickle.config_file).
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

import markpickle
from markpickle.config_class import Config
from markpickle.config_file import (
    _apply_section,
    _extract_markpickle_section,
    load_config,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_toml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "pyproject.toml"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# load_config — pyproject.toml auto-discovery
# ---------------------------------------------------------------------------


def test_load_config_returns_default_when_no_file(tmp_path, monkeypatch):
    """When no pyproject.toml exists, returns default Config."""
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert isinstance(config, Config)
    assert config.infer_scalar_types is True  # unchanged default


def test_load_config_reads_tool_markpickle_section(tmp_path, monkeypatch):
    _write_toml(
        tmp_path,
        """
        [tool.markpickle]
        infer_scalar_types = false
        none_string = "null"
    """,
    )
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.infer_scalar_types is False
    assert config.none_string == "null"


def test_load_config_ignores_unknown_keys(tmp_path, monkeypatch):
    _write_toml(
        tmp_path,
        """
        [tool.markpickle]
        infer_scalar_types = false
        totally_made_up_key = "ignored"
    """,
    )
    monkeypatch.chdir(tmp_path)
    config = load_config()  # should not raise
    assert config.infer_scalar_types is False


def test_apply_section_returns_warning_for_unknown_key() -> None:
    warnings = _apply_section(Config(), {"totally_made_up_key": "ignored"})

    assert warnings == ["Unknown config key 'totally_made_up_key' — ignored"]


def test_apply_section_coerces_bool_and_list_values() -> None:
    config = Config()

    _apply_section(
        config,
        {
            "infer_scalar_types": "false",
            "true_values": "yes",
        },
    )

    assert config.infer_scalar_types is False
    assert config.true_values == ["yes"]


def test_apply_section_skips_default_field() -> None:
    config = Config()
    original_default = config.default

    warnings = _apply_section(config, {"default": "ignored"})

    assert warnings == []
    assert config.default == original_default


def test_load_config_empty_section_returns_defaults(tmp_path, monkeypatch):
    _write_toml(
        tmp_path,
        """
        [tool.other]
        something = 1
    """,
    )
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.infer_scalar_types is True  # default unchanged


def test_load_config_list_fields(tmp_path, monkeypatch):
    _write_toml(
        tmp_path,
        """
        [tool.markpickle]
        true_values = ["True", "true", "yes", "1"]
    """,
    )
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert "yes" in config.true_values
    assert "1" in config.true_values


def test_load_config_explicit_path(tmp_path):
    cfg_file = tmp_path / "my_config.toml"
    cfg_file.write_text(
        textwrap.dedent("""
        [tool.markpickle]
        list_bullet_style = "*"
    """),
        encoding="utf-8",
    )
    config = load_config(str(cfg_file))
    assert config.list_bullet_style == "*"


def test_load_config_explicit_path_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.toml")


def test_load_config_standalone_toml_root_keys(tmp_path):
    """Standalone config.toml with keys at root level (no section header)."""
    cfg_file = tmp_path / "markpickle.toml"
    cfg_file.write_text(
        textwrap.dedent("""
        infer_scalar_types = false
        list_bullet_style = "+"
    """),
        encoding="utf-8",
    )
    config = load_config(str(cfg_file))
    assert config.infer_scalar_types is False
    assert config.list_bullet_style == "+"


def test_extract_markpickle_section_supports_nested_markpickle_table(tmp_path):
    cfg_file = tmp_path / "markpickle.toml"
    data = {"markpickle": {"list_bullet_style": "*"}}

    section = _extract_markpickle_section(data, cfg_file)

    assert section == {"list_bullet_style": "*"}


def test_load_config_base_is_layered(tmp_path, monkeypatch):
    """Keys from file layer on top of a provided base Config."""
    _write_toml(
        tmp_path,
        """
        [tool.markpickle]
        list_bullet_style = "*"
    """,
    )
    monkeypatch.chdir(tmp_path)
    base = Config()
    base.infer_scalar_types = False
    config = load_config(base=base)
    # base value preserved
    assert config.infer_scalar_types is False
    # file value applied on top
    assert config.list_bullet_style == "*"


# ---------------------------------------------------------------------------
# Integration: config file affects actual conversion
# ---------------------------------------------------------------------------


def test_config_affects_conversion(tmp_path, monkeypatch):
    _write_toml(
        tmp_path,
        """
        [tool.markpickle]
        infer_scalar_types = false
    """,
    )
    monkeypatch.chdir(tmp_path)
    config = load_config()
    # With inference off, "42" stays a string
    result = markpickle.loads("42", config=config)
    assert result == "42"
    assert isinstance(result, str)
