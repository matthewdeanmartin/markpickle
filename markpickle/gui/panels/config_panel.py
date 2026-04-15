"""
Config panel — view and edit Config options, see their effect live.

Holds a ConfigState that it pushes to whenever any field changes.
Other panels subscribe to ConfigState to use the current config.
"""

from __future__ import annotations

import tkinter as tk

from markpickle.config_class import Config
from markpickle.gui import theme as T

_EDITABLE_FIELDS = [
    "infer_scalar_types",
    "none_string",
    "true_values",
    "false_values",
    "none_values",
    "list_bullet_style",
    "serialize_dict_as_table",
    "serialize_child_dict_as_table",
    "serialize_tuples_as_ordered_lists",
    "ordered_list_as_tuple",
    "serialize_date_format",
    "serialized_datetime_format",
    "tables_become_list_of_lists",
    "deserialized_add_missing_key",
    "deserialized_missing_key_name",
    "serialize_force_final_newline",
]


class ConfigPanel(tk.Frame):
    """
    Live Config Editor panel.
    Allows viewing and editing markpickle Config options, and seeing their effect
    on a markdown document in real-time.
    """

    def __init__(
        self,
        parent,
        config: Config | None = None,
        config_source: str = "defaults",
        doc_state=None,
        config_state=None,
        **kw,
    ):  # pylint: disable=too-many-positional-arguments
        super().__init__(parent, **T.frame_kw(), **kw)
        self._active_config: Config = config if config is not None else Config()
        self._config_source: str = config_source
        self._doc_state = doc_state
        self._config_state = config_state
        self._vars: dict[str, tk.Variable] = {}
        self._build()
        if doc_state is not None:
            doc_state.register(self._on_doc_changed)

    # ------------------------------------------------------------------
    def activate(self):
        """Called when this panel becomes active."""
        if self._doc_state is not None and self._doc_state.text.strip():
            self._test_roundtrip_with_md(self._doc_state.text)

    def _on_doc_changed(self, text: str):
        current = self._md_input.get("1.0", "end-1c")
        if current == text:
            return
        self._md_input.delete("1.0", "end")
        if text:
            self._md_input.insert("1.0", text)
        else:
            # doc was cleared — clear the output too
            self._set_preview_output("")
            self._status.config(text="", fg=T.OVERLAY0)

    # ------------------------------------------------------------------
    def _build(self):
        top = tk.Frame(self, **T.frame_kw())
        top.pack(fill="x", padx=10, pady=(10, 4))

        tk.Label(top, text="Live Config Editor", **T.heading_kw()).pack(side="left")

        self._source_label = tk.Label(
            top, text=f"Config: {self._config_source}", bg=T.BASE, fg=T.OVERLAY2, font=T.FONT_SMALL
        )
        self._source_label.pack(side="left", padx=(12, 0))

        reload_btn = tk.Button(top, text="Reload Config", command=self._reload_config, **T.small_button_kw())
        reload_btn.pack(side="right")

        reset_btn = tk.Button(top, text="Reset to Defaults", command=self._reset_to_defaults, **T.small_button_kw())
        reset_btn.pack(side="right", padx=(0, 6))

        test_btn = tk.Button(
            top,
            text="Test Round-trip",
            command=self._test_roundtrip,
            bg=T.BLUE,
            fg=T.BASE,
            activebackground=T.LAVENDER,
            activeforeground=T.BASE,
            relief="flat",
            font=T.FONT_UI_BOLD,
            padx=10,
            pady=3,
            cursor="hand2",
            bd=0,
        )
        test_btn.pack(side="right", padx=(0, 6))

        pane = tk.PanedWindow(self, orient="horizontal", bg=T.CRUST, sashwidth=4, sashrelief="flat", sashpad=2)
        pane.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Left: scrollable field list
        left_outer = tk.Frame(pane, **T.frame_kw())
        canvas = tk.Canvas(left_outer, bg=T.BASE, highlightthickness=0)
        vsb = tk.Scrollbar(
            left_outer, orient="vertical", command=canvas.yview, bg=T.SURFACE1, troughcolor=T.SURFACE0, relief="flat"
        )
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._fields_frame = tk.Frame(canvas, **T.frame_kw())
        canvas_window = canvas.create_window((0, 0), window=self._fields_frame, anchor="nw")

        def _on_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())

        self._fields_frame.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_configure)

        # Right: markdown input + preview output
        right_frame = tk.Frame(pane, **T.frame_kw())
        tk.Label(right_frame, text="Markdown input (from shared doc or paste here)", **T.label_kw()).pack(
            anchor="w", padx=4, pady=(4, 2)
        )
        self._md_input = tk.Text(right_frame, **T.text_area_kw(), height=8, wrap="none", undo=True)
        md_vsb = tk.Scrollbar(
            right_frame,
            orient="vertical",
            command=self._md_input.yview,
            bg=T.SURFACE1,
            troughcolor=T.SURFACE0,
            relief="flat",
        )
        self._md_input.configure(yscrollcommand=md_vsb.set)
        md_vsb.pack(side="right", fill="y")
        self._md_input.pack(fill="x", padx=(4, 0), pady=(0, 4))

        tk.Label(right_frame, text="Deserialised → re-serialised with this config", **T.label_kw()).pack(
            anchor="w", padx=4, pady=(4, 2)
        )
        self._preview_output = tk.Text(right_frame, **T.text_area_kw(), wrap="none", state="disabled")
        pv_vsb = tk.Scrollbar(
            right_frame,
            orient="vertical",
            command=self._preview_output.yview,
            bg=T.SURFACE1,
            troughcolor=T.SURFACE0,
            relief="flat",
        )
        self._preview_output.configure(yscrollcommand=pv_vsb.set)
        pv_vsb.pack(side="right", fill="y")
        self._preview_output.pack(fill="both", expand=True, padx=(4, 0), pady=(0, 4))

        pane.add(left_outer, minsize=260)
        pane.add(right_frame, minsize=200)

        self._status = tk.Label(self, text="", bg=T.BASE, fg=T.OVERLAY0, font=T.FONT_SMALL, anchor="w")
        self._status.pack(fill="x", padx=12, pady=(0, 4))

        self._populate_fields(self._active_config)

        if self._doc_state is not None and self._doc_state.text.strip():
            self._md_input.insert("1.0", self._doc_state.text)

    # ------------------------------------------------------------------
    def _populate_fields(self, cfg: Config):
        for widget in self._fields_frame.winfo_children():
            widget.destroy()
        self._vars.clear()

        for i, field_name in enumerate(_EDITABLE_FIELDS):
            field_value = getattr(cfg, field_name)
            var: tk.Variable
            row = tk.Frame(self._fields_frame, bg=T.BASE if i % 2 == 0 else T.SURFACE0)
            row.pack(fill="x", padx=4, pady=1)

            tk.Label(row, text=field_name, bg=row["bg"], fg=T.SUBTEXT1, font=T.FONT_SMALL, width=32, anchor="w").pack(
                side="left", padx=(4, 8)
            )

            if isinstance(field_value, bool):
                var = tk.BooleanVar(value=field_value)
                cb = tk.Checkbutton(
                    row,
                    variable=var,
                    bg=row["bg"],
                    fg=T.TEXT,
                    selectcolor=T.SURFACE1,
                    activebackground=row["bg"],
                    activeforeground=T.TEXT,
                    command=self._on_field_changed,
                )
                cb.pack(side="left")
            elif isinstance(field_value, list):
                var = tk.StringVar(value=", ".join(str(v) for v in field_value))
                var.trace_add("write", lambda *_: self._on_field_changed())
                tk.Entry(
                    row,
                    textvariable=var,
                    bg=T.SURFACE1,
                    fg=T.TEXT,
                    insertbackground=T.TEXT,
                    relief="flat",
                    font=T.FONT_SMALL,
                    width=28,
                ).pack(side="left", padx=(0, 4))
            else:
                var = tk.StringVar(value=str(field_value))
                var.trace_add("write", lambda *_: self._on_field_changed())
                tk.Entry(
                    row,
                    textvariable=var,
                    bg=T.SURFACE1,
                    fg=T.TEXT,
                    insertbackground=T.TEXT,
                    relief="flat",
                    font=T.FONT_SMALL,
                    width=28,
                ).pack(side="left", padx=(0, 4))

            self._vars[field_name] = var

    def _on_field_changed(self):
        """Push updated config to ConfigState whenever any field changes."""
        if self._config_state is not None:
            self._config_state.set(self._get_config())

    def _get_config(self) -> Config:
        defaults = Config()
        cfg = Config()
        for field_name, var in self._vars.items():
            default_val = getattr(defaults, field_name)
            raw = var.get()
            try:
                if isinstance(default_val, bool):
                    setattr(cfg, field_name, bool(raw))
                elif isinstance(default_val, list):
                    parts = [p.strip() for p in str(raw).split(",") if p.strip()]
                    setattr(cfg, field_name, parts)
                elif isinstance(default_val, str):
                    setattr(cfg, field_name, str(raw))
            except (ValueError, TypeError):
                pass
        return cfg

    # ------------------------------------------------------------------
    def _test_roundtrip(self):
        text = self._md_input.get("1.0", "end-1c").strip()
        if not text:
            self._status.config(text="No markdown in input area — load a doc first.", fg=T.YELLOW)
            return
        self._test_roundtrip_with_md(text)

    def _test_roundtrip_with_md(self, md_text: str):
        import markpickle  # pylint: disable=import-outside-toplevel

        try:
            cfg = self._get_config()
            obj = markpickle.loads(md_text, config=cfg)
            out = markpickle.dumps(obj, config=cfg)
            self._set_preview_output(out)
            self._status.config(text="Round-trip OK.", fg=T.GREEN)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._set_preview_output(f"Error: {exc}")
            self._status.config(text=f"Error: {exc}", fg=T.RED)

    def _reload_config(self):
        try:
            cfg, source = _load_config_with_source()
            self._active_config = cfg
            self._config_source = source
            self._source_label.config(text=f"Config: {source}")
            self._populate_fields(cfg)
            if self._config_state is not None:
                self._config_state.set(cfg)
            self._status.config(text=f"Reloaded: {source}", fg=T.GREEN)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._status.config(text=f"Reload error: {exc}", fg=T.RED)

    def _reset_to_defaults(self):
        cfg = Config()
        self._populate_fields(cfg)
        self._config_source = "defaults"
        self._source_label.config(text="Config: defaults")
        if self._config_state is not None:
            self._config_state.set(cfg)
        self._status.config(text="Reset to built-in defaults.", fg=T.GREEN)

    def _set_preview_output(self, text: str):
        self._preview_output.config(state="normal")
        self._preview_output.delete("1.0", "end")
        self._preview_output.insert("1.0", text)
        self._preview_output.config(state="disabled")


# ---------------------------------------------------------------------------
# Helper used here and by app.py at startup
# ---------------------------------------------------------------------------


def _load_config_with_source() -> tuple[Config, str]:
    from pathlib import Path  # pylint: disable=import-outside-toplevel

    try:
        from markpickle.config_file import (
            load_config,  # pylint: disable=import-outside-toplevel
        )

        cfg = load_config()
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
                    return cfg, f"pyproject.toml ([tool.markpickle], {len(section)} key(s))"
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            return cfg, "pyproject.toml (no [tool.markpickle] section — defaults)"
        return cfg, "defaults (no pyproject.toml found)"
    except Exception:  # pylint: disable=broad-exception-caught
        return Config(), "defaults"
