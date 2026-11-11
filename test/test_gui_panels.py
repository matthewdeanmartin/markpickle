from __future__ import annotations

import pytest

tk = pytest.importorskip("tkinter")
from pathlib import Path  # noqa: E402

from markpickle.config_class import Config  # noqa: E402
from markpickle.gui.configstate import ConfigState  # noqa: E402
from markpickle.gui.docstate import DocumentState  # noqa: E402
from markpickle.gui.panels.config_panel import (  # noqa: E402
    ConfigPanel,
    _load_config_with_source,
)
from markpickle.gui.panels.convert import ConvertPanel  # noqa: E402
from markpickle.gui.panels.doctor_panel import DoctorPanel  # noqa: E402
from markpickle.gui.panels.format_panel import FormatPanel  # noqa: E402
from markpickle.gui.panels.help_panel import HelpPanel  # noqa: E402
from markpickle.gui.panels.validate_panel import ValidatePanel  # noqa: E402


@pytest.fixture
def root():
    try:
        app = tk.Tk()
        app.withdraw()
    except tk.TclError:
        pytest.skip("No display available for tkinter")
    yield app
    app.destroy()


def _widget_text(widget: tk.Text) -> str:
    return widget.get("1.0", "end-1c")


def test_convert_panel_markdown_to_python_happy_path(root: tk.Tk) -> None:
    doc_state = DocumentState()
    panel = ConvertPanel(root, doc_state=doc_state, config_state=ConfigState(Config()))

    panel._load_text("- alpha\n- beta\n")
    panel._run()

    assert doc_state.text == "- alpha\n- beta\n"
    assert _widget_text(panel._output) == "['alpha', 'beta']"
    assert panel._status.cget("text") == "OK"


def test_convert_panel_python_to_markdown_happy_path(root: tk.Tk) -> None:
    panel = ConvertPanel(root, config_state=ConfigState(Config()))

    panel._toggle_direction()
    panel._load_text("['alpha', 'beta']")
    panel._run()

    assert panel._dir_btn.cget("text") == "Python → Markdown"
    assert "- alpha" in _widget_text(panel._output)
    assert "- beta" in _widget_text(panel._output)
    assert panel._status.cget("text") == "OK"


def test_format_panel_formats_document_on_activate(root: tk.Tk) -> None:
    doc_state = DocumentState()
    panel = FormatPanel(root, doc_state=doc_state, config_state=ConfigState(Config()))
    doc_state.set("# Title\n\n- alpha\n- beta")

    panel.activate()

    assert panel._mdformat_label.cget("text") != ""
    assert _widget_text(panel._output).strip() != ""
    assert panel._status.cget("text") == "OK"


def test_validate_panel_reports_roundtrip_safe(root: tk.Tk) -> None:
    panel = ValidatePanel(root, doc_state=DocumentState(), config_state=ConfigState(Config()))

    panel._load_text("# Title\n\nvalue\n")
    panel._run()

    output = _widget_text(panel._output)
    assert "AST Analysis" in output
    assert "No structural issues found." in output
    assert "Round-trip safe." in output
    assert panel._status.cget("text") == "All checks passed."


def test_doctor_panel_shows_environment_and_config(root: tk.Tk) -> None:
    panel = DoctorPanel(root, config_state=ConfigState(Config()))

    output = _widget_text(panel._output)
    assert "Environment Doctor" not in output
    assert "Active Config" in output
    assert "markpickle" in output
    assert "infer_scalar_types" in output


def test_help_panel_populates_cheat_sheet(root: tk.Tk) -> None:
    panel = HelpPanel(root)

    output = _widget_text(panel._text)
    assert "MARKPICKLE SYNTAX CHEAT SHEET" in output
    assert "markpickle gui" in output


def test_config_panel_roundtrip_and_state_updates(root: tk.Tk) -> None:
    doc_state = DocumentState()
    doc_state.set("# Title\n\nvalue\n")
    config_state = ConfigState(Config())
    panel = ConfigPanel(root, config=Config(), config_source="defaults", doc_state=doc_state, config_state=config_state)

    panel.activate()
    panel._vars["list_bullet_style"].set("*")
    panel._on_field_changed()

    preview = _widget_text(panel._preview_output)
    assert preview.strip() != ""
    assert panel._status.cget("text") == "Round-trip OK."
    assert config_state.config.list_bullet_style == "*"

    panel._reset_to_defaults()

    assert panel._source_label.cget("text") == "Config: defaults"
    assert panel._status.cget("text") == "Reset to built-in defaults."


def test_load_config_with_source_detects_pyproject_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.markpickle]\nlist_bullet_style = '*'\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    config, source = _load_config_with_source()

    assert config.list_bullet_style == "*"
    assert source == "pyproject.toml ([tool.markpickle], 1 key(s))"


