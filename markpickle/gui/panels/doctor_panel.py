"""
Doctor panel — environment info, active config dump, copy-to-clipboard.
"""

import importlib.metadata
import platform
import tkinter as tk

from markpickle.gui import theme as T


def _version(pkg: str) -> str:
    try:
        return importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError:
        return "NOT INSTALLED"


def _tkinter_status() -> str:
    """Check if tkinter is available."""
    try:
        # We already imported it at top level as tk
        return f"available (version {tk.TkVersion})"
    except Exception:  # pylint: disable=broad-exception-caught
        return "NOT AVAILABLE"


class DoctorPanel(tk.Frame):
    """
    Panel for diagnostics and showing environment information.
    """

    def __init__(self, parent, config_state=None, **kw):
        super().__init__(parent, **T.frame_kw(), **kw)
        self._config_state = config_state
        self._build()
        if config_state is not None:
            config_state.register(lambda _cfg: self._refresh())

    def activate(self):
        """Refresh when switched to so config is always current."""
        self._refresh()

    def _build(self):
        top = tk.Frame(self, **T.frame_kw())
        top.pack(fill="x", padx=10, pady=(10, 4))

        tk.Label(top, text="Environment Doctor", **T.heading_kw()).pack(side="left")

        copy_btn = tk.Button(top, text="Copy to Clipboard", command=self._copy, **T.small_button_kw())
        copy_btn.pack(side="right")

        refresh_btn = tk.Button(top, text="Refresh", command=self._refresh, **T.small_button_kw())
        refresh_btn.pack(side="right", padx=(0, 6))

        self._output = tk.Text(self, **T.text_area_kw(), wrap="none", state="disabled")
        self._output.tag_config("ok", foreground=T.GREEN)
        self._output.tag_config("bad", foreground=T.RED)
        self._output.tag_config("heading", foreground=T.MAUVE, font=T.FONT_UI_BOLD)
        self._output.tag_config("sep", foreground=T.SURFACE2)
        self._output.tag_config("hint", foreground=T.OVERLAY2, font=T.FONT_SMALL)
        self._output.tag_config("key", foreground=T.BLUE)
        self._output.tag_config("val", foreground=T.TEXT)

        vsb = tk.Scrollbar(
            self, orient="vertical", command=self._output.yview, bg=T.SURFACE1, troughcolor=T.SURFACE0, relief="flat"
        )
        self._output.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", padx=(0, 10), pady=(0, 10))
        self._output.pack(fill="both", expand=True, padx=(10, 0), pady=(0, 10))

        self._refresh()

    # ------------------------------------------------------------------
    def _refresh(self):
        mp_ver = _version("markpickle")
        rows = [
            ("markpickle", mp_ver),
            ("Python", platform.python_version()),
            ("mistune", _version("mistune")),
            ("tabulate [tables]", _version("tabulate")),
            ("Pillow [images]", _version("pillow")),
            ("mdformat [format]", _version("mdformat")),
            ("tkinter", _tkinter_status()),
        ]

        self._output.config(state="normal")
        self._output.delete("1.0", "end")

        sep = "─" * 52 + "\n"

        # --- Packages ---
        self._output.insert("end", sep, "sep")
        self._output.insert("end", f"{'Package':<28}{'Version / Status'}\n", "heading")
        self._output.insert("end", sep, "sep")

        for name, status in rows:
            ok = status not in ("NOT INSTALLED", "NOT AVAILABLE")
            marker = " ok " if ok else " !! "
            tag = "ok" if ok else "bad"
            self._output.insert("end", f"[{marker}] {name:<24}{status}\n", tag)

        self._output.insert("end", sep, "sep")

        # --- Config file source ---
        from pathlib import Path  # pylint: disable=import-outside-toplevel

        pyproject = Path.cwd() / "pyproject.toml"
        if pyproject.exists():
            try:
                from markpickle.config_file import (  # pylint: disable=import-outside-toplevel
                    _extract_markpickle_section,
                    _read_toml,
                )

                data = _read_toml(pyproject)
                section = _extract_markpickle_section(data, pyproject)
                if section:
                    self._output.insert(
                        "end", f"\nConfig file: {pyproject}\n  [tool.markpickle] — {len(section)} key(s) loaded\n", "ok"
                    )
                else:
                    self._output.insert(
                        "end",
                        f"\nConfig file: {pyproject}\n  (no [tool.markpickle] section — using defaults)\n",
                        "hint",
                    )
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        else:
            self._output.insert("end", "\nConfig file: none found (using defaults)\n", "hint")

        # --- Active config values ---
        self._output.insert("end", "\n")
        self._output.insert("end", sep, "sep")
        self._output.insert("end", f"{'Active Config':<28}{'Value'}\n", "heading")
        self._output.insert("end", sep, "sep")

        from markpickle.config_class import (
            Config,  # pylint: disable=import-outside-toplevel
        )

        cfg = self._config_state.config if self._config_state is not None else Config()
        import dataclasses  # pylint: disable=import-outside-toplevel

        for field in dataclasses.fields(cfg):
            val = getattr(cfg, field.name)
            # skip non-serialisable fields (callables)
            if callable(val):
                continue
            self._output.insert("end", f"  {field.name:<34}", "key")
            self._output.insert("end", f"{val!r}\n", "val")

        self._output.insert("end", sep, "sep")
        self._output.insert("end", "\nTo install all optional extras:\n  pip install markpickle[all]\n", "hint")
        self._output.config(state="disabled")

    def _copy(self):
        text = self._output.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
