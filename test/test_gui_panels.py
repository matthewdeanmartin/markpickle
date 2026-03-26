from __future__ import annotations
import pytest

tk = pytest.importorskip("tkinter")
from pathlib import Path

from markpickle.config_class import Config
from markpickle.gui.configstate import ConfigState
from markpickle.gui.docstate import DocumentState
from markpickle.gui.panels.config_panel import ConfigPanel, _load_config_with_source
from markpickle.gui.panels.convert import ConvertPanel
from markpickle.gui.panels.doctor_panel import DoctorPanel
from markpickle.gui.panels.format_panel import FormatPanel
from markpickle.gui.panels.help_panel import HelpPanel
from markpickle.gui.panels.validate_panel import ValidatePanel


@pytest.fixture()
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
