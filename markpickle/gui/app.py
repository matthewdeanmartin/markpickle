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
        import tkinter as tk  # pylint: disable=unused-import,import-outside-toplevel
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
        import tkinter as tk  # pylint: disable=import-outside-toplevel

        from markpickle.gui import (
            theme as theme_mod,  # pylint: disable=import-outside-toplevel
        )

        self._root = tk.Tk()
        self._root.title("markpickle")
        self._root.geometry("1100x700")
        self._root.minsize(700, 480)
        self._root.configure(bg=theme_mod.BASE)
        self._root.option_add("*tearOff", False)

        self._theme = theme_mod
        self._tk = tk
        self._active_panel = tk.StringVar(value="Convert")
        self._panels: dict[str, tk.Frame] = {}
        self._sidebar_buttons: dict[str, tk.Button] = {}

        self._build()
        self._switch_panel("Convert")

    def mainloop(self):
        """Run the application main loop."""
        self._root.mainloop()

    # ------------------------------------------------------------------
    def _build(self):
        """Build the application UI."""
        tk_ = self._tk
        theme = self._theme

        outer = tk_.Frame(self._root, bg=theme.CRUST)
        outer.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk_.Frame(outer, bg=theme.MANTLE, width=140)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = tk_.Frame(sidebar, bg=theme.MANTLE)
        logo_frame.pack(fill="x", pady=(16, 8))
        tk_.Label(
            logo_frame,
            text="mark\npickle",
            bg=theme.MANTLE,
            fg=theme.BLUE,
            font=("Consolas", 14, "bold"),
            justify="center",
        ).pack()
        tk_.Frame(sidebar, bg=theme.SURFACE2, height=1).pack(fill="x", padx=12, pady=(4, 12))

        for name in self._PANEL_NAMES:
            btn = tk_.Button(
                sidebar,
                text=name,
                command=lambda n=name: self._switch_panel(n),
                bg=theme.MANTLE,
                fg=theme.SUBTEXT1,
                activebackground=theme.SURFACE0,
                activeforeground=theme.TEXT,
                relief="flat",
                font=theme.FONT_UI,
                padx=12,
                pady=8,
                anchor="w",
                cursor="hand2",
                bd=0,
                width=14,
            )
            btn.pack(fill="x", padx=6, pady=2)
            self._sidebar_buttons[name] = btn

        tk_.Frame(sidebar, bg=theme.SURFACE2, height=1).pack(fill="x", padx=12, side="bottom", pady=(0, 4))
        try:
            import importlib.metadata  # pylint: disable=import-outside-toplevel

            ver = importlib.metadata.version("markpickle")
        except Exception:  # pylint: disable=broad-exception-caught
            ver = "dev"
        tk_.Label(sidebar, text=f"v{ver}", bg=theme.MANTLE, fg=theme.OVERLAY0, font=theme.FONT_SMALL).pack(
            side="bottom", pady=(0, 6)
        )

        # Content area
        self._content = tk_.Frame(outer, bg=theme.BASE)
        self._content.pack(side="left", fill="both", expand=True)

        # Shared state objects
        from markpickle.gui.configstate import (
            ConfigState,  # pylint: disable=import-outside-toplevel
        )
        from markpickle.gui.docstate import (
            DocumentState,  # pylint: disable=import-outside-toplevel
        )
        from markpickle.gui.panels.config_panel import (
            _load_config_with_source,  # pylint: disable=import-outside-toplevel
        )

        doc_state = DocumentState()
        active_config, config_source = _load_config_with_source()
        config_state = ConfigState(active_config)

        # Build panels
        from markpickle.gui.panels.config_panel import (
            ConfigPanel,  # pylint: disable=import-outside-toplevel
        )
        from markpickle.gui.panels.convert import (
            ConvertPanel,  # pylint: disable=import-outside-toplevel
        )
        from markpickle.gui.panels.doctor_panel import (
            DoctorPanel,  # pylint: disable=import-outside-toplevel
        )
        from markpickle.gui.panels.format_panel import (
            FormatPanel,  # pylint: disable=import-outside-toplevel
        )
        from markpickle.gui.panels.help_panel import (
            HelpPanel,  # pylint: disable=import-outside-toplevel
        )
        from markpickle.gui.panels.validate_panel import (
            ValidatePanel,  # pylint: disable=import-outside-toplevel
        )

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
        """Switch the active panel."""
        theme = self._theme
        for btn_name, btn in self._sidebar_buttons.items():
            btn.config(
                bg=theme.SURFACE0 if btn_name == name else theme.MANTLE,
                fg=theme.TEXT if btn_name == name else theme.SUBTEXT1,
            )

        panel = self._panels[name]
        panel.lift()
        self._active_panel.set(name)

        if hasattr(panel, "activate"):
            panel.activate()
