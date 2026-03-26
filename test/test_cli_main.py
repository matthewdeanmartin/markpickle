import io
import importlib.metadata
import json
import sys
import types
from argparse import Namespace
from unittest.mock import patch
from pathlib import Path

import pytest

import markpickle
from markpickle import __main__ as cli


def test_run_without_subcommand_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    return_code = cli.run([])

    captured = capsys.readouterr()
    assert return_code == 0
    assert "usage: markpickle" in captured.out
    assert captured.err == ""


def test_convert_file_to_stdout(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    infile = tmp_path / "items.md"
    markdown = "- a\n- b\n"
    infile.write_text(markdown, encoding="utf-8")

    return_code = cli.run(["convert", str(infile)])

    captured = capsys.readouterr()
    expected = json.dumps(markpickle.loads(markdown), default=str, indent=2) + "\n"
    assert return_code == 0
    assert captured.out == expected
    assert captured.err == ""


def test_convert_stdin_to_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    outfile = tmp_path / "items.json"
    markdown = "- alpha\n- beta\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO(markdown))

    return_code = cli.run(["convert", "-", str(outfile)])

    captured = capsys.readouterr()
    assert return_code == 0
    assert outfile.read_text(encoding="utf-8") == json.dumps(markpickle.loads(markdown), default=str, indent=2) + "\n"
    assert captured.out == f"Written to {outfile}\n"
    assert captured.err == ""


def test_convert_missing_file_returns_error(capsys: pytest.CaptureFixture[str]) -> None:
    return_code = cli.run(["convert", "missing.md"])

    captured = capsys.readouterr()
    assert return_code == 1
    assert captured.out == ""
    assert "error: file not found: missing.md" in captured.err


def test_convert_value_error_returns_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    infile = tmp_path / "items.md"
    infile.write_text("- a\n", encoding="utf-8")

    def _raise_value_error(*_args, **_kwargs):
        raise ValueError("bad markdown")

    monkeypatch.setattr("markpickle.deserialize.load", _raise_value_error)

    return_code = cli.run(["convert", str(infile)])

    captured = capsys.readouterr()
    assert return_code == 1
    assert captured.out == ""
    assert "error: bad markdown" in captured.err


def test_convert_invalid_config_exits(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    infile = tmp_path / "items.md"
    infile.write_text("- a\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        cli.run(["convert", str(infile), "--config", str(tmp_path / "missing.toml")])

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert "error loading config:" in captured.err


def test_validate_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    infile = tmp_path / "doc.md"
    infile.write_text("# Title\n\nvalue\n", encoding="utf-8")

    return_code = cli.run(["validate", str(infile)])

    captured = capsys.readouterr()
    assert return_code == 0
    assert captured.out.startswith(f"OK    {infile}")
    assert captured.err == ""


def test_validate_missing_file_returns_error(capsys: pytest.CaptureFixture[str]) -> None:
    return_code = cli.run(["validate", "missing.md"])

    captured = capsys.readouterr()
    assert return_code == 1
    assert captured.out == ""
    assert "error: file not found: missing.md" in captured.err


def test_validate_reports_ast_issue(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    infile = tmp_path / "doc.md"
    infile.write_text("# Title\n\nSee [docs](https://example.com)\n", encoding="utf-8")

    return_code = cli.run(["validate", str(infile)])

    captured = capsys.readouterr()
    assert return_code == 1
    assert captured.out.startswith(f"FAIL  {infile}")
    assert "link found in paragraph" in captured.out
    assert captured.err == ""


def test_validate_reports_parse_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    infile = tmp_path / "doc.md"
    infile.write_text("# Title\n\nvalue\n", encoding="utf-8")

    def _raise_runtime_error(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(markpickle, "loads", _raise_runtime_error)

    return_code = cli.run(["validate", str(infile), "--no-ast"])

    captured = capsys.readouterr()
    assert return_code == 1
    assert captured.out.startswith(f"FAIL  {infile}")
    assert "Parse error: boom" in captured.out
    assert captured.err == ""


def test_validate_reports_unsupported_construct(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    infile = tmp_path / "doc.md"
    infile.write_text("# Title\n\nvalue\n", encoding="utf-8")

    def _raise_not_implemented(*_args, **_kwargs):
        raise NotImplementedError("tables")

    monkeypatch.setattr("markpickle.validate.validate_markdown", _raise_not_implemented)

    return_code = cli.run(["validate", str(infile), "--no-roundtrip"])

    captured = capsys.readouterr()
    assert return_code == 1
    assert captured.out.startswith(f"FAIL  {infile}")
    assert "Unsupported construct: tables" in captured.out
    assert captured.err == ""


def test_doctor_reports_pyproject_without_markpickle_section(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.other]\nvalue = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    return_code = cli.run(["doctor"])

    captured = capsys.readouterr()
    assert return_code == 0
    assert f"Config: {tmp_path / 'pyproject.toml'} (no [tool.markpickle] section)" in captured.out


def test_doctor_prints_diagnostics(capsys: pytest.CaptureFixture[str]) -> None:
    return_code = cli.run(["doctor"])

    captured = capsys.readouterr()
    assert return_code == 0
    assert "Package" in captured.out
    assert "tkinter" in captured.out
    assert captured.err == ""


def test_version_returns_not_installed_for_missing_package(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_missing(_pkg: str) -> str:
        raise importlib.metadata.PackageNotFoundError

    monkeypatch.setattr(importlib.metadata, "version", _raise_missing)

    assert cli._version("definitely-missing") == "NOT INSTALLED"


def test_tkinter_status_handles_import_error() -> None:
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "tkinter":
            raise ImportError("missing tkinter")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        assert cli._tkinter_status() == "NOT AVAILABLE (missing from this Python build)"


def test_load_config_exits_on_import_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def _raise_import_error(_path):
        raise ImportError("tomli missing")

    monkeypatch.setattr("markpickle.config_file.load_config", _raise_import_error)

    with pytest.raises(SystemExit) as exc_info:
        cli._load_config(Namespace(config="anything.toml"))

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert "error loading config: tomli missing" in captured.err


def test_gui_subcommand_dispatches_to_launch_gui(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    fake_module = types.SimpleNamespace(launch_gui=lambda: calls.append("launched"))

    monkeypatch.setitem(sys.modules, "markpickle.gui.app", fake_module)

    return_code = cli.run(["gui"])

    assert return_code == 0
    assert calls == ["launched"]


def test_gui_subcommand_reports_import_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "markpickle.gui.app":
            raise ImportError("tk unavailable")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        return_code = cli.run(["gui"])

    captured = capsys.readouterr()
    assert return_code == 1
    assert "error: could not launch GUI: tk unavailable" in captured.err
    assert "Make sure tkinter is available" in captured.err
