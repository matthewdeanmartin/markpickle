"""
Tkinter GUI for markpickle.

Run with:
    markpickle gui
    markpickle-gui
"""

from __future__ import annotations


def launch_gui() -> None:
    """Launch the markpickle tkinter GUI."""
    try:
        import tkinter as tk  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "tkinter is not available in this Python installation. "
            "On Linux, install it with your package manager (e.g. python3-tk)."
        ) from exc

    app = _MarkpickleApp()
    app.mainloop()


# ---------------------------------------------------------------------------
# Internal — only imported when GUI is launched
# ---------------------------------------------------------------------------


class _MarkpickleApp:
    """Main application window."""

    _PANEL_NAMES = ["Convert", "Format", "Validate", "Config", "Doctor", "Help"]

    def __init__(self):
        import tkinter as tk

        from markpickle.gui import theme as T

        self._root = tk.Tk()
        self._root.title("markpickle")
        self._root.geometry("1100x700")
        self._root.minsize(700, 480)
        self._root.configure(bg=T.BASE)
        self._root.option_add("*tearOff", False)

        self._T = T
        self._tk = tk
        self._active_panel = tk.StringVar(value="Convert")
        self._panels: dict[str, tk.Frame] = {}
        self._sidebar_buttons: dict[str, tk.Button] = {}

        self._build()
        self._switch_panel("Convert")

    def mainloop(self):
        self._root.mainloop()

    # ------------------------------------------------------------------
    def _build(self):
        tk = self._tk
        T = self._T

        outer = tk.Frame(self._root, bg=T.CRUST)
        outer.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(outer, bg=T.MANTLE, width=140)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = tk.Frame(sidebar, bg=T.MANTLE)
        logo_frame.pack(fill="x", pady=(16, 8))
        tk.Label(
            logo_frame, text="mark\npickle", bg=T.MANTLE, fg=T.BLUE, font=("Consolas", 14, "bold"), justify="center"
        ).pack()
        tk.Frame(sidebar, bg=T.SURFACE2, height=1).pack(fill="x", padx=12, pady=(4, 12))

        for name in self._PANEL_NAMES:
            btn = tk.Button(
                sidebar,
                text=name,
                command=lambda n=name: self._switch_panel(n),
                bg=T.MANTLE,
                fg=T.SUBTEXT1,
                activebackground=T.SURFACE0,
                activeforeground=T.TEXT,
                relief="flat",
                font=T.FONT_UI,
                padx=12,
                pady=8,
                anchor="w",
                cursor="hand2",
                bd=0,
                width=14,
            )
            btn.pack(fill="x", padx=6, pady=2)
            self._sidebar_buttons[name] = btn

        tk.Frame(sidebar, bg=T.SURFACE2, height=1).pack(fill="x", padx=12, side="bottom", pady=(0, 4))
        try:
            import importlib.metadata

            ver = importlib.metadata.version("markpickle")
        except Exception:
            ver = "dev"
        tk.Label(sidebar, text=f"v{ver}", bg=T.MANTLE, fg=T.OVERLAY0, font=T.FONT_SMALL).pack(
            side="bottom", pady=(0, 6)
        )

        # Content area
        self._content = tk.Frame(outer, bg=T.BASE)
        self._content.pack(side="left", fill="both", expand=True)

        # Shared state objects
        from markpickle.gui.configstate import ConfigState
        from markpickle.gui.docstate import DocumentState
        from markpickle.gui.panels.config_panel import _load_config_with_source

        doc_state = DocumentState()
        active_config, config_source = _load_config_with_source()
        config_state = ConfigState(active_config)

        # Build panels
        from markpickle.gui.panels.config_panel import ConfigPanel
        from markpickle.gui.panels.convert import ConvertPanel
        from markpickle.gui.panels.doctor_panel import DoctorPanel
        from markpickle.gui.panels.format_panel import FormatPanel
        from markpickle.gui.panels.help_panel import HelpPanel
        from markpickle.gui.panels.validate_panel import ValidatePanel

        panels = {
            "Convert": ConvertPanel(self._content, doc_state=doc_state, config_state=config_state),
            "Format": FormatPanel(self._content, doc_state=doc_state, config_state=config_state),
            "Validate": ValidatePanel(self._content, doc_state=doc_state, config_state=config_state),
            "Config": ConfigPanel(
                self._content,
                config=active_config,
                config_source=config_source,
                doc_state=doc_state,
                config_state=config_state,
            ),
            "Doctor": DoctorPanel(self._content, config_state=config_state),
            "Help": HelpPanel(self._content),
        }
        for name, panel in panels.items():
            panel.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._panels[name] = panel

    # ------------------------------------------------------------------
    def _switch_panel(self, name: str):
        T = self._T
        for btn_name, btn in self._sidebar_buttons.items():
            btn.config(bg=T.SURFACE0 if btn_name == name else T.MANTLE, fg=T.TEXT if btn_name == name else T.SUBTEXT1)

        panel = self._panels[name]
        panel.lift()
        self._active_panel.set(name)

        if hasattr(panel, "activate"):
            panel.activate()
