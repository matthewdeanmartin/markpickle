"""
Help / Cheat Sheet panel — syntax reference for supported markdown constructs.
"""

import tkinter as tk

from markpickle.gui import theme as T

_CHEAT_SHEET = """\
MARKPICKLE SYNTAX CHEAT SHEET
══════════════════════════════════════════════════════════

SCALARS
───────
Plain paragraph text → string
  hello world

Numbers (auto-inferred with infer_scalar_types=True):
  42         → int
  3.14       → float
  True/true  → bool True
  False/false → bool False
  None       → None
  2024-01-15 → datetime.date

LISTS (unordered → list)
───────────────────────
- alpha
- beta
- gamma

→ ['alpha', 'beta', 'gamma']

LISTS (ordered → tuple)
───────────────────────
1. first
2. second
3. third

→ ('first', 'second', 'third')

NESTED LISTS
────────────
- outer
  - inner one
  - inner two

→ ['outer', ['inner one', 'inner two']]

DICTIONARIES (ATX headers as keys)
────────────────────────────────────
# key1

value one

# key2

value two

→ {'key1': 'value one', 'key2': 'value two'}

NESTED DICTS (sub-headers)
──────────────────────────
# parent

## child

value

→ {'parent': {'child': 'value'}}

TABLES (list of dicts)
──────────────────────
| name  | age |
| ----- | --- |
| Alice |  30 |
| Bob   |  25 |

→ [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]

DEFINITION LISTS (dict)
───────────────────────
term
:   definition

→ {'term': 'definition'}

CODE BLOCKS (string value)
──────────────────────────
```python
print("hello")
```

→ 'print("hello")'

MULTIPLE DOCUMENTS (--- separator)
────────────────────────────────────
Use loads_all() / load_all() to parse multiple
documents separated by --- lines.

UNSUPPORTED (will not round-trip)
────────────────────────────────────
  • Blockquotes (> text)
  • Inline links ([text](url))
  • Inline images (![alt](url))
  • Horizontal rules (---)
  • Raw HTML blocks
  • Strikethrough (~~text~~)

Use the Validate panel to check your document.

DOM MODE
────────
loads_as_dom(text) → list of tag-named dicts
  [{'tag': 'h1', 'text': 'Title'},
   {'tag': 'p',  'text': 'Hello'},
   {'tag': 'ul', 'items': ['a', 'b']}]

All markdown preserved — nothing is discarded.

INSTALL EXTRAS
──────────────
pip install markpickle[all]      # everything
pip install markpickle[tables]   # tabulate
pip install markpickle[images]   # Pillow
pip install markpickle[format]   # mdformat

CLI COMMANDS
────────────
markpickle convert data.md           # → JSON to stdout
markpickle convert data.md out.json  # → JSON file
markpickle convert -                 # read from stdin
markpickle validate data.md          # round-trip check
markpickle doctor                    # show env info
markpickle gui                       # launch this GUI
"""


class HelpPanel(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **T.frame_kw(), **kw)
        self._build()

    def _build(self):
        top = tk.Frame(self, **T.frame_kw())
        top.pack(fill="x", padx=10, pady=(10, 4))

        tk.Label(top, text="Help & Cheat Sheet", **T.heading_kw()).pack(side="left")

        copy_btn = tk.Button(top, text="Copy All", command=self._copy_all, **T.small_button_kw())
        copy_btn.pack(side="right")

        self._text = tk.Text(self, **T.text_area_kw(), wrap="none", state="normal")
        self._text.tag_config("section", foreground=T.MAUVE, font=T.FONT_UI_BOLD)
        self._text.tag_config("subsection", foreground=T.BLUE)
        self._text.tag_config("code", foreground=T.GREEN, font=T.FONT_MONO)
        self._text.tag_config("warn", foreground=T.YELLOW)

        vsb = tk.Scrollbar(
            self, orient="vertical", command=self._text.yview, bg=T.SURFACE1, troughcolor=T.SURFACE0, relief="flat"
        )
        hsb = tk.Scrollbar(
            self, orient="horizontal", command=self._text.xview, bg=T.SURFACE1, troughcolor=T.SURFACE0, relief="flat"
        )
        self._text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y", padx=(0, 10), pady=(0, 0))
        hsb.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        self._text.pack(fill="both", expand=True, padx=(10, 0), pady=(0, 0))

        self._populate()
        self._text.config(state="disabled")

    def _populate(self):
        for line in _CHEAT_SHEET.splitlines(keepends=True):
            stripped = line.rstrip()
            if stripped and stripped == stripped.upper() and len(stripped) > 4 and not stripped.startswith(" "):
                self._text.insert("end", line, "section")
            elif stripped.startswith("══") or stripped.startswith("──"):
                self._text.insert("end", line, "subsection")
            elif stripped.startswith("  •"):
                self._text.insert("end", line, "warn")
            elif stripped.startswith("  ") and stripped.strip().startswith(
                ("→", "#", "-", "|", "1.", "```", "term", ":")
            ):
                self._text.insert("end", line, "code")
            else:
                self._text.insert("end", line)

    def _copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(_CHEAT_SHEET)
