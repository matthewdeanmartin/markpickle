from markpickle.gui import app as gui_app


class _DummyButton:
    def __init__(self) -> None:
        self.kwargs: dict[str, str] = {}

    def config(self, **kwargs) -> None:
        self.kwargs.update(kwargs)


class _DummyPanel:
    def __init__(self, with_activate: bool = False) -> None:
        self.lifted = False
        self.activated = False
        if with_activate:
            self.activate = self._activate

    def lift(self) -> None:
        self.lifted = True

    def _activate(self) -> None:
        self.activated = True


class _DummyVar:
    def __init__(self) -> None:
        self.value = None

    def set(self, value: str) -> None:
        self.value = value


class _DummyTheme:
    SURFACE0 = "selected"
    MANTLE = "idle"
    TEXT = "active-text"
    SUBTEXT1 = "inactive-text"


def test_launch_gui_runs_mainloop(monkeypatch) -> None:
    calls: list[str] = []

    class DummyApp:
        def mainloop(self) -> None:
            calls.append("mainloop")

    monkeypatch.setattr(gui_app, "_MarkpickleApp", DummyApp)

    gui_app.launch_gui()

    assert calls == ["mainloop"]


def test_switch_panel_updates_sidebar_and_activates_panel() -> None:
    app = gui_app._MarkpickleApp.__new__(gui_app._MarkpickleApp)
    app._theme = _DummyTheme()
    app._active_panel = _DummyVar()
    app._sidebar_buttons = {
        "Convert": _DummyButton(),
        "Help": _DummyButton(),
    }
    convert_panel = _DummyPanel()
    help_panel = _DummyPanel(with_activate=True)
    app._panels = {
        "Convert": convert_panel,
        "Help": help_panel,
    }

    gui_app._MarkpickleApp._switch_panel(app, "Help")

    assert app._sidebar_buttons["Help"].kwargs == {"bg": "selected", "fg": "active-text"}
    assert app._sidebar_buttons["Convert"].kwargs == {"bg": "idle", "fg": "inactive-text"}
    assert help_panel.lifted is True
    assert help_panel.activated is True
    assert app._active_panel.value == "Help"