def test_load_config_with_source_reports_defaults_without_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    config, source = _load_config_with_source()

    assert isinstance(config, Config)
    assert source == "defaults (no pyproject.toml found)"


def test_format_panel_basic_normalizer_strips_trailing_spaces_and_adds_newline(root: tk.Tk) -> None:
    panel = FormatPanel(root, config_state=ConfigState(Config()))

    assert panel._format("# Title   \n\nvalue  ") == "# Title\n\nvalue\n"


def test_format_panel_doc_state_clear_clears_output_and_status(root: tk.Tk) -> None:
    doc_state = DocumentState()
    panel = FormatPanel(root, doc_state=doc_state, config_state=ConfigState(Config()))
    panel._load_text("# Title\n")
    panel._run()
    doc_state.set("")

    assert _widget_text(panel._input) == ""
    assert _widget_text(panel._output) == ""
    assert panel._status.cget("text") == ""


def test_validate_panel_flags_unsafe_inline_markdown(root: tk.Tk) -> None:
    panel = ValidatePanel(root, doc_state=DocumentState(), config_state=ConfigState(Config()))

    panel._load_text("# Title\n\nA **bold** value.\n")
    panel._run()
    output = _widget_text(panel._output)

    assert "strong formatting" in output
    assert panel._status.cget("text") != "All checks passed."


def test_validate_panel_empty_input_requests_markdown(root: tk.Tk) -> None:
    panel = ValidatePanel(root, doc_state=DocumentState(), config_state=ConfigState(Config()))

    panel._run()

    assert "No input provided." in _widget_text(panel._output)


def test_config_panel_empty_roundtrip_sets_guidance_status(root: tk.Tk) -> None:
    panel = ConfigPanel(root, config=Config(), doc_state=DocumentState(), config_state=ConfigState(Config()))

    panel._test_roundtrip()

    assert panel._status.cget("text") == "No markdown in input area — load a doc first."


def test_config_panel_list_values_are_trimmed_and_empty_items_removed(root: tk.Tk) -> None:
    panel = ConfigPanel(root, config=Config(), config_state=ConfigState(Config()))
    panel._vars["true_values"].set(" yes, , y ")

    assert panel._get_config().true_values == ["yes", "y"]


def test_convert_panel_invalid_python_expression_is_reported(root: tk.Tk) -> None:
    panel = ConvertPanel(root, config_state=ConfigState(Config()))
    panel._toggle_direction()
    panel._load_text("not valid python !!!")
    panel._run()

    assert _widget_text(panel._output).startswith("Error:")
    assert panel._status.cget("text").startswith("Error:")


def test_convert_panel_clear_resets_shared_document_and_output(root: tk.Tk) -> None:
    doc_state = DocumentState()
    panel = ConvertPanel(root, doc_state=doc_state, config_state=ConfigState(Config()))
    panel._load_text("# Title\n")
    panel._run()
    panel._clear()

    assert doc_state.text == ""
    assert _widget_text(panel._input) == ""
    assert _widget_text(panel._output) == ""
    assert panel._status.cget("text") == ""


def test_convert_panel_copy_output_updates_status(root: tk.Tk, monkeypatch: pytest.MonkeyPatch) -> None:
    panel = ConvertPanel(root, config_state=ConfigState(Config()))
    panel._set_output("copied text")
    copied: list[str] = []
    monkeypatch.setattr(panel, "clipboard_clear", lambda: None)
    monkeypatch.setattr(panel, "clipboard_append", copied.append)

    panel._copy_output()

    assert copied == ["copied text"]
    assert panel._status.cget("text") == "Copied to clipboard."


def test_validate_panel_can_run_ast_only(root: tk.Tk) -> None:
    panel = ValidatePanel(root, doc_state=DocumentState(), config_state=ConfigState(Config()))
    panel._roundtrip_var.set(False)
    panel._load_text("# Title\n\nA **bold** value.\n")

    panel._run()

    assert "AST Analysis" in _widget_text(panel._output)
    assert "Round-trip Check" not in _widget_text(panel._output)
    assert panel._status.cget("text") == "Issues found."


def test_validate_panel_clear_updates_shared_document_and_status(root: tk.Tk) -> None:
    doc_state = DocumentState()
    panel = ValidatePanel(root, doc_state=doc_state, config_state=ConfigState(Config()))
    panel._load_text("# Title\n")
    panel._run()
    panel._clear()

    assert doc_state.text == ""
    assert _widget_text(panel._input) == ""
    assert _widget_text(panel._output) == ""
    assert panel._status.cget("text") == ""
