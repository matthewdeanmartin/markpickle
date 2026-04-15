"""
Format panel — reformat markdown with mdformat (if installed) or normalise whitespace.
Auto-runs after Random. Auto-runs when activated if a doc is in shared state.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog

from markpickle.gui import theme as T


class FormatPanel(tk.Frame):
    """
    Panel for formatting markdown using mdformat or basic normalization.
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

        format_btn = tk.Button(
            top,
            text="Format",
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
        format_btn.pack(side="left")

        open_btn = tk.Button(top, text="Open File…", command=self._open_file, **T.small_button_kw())
        open_btn.pack(side="left", padx=(8, 0))

        rand_btn = tk.Button(top, text="Random", command=self._random, **T.small_button_kw())
        rand_btn.pack(side="left", padx=(8, 0))

        copy_btn = tk.Button(top, text="Copy Output", command=self._copy_output, **T.small_button_kw())
        copy_btn.pack(side="right")

        self._mdformat_label = tk.Label(top, text="", bg=T.BASE, fg=T.TEXT, font=T.FONT_SMALL)
        self._mdformat_label.pack(side="left", padx=(12, 0))

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
        tk.Label(right_frame, text="Formatted Output", **T.label_kw()).pack(anchor="w", padx=4, pady=(4, 2))
        self._output = tk.Text(right_frame, **T.text_area_kw(), wrap="none", state="disabled")
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

        pane.add(left_frame, minsize=200)
        pane.add(right_frame, minsize=200)

        self._status = tk.Label(self, text="", bg=T.BASE, fg=T.OVERLAY0, font=T.FONT_SMALL, anchor="w")
        self._status.pack(fill="x", padx=12, pady=(0, 4))

        self._check_mdformat()

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

    # ------------------------------------------------------------------
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
    def _check_mdformat(self):
        try:
            # pylint: disable=import-outside-toplevel, unused-import
            import mdformat  # noqa: F401

            self._mdformat_label.config(text="mdformat available", fg=T.GREEN)
        except ImportError:
            self._mdformat_label.config(text="mdformat not installed — using basic normaliser", fg=T.YELLOW)

    def _run(self):
        text = self._input.get("1.0", "end-1c")
        try:
            formatted = self._format(text)
            self._set_output(formatted)
            self._status.config(text="OK", fg=T.GREEN)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._set_output(f"Error: {exc}")
            self._status.config(text=f"Error: {exc}", fg=T.RED)

    def _format(self, text: str) -> str:
        try:
            # pylint: disable=import-outside-toplevel
            import mdformat

            return mdformat.text(text)
        except ImportError:
            pass
        lines = text.splitlines()
        cleaned = [line.rstrip() for line in lines]
        result = "\n".join(cleaned)
        if result and not result.endswith("\n"):
            result += "\n"
        return result

    def _copy_output(self):
        text = self._output.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        self._status.config(text="Copied to clipboard.", fg=T.GREEN)

    def _set_output(self, text: str):
        self._output.config(state="normal")
        self._output.delete("1.0", "end")
        self._output.insert("1.0", text)
        self._output.config(state="disabled")
