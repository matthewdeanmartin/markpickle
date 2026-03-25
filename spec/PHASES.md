# Markpickle Development Phases

## Phase 1 — Foundations (current)

### 1.1 Optional dependencies
- Make `tabulate` optional: guard import in `third_party_tables.py`, skip if not installed
- Make `pillow` optional: guard import in `binary_streams.py`, skip if not installed
- Make `mdformat` optional: it is already dev-only but any runtime import must be guarded
- Add `[project.optional-dependencies]` to `pyproject.toml`:
  - `[all]` = tabulate + pillow + mdformat
  - `[tables]` = tabulate
  - `[images]` = pillow
  - `[format]` = mdformat

### 1.2 CLI entry point
- Add `[project.scripts]` entry so `markpickle` works as a command (not just `python -m markpickle`)
- Redesign `__main__.py` with subcommands via argparse:
  - `markpickle convert <infile> [outfile]` — main conversion (md→json or py→md based on extension)
  - `markpickle validate <infile>` — check if file can be safely round-tripped
  - `markpickle doctor` — show installed optional deps, Python version, mistune version
  - `markpickle gui` — launch the tkinter GUI (phase 3)
- When run with no arguments: print help and exit (no silent stdin wait)
- Keep stdin pipe support: `markpickle convert -` reads stdin
- `--config config.toml` flag on all subcommands (phase 2)

### 1.3 Mistune version fix
- The `mistune<3.0.0` pin is correct but pip may resolve to very old 0.x versions
- Tighten pin to `mistune>=2.0.0,<3.0.0` so the AST renderer is always available

### 1.4 Doctor command (initial)
- `markpickle doctor` prints a table of:
  - Python version
  - mistune version (required)
  - tabulate version / NOT INSTALLED
  - pillow version / NOT INSTALLED
  - mdformat version / NOT INSTALLED
  - tkinter availability (stdlib, but may be missing on minimal installs)

---

## Phase 2 — Config file + DOM mode

### 2.1 File-based config (`config.toml`)
- Load `[tool.markpickle]` section from `pyproject.toml` in current directory by default
- `--config path/to/config.toml` overrides location
- Map TOML keys to `Config` dataclass fields
- Helper module: `markpickle/config_file.py`

### 2.2 HTML/DOM-style deserialization
- New function: `markpickle.load_as_dom(stream) -> dict`
- Walks the mistune AST and produces a structure where keys are HTML tag names:
  `{"h1": "Title", "h2": "Section", "p": "some text", "ul": ["a", "b"], "table": [...]}`
- Not lossy (preserves all markdown structure as a DOM tree)
- Does not replace existing `load()` — it is a separate API
- New module: `markpickle/dom_deserialize.py`
- Exposed as `markpickle.load_as_dom` and `markpickle.loads_as_dom`

### 2.3 Validate command
- Walk the document and check for constructs that won't round-trip cleanly
- Return exit code 0 (ok) or 1 (issues found) with human-readable report

---

## Phase 3 — Tkinter GUI

### 3.1 Architecture
- `markpickle/gui/` package, lazily imported (never loaded during CLI usage)
- `markpickle/gui/app.py` — main window, panel switcher
- `markpickle/gui/panels/` — one module per panel
- Dark theme: Catppuccin Mocha palette
- Left sidebar: tab buttons for each panel
- Right column: syntax cheat sheet for the active panel

### 3.2 Panels
1. **Convert** — paste markdown → see Python repr, or paste Python → see markdown
2. **Format** — paste markdown → reformat with mdformat (if installed) or internal formatter
3. **Validate** — paste markdown → report on what will/won't round-trip
4. **Config** — view/edit current Config options, see their effect live
5. **Doctor** — same output as `markpickle doctor` CLI command
6. **Help / Cheat Sheet** — embedded syntax reference

### 3.3 Entry points
- `markpickle gui` subcommand
- `markpickle-gui` script entry point (for desktop launchers)

---

## Phase 4 — Polish & Testing

### 4.1 Tests for new features
- Tests for optional-dep guards (monkeypatch imports)
- Tests for DOM deserialization
- Tests for config file loading
- CLI smoke tests (subprocess)

### 4.2 Documentation
- Update README with install extras (`pip install markpickle[all]`)
- Document CLI usage with examples
- Document DOM mode

### 4.3 Version bump
- Bump to 2.1.0 after phase 1+2
- Bump to 2.2.0 after phase 3

---

## Scope notes

- **mistune is and remains a hard dependency** — the entire deserialization pipeline depends on its AST format
- `pip install markpickle` (no extras) installs only mistune; everything else is optional
- GUI is always available to import (tkinter is stdlib) but the package does not import it at top level
- Rust extension (`_rust_speedups.py`) remains a placeholder — not in scope for these phases
