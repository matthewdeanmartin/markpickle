"""
Convert panel — Markdown → Python repr, or Python repr → Markdown.
Auto-runs conversion after Random.
"""

import tkinter as tk
from tkinter import filedialog

from markpickle.gui import theme as T


class ConvertPanel(tk.Frame):
    def __init__(self, parent, doc_state=None, config_state=None, **kw):
        super().__init__(parent, **T.frame_kw(), **kw)
        self._direction = "md_to_py"
        self._doc_state = doc_state
        self._config_state = config_state
        self._updating_from_state = False
        self._build()
        if doc_state is not None:
            doc_state.register(self._on_doc_changed)

    def _build(self):
        top = tk.Frame(self, **T.frame_kw())
        top.pack(fill="x", padx=10, pady=(10, 4))

        self._dir_btn = tk.Button(top, text="Markdown → Python", command=self._toggle_direction, **T.small_button_kw())
        self._dir_btn.pack(side="left")

        run_btn = tk.Button(
            top,
            text="Convert",
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
        run_btn.pack(side="left", padx=(8, 0))

        open_btn = tk.Button(top, text="Open File…", command=self._open_file, **T.small_button_kw())
        open_btn.pack(side="left", padx=(8, 0))

        rand_btn = tk.Button(top, text="Random", command=self._random, **T.small_button_kw())
        rand_btn.pack(side="left", padx=(8, 0))

        clear_btn = tk.Button(top, text="Clear", command=self._clear, **T.small_button_kw())
        clear_btn.pack(side="left", padx=(8, 0))

        copy_btn = tk.Button(top, text="Copy Output", command=self._copy_output, **T.small_button_kw())
        copy_btn.pack(side="right")

        pane = tk.PanedWindow(self, orient="horizontal", bg=T.CRUST, sashwidth=4, sashrelief="flat", sashpad=2)
        pane.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left_frame = tk.Frame(pane, **T.frame_kw())
        self._in_label = tk.Label(left_frame, text="Input (Markdown)", **T.label_kw())
        self._in_label.pack(anchor="w", padx=4, pady=(4, 2))
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
        self._out_label = tk.Label(right_frame, text="Output (Python repr)", **T.label_kw())
        self._out_label.pack(anchor="w", padx=4, pady=(4, 2))
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

    # ------------------------------------------------------------------
    def _on_input_modified(self, _event=None):
        if self._updating_from_state:
            return
        if self._doc_state is not None and self._direction == "md_to_py":
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
            self._status.config(text=f"Loaded: {path}", fg=T.GREEN)
            self._run()
        except Exception as exc:
            self._status.config(text=f"Error: {exc}", fg=T.RED)

    def _random(self):
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
    def _toggle_direction(self):
        if self._direction == "md_to_py":
            self._direction = "py_to_md"
            self._dir_btn.config(text="Python → Markdown")
            self._in_label.config(text="Input (Python repr)")
            self._out_label.config(text="Output (Markdown)")
        else:
            self._direction = "md_to_py"
            self._dir_btn.config(text="Markdown → Python")
            self._in_label.config(text="Input (Markdown)")
            self._out_label.config(text="Output (Python repr)")

    def _run(self):
        import markpickle

        text = self._input.get("1.0", "end-1c")
        cfg = self._config_state.config if self._config_state is not None else None
        try:
            if self._direction == "md_to_py":
                result = markpickle.loads(text, config=cfg)
                out = repr(result)
            else:
                import ast

                obj = ast.literal_eval(text)
                out = markpickle.dumps(obj, config=cfg)
            self._set_output(out)
            self._status.config(text="OK", fg=T.GREEN)
        except Exception as exc:
            self._set_output(f"Error: {exc}")
            self._status.config(text=f"Error: {exc}", fg=T.RED)

    def _clear(self):
        self._input.delete("1.0", "end")
        self._set_output("")
        self._status.config(text="", fg=T.OVERLAY0)
        if self._doc_state is not None:
            self._doc_state.set("")

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
