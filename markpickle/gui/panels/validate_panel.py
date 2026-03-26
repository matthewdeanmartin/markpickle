"""
Validate panel — paste markdown, see round-trip analysis report.
Auto-runs when activated if a doc is in shared state.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog

from markpickle.gui import theme as T


class ValidatePanel(tk.Frame):
    """
    Panel for validating markdown round-trip and AST analysis.
    """

    def __init__(self, parent, doc_state=None, config_state=None, **kw):
        super().__init__(parent, **T.frame_kw(), **kw)
        self._doc_state = doc_state
        self._config_state = config_state
        self._updating_from_state = False
        self._build()
        if doc_state is not None:
            doc_state.register(self._on_doc_changed)

    def activate(self):
        """Called by the app when this panel is switched to."""
        if self._doc_state is not None and self._doc_state.text.strip():
            self._run()

    def _build(self):
        top = tk.Frame(self, **T.frame_kw())
        top.pack(fill="x", padx=10, pady=(10, 4))

        run_btn = tk.Button(
            top,
            text="Validate",
            command=self._run,
            bg=T.BLUE,
            fg=T.BASE,
            activebackground=T.LAVENDER,
            activeforeground=T.BASE,
            relief="flat",
            font=T.FONT_UI_BOLD,
            padx=12,
            pady=4,
            cursor="hand2",
            bd=0,
        )
        run_btn.pack(side="left")

        open_btn = tk.Button(top, text="Open File…", command=self._open_file, **T.small_button_kw())
        open_btn.pack(side="left", padx=(8, 0))

        rand_btn = tk.Button(top, text="Random", command=self._random, **T.small_button_kw())
        rand_btn.pack(side="left", padx=(8, 0))

        self._roundtrip_var = tk.BooleanVar(value=True)
        self._ast_var = tk.BooleanVar(value=True)

        tk.Checkbutton(
            top,
            text="Round-trip check",
            variable=self._roundtrip_var,
            bg=T.BASE,
            fg=T.TEXT,
            selectcolor=T.SURFACE1,
            activebackground=T.BASE,
            activeforeground=T.TEXT,
            font=T.FONT_SMALL,
        ).pack(side="left", padx=(12, 0))
        tk.Checkbutton(
            top,
            text="AST analysis",
            variable=self._ast_var,
            bg=T.BASE,
            fg=T.TEXT,
            selectcolor=T.SURFACE1,
            activebackground=T.BASE,
            activeforeground=T.TEXT,
            font=T.FONT_SMALL,
        ).pack(side="left", padx=(8, 0))

        clear_btn = tk.Button(top, text="Clear", command=self._clear, **T.small_button_kw())
        clear_btn.pack(side="right")

        pane = tk.PanedWindow(self, orient="horizontal", bg=T.CRUST, sashwidth=4, sashrelief="flat", sashpad=2)
        pane.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left_frame = tk.Frame(pane, **T.frame_kw())
        tk.Label(left_frame, text="Input (Markdown)", **T.label_kw()).pack(anchor="w", padx=4, pady=(4, 2))
        self._input = tk.Text(left_frame, **T.text_area_kw(), wrap="none", undo=True)
        self._input.bind("<<Modified>>", self._on_input_modified)
        in_vsb = tk.Scrollbar(
            left_frame,
            orient="vertical",
            command=self._input.yview,
            bg=T.SURFACE1,
            troughcolor=T.SURFACE0,
            relief="flat",
        )
        self._input.configure(yscrollcommand=in_vsb.set)
        in_vsb.pack(side="right", fill="y")
        self._input.pack(fill="both", expand=True, padx=(4, 0), pady=(0, 4))

        right_frame = tk.Frame(pane, **T.frame_kw())
        tk.Label(right_frame, text="Validation Report", **T.label_kw()).pack(anchor="w", padx=4, pady=(4, 2))
        self._output = tk.Text(right_frame, **T.text_area_kw(), wrap="word", state="disabled")
        out_vsb = tk.Scrollbar(
            right_frame,
            orient="vertical",
            command=self._output.yview,
            bg=T.SURFACE1,
            troughcolor=T.SURFACE0,
            relief="flat",
        )
        self._output.configure(yscrollcommand=out_vsb.set)
        out_vsb.pack(side="right", fill="y")
        self._output.pack(fill="both", expand=True, padx=(4, 0), pady=(0, 4))
        self._output.tag_config("ok", foreground=T.GREEN)
        self._output.tag_config("warn", foreground=T.YELLOW)
        self._output.tag_config("issue", foreground=T.RED)
        self._output.tag_config("heading", foreground=T.MAUVE, font=T.FONT_UI_BOLD)

        pane.add(left_frame, minsize=200)
        pane.add(right_frame, minsize=200)

        self._status = tk.Label(self, text="", bg=T.BASE, fg=T.OVERLAY0, font=T.FONT_SMALL, anchor="w")
        self._status.pack(fill="x", padx=12, pady=(0, 4))

    # ------------------------------------------------------------------
    def _on_input_modified(self, _event=None):
        if self._updating_from_state:
            return
        if self._doc_state is not None:
            self._doc_state.set(self._input.get("1.0", "end-1c"))
        self._input.edit_modified(False)

    def _on_doc_changed(self, text: str):
        current = self._input.get("1.0", "end-1c")
        if current == text:
            return
        self._updating_from_state = True
        self._input.delete("1.0", "end")
        if text:
            self._input.insert("1.0", text)
        else:
            self._set_output("")
            self._status.config(text="", fg=T.OVERLAY0)
        self._input.edit_modified(False)
        self._updating_from_state = False

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Open Markdown file",
            filetypes=[("Markdown", "*.md *.markdown *.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            self._load_text(text)
            self._run()
            self._status.config(text=f"Loaded: {path}", fg=T.GREEN)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._status.config(text=f"Error: {exc}", fg=T.RED)

    def _random(self):
        # pylint: disable=import-outside-toplevel
        from markpickle.gui.randgen import random_markdown

        label, text = random_markdown()
        self._load_text(text)
        self._run()
        self._status.config(text=f"Random scenario: {label}", fg=T.PEACH)

    def _load_text(self, text: str):
        self._input.delete("1.0", "end")
        self._input.insert("1.0", text)
        self._input.edit_modified(False)
        if self._doc_state is not None:
            self._doc_state.set(text)

    # ------------------------------------------------------------------
    def _run(self):
        # pylint: disable=import-outside-toplevel
        import markpickle
        from markpickle.validate import validate_markdown

        text = self._input.get("1.0", "end-1c")
        if not text.strip():
            self._write_report([("heading", "No input provided.")])
            return

        cfg = self._config_state.config if self._config_state is not None else None
        lines: list[tuple[str, str]] = []

        if self._ast_var.get():
            lines.append(("heading", "AST Analysis\n"))
            try:
                ast_issues = validate_markdown(text)
                if ast_issues:
                    for issue in ast_issues:
                        lines.append(("issue", f"  ✗ {issue}\n"))
                else:
                    lines.append(("ok", "  ✓ No structural issues found.\n"))
            except Exception as exc:  # pylint: disable=broad-exception-caught
                lines.append(("issue", f"  Error during AST analysis: {exc}\n"))
            lines.append(("heading", ""))

        if self._roundtrip_var.get():
            lines.append(("heading", "Round-trip Check\n"))
            try:
                obj = markpickle.loads(text, config=cfg)
                round_tripped = markpickle.dumps(obj, config=cfg)
                obj2 = markpickle.loads(round_tripped, config=cfg)
                if obj == obj2:
                    lines.append(("ok", "  ✓ Round-trip safe.\n"))
                else:
                    lines.append(("issue", "  ✗ Round-trip produced a different object (lossy conversion).\n"))
                    lines.append(("warn", f"  Original:     {repr(obj)[:120]}\n"))
                    lines.append(("warn", f"  Round-tripped:{repr(obj2)[:120]}\n"))
            except NotImplementedError as exc:
                lines.append(("issue", f"  ✗ Unsupported construct: {exc}\n"))
            except Exception as exc:  # pylint: disable=broad-exception-caught
                lines.append(("issue", f"  ✗ Parse error: {exc}\n"))

        all_ok = all(tag in ("ok", "heading") for tag, _ in lines)
        self._status.config(
            text="All checks passed." if all_ok else "Issues found.",
            fg=T.GREEN if all_ok else T.RED,
        )
        self._write_report(lines)

    def _clear(self):
        self._input.delete("1.0", "end")
        self._set_output("")
        self._status.config(text="", fg=T.OVERLAY0)
        if self._doc_state is not None:
            self._doc_state.set("")

    def _write_report(self, segments: list[tuple[str, str]]):
        self._output.config(state="normal")
        self._output.delete("1.0", "end")
        for tag, text in segments:
            self._output.insert("end", text, tag)
        self._output.config(state="disabled")

    def _set_output(self, text: str):
        self._output.config(state="normal")
        self._output.delete("1.0", "end")
        self._output.insert("1.0", text)
        self._output.config(state="disabled")
