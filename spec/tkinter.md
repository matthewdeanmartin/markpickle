# Contributing to the Tkinter GUI

This document explains the architecture, design decisions, and conventions
behind markpickle's tkinter GUI so that contributors can extend or modify it
confidently.

______________________________________________________________________

## Launching the GUI

Three equivalent entry points:

```bash
uv run markpickle gui        # subcommand
uv run markpickle --gui      # top-level flag
uv run markpickle-gui        # gui-scripts entry point (pyproject.toml)
```

All three converge on `markpickle.gui.app:launch_gui`.

______________________________________________________________________

## Architecture overview

```
markpickle/
├── core/              # Pure domain logic (diagnostics, backup, dedupe, …)
├── platform/          # OS-specific PATH readers/writers
├── models.py          # Frozen dataclasses consumed by every layer
├── services.py        # Orchestration helpers shared by CLI and GUI
├── cli.py             # argparse CLI (unchanged by the GUI)
└── gui/
    ├── __init__.py
    └── app.py         # Entire GUI: app, panels, widgets, runner
```

### The three-layer rule

| Layer | Touches the filesystem? | Knows about tkinter? | Examples |
|----------------------------------|----------------------------------|----------------------|-----------------------------------------------------------------|
| **Core** (`core/*`, `models.py`) | Yes (reads/writes PATH, backups) | No | `analyze_snapshot`, `EditSession`, `create_backup` |
| **Services** (`services.py`) | Yes (loads config, calls core) | No | `read_current_report`, `backup_now`, `get_snapshot_and_adapter` |
| **GUI** (`gui/app.py`) | No (delegates to services/core) | Yes | `DashboardPanel`, `InspectPanel`, `EditPanel` |

The GUI never reads or writes the PATH directly. It calls core modules
(via the services layer when orchestration is needed) and renders the
returned dataclasses into treeviews and text widgets.

### Why a single `app.py`?

The GUI is ~1100 lines. Splitting it across many files would add import
ceremony without improving navigability. If the GUI grows significantly,
the natural split points are clearly marked with comment banners:

```
# ── Dashboard ─────────────────────
# ── Inspect / Doctor ──────────────
# ── Backups ───────────────────────
# ...
```

Each section is self-contained and can be extracted to its own module by
moving the class and updating the `_build_panel` factory dict.

______________________________________________________________________

## Zero overhead on the CLI

The `gui` package is **never imported** during normal CLI usage. The
import is deferred behind a condition in `cli.py`:

```python
if args.command == "gui" or getattr(args, "gui", False):
    from markpickle.gui.app import launch_gui

    return launch_gui()
```

This means `import tkinter` (and all GUI code) only runs when the user
explicitly asks for the GUI. Verified by test:

```python
import markpickle.cli

assert "tkinter" not in sys.modules
```

______________________________________________________________________

## The dark theme

All colours are defined as module-level constants at the top of `app.py`:

```python
_CLR_OK = "#22c55e"  # green  — valid entries
_CLR_WARN = "#eab308"  # yellow — duplicates, warnings
_CLR_ERR = "#ef4444"  # red    — missing, invalid
_CLR_DIM = "#9ca3af"  # grey   — secondary text
_CLR_BG = "#1e1e2e"  # dark   — main background
_CLR_BG_ALT = "#252536"  # slightly lighter — text widgets
_CLR_FG = "#cdd6f4"  # light  — primary text
_CLR_ACCENT = "#89b4fa"  # blue   — headings, active sidebar
_CLR_SIDEBAR = "#181825"  # darkest — sidebar background
_CLR_BTN = "#313244"  # button background
_CLR_BTN_ACTIVE = "#45475a"  # button hover
```

These are [Catppuccin Mocha](https://catppuccin.com/) inspired. To change
the palette, update these constants — every widget references them.

### Treeview styling

Treeviews use a custom `ttk.Style` named `"Path.Treeview"` configured in
`_make_tree`. Row colouring is done via treeview **tags**:

```python
tree.tag_configure("ok", foreground=_CLR_OK)
tree.tag_configure("warn", foreground=_CLR_WARN)
tree.tag_configure("error", foreground=_CLR_ERR)
tree.tag_configure("dim", foreground=_CLR_DIM)
```

When inserting rows, pass the tag:

```python
tree.insert("", tk.END, values=(...), tags=("warn",))
```

The `_entry_display(entry)` helper maps a `DiagnosticEntry` to
`(tag, status_marker, notes_string)` for consistent rendering across
the Inspect, Doctor, and Edit panels.

______________________________________________________________________

## Background threading

Tkinter is single-threaded. All I/O (reading PATH, writing backups,
filesystem scans) must run off the UI thread.

### `_BackgroundRunner`

```python
class _BackgroundRunner:
    def run(self, func, *, args=(), on_success=None, on_error=None):
# 1. Spawns a daemon thread
# 2. Calls func(*args)
# 3. Posts on_success(result) or on_error(exc) back via root.after()
```

Usage in a panel:

```python
def _load(self):
    self._status.set("Loading...")
    self._runner.run(
        self._fetch,  # runs in background thread
        args=(self._scope_var.get(),),
        on_success=self._display,  # runs on main thread
        on_error=self._on_error,  # runs on main thread
    )


@staticmethod
def _fetch(scope_str):
    # This method MUST NOT touch any tkinter widget.
    # It can only call core/services and return data.
    from markpickle.services import read_current_report
    return read_current_report(Scope.from_value(scope_str))


def _display(self, report):
    # Safe to update widgets here — we're on the main thread.
    ...
```

**Rules:**

1. `_fetch` methods are `@staticmethod` — they must not reference `self`
   or any widget. This prevents accidental cross-thread widget access.
1. `on_success` / `on_error` callbacks run on the main thread via
   `root.after(0, ...)`, so they can freely update the UI.
1. Only one operation runs at a time per panel. Disable buttons during
   long operations if needed.

______________________________________________________________________

## Panel architecture

Every panel extends `_BasePanel`:

```python
class _BasePanel(tk.Frame):
    def __init__(self, parent, runner, status_var):
        super().__init__(parent, bg=_CLR_BG)
        self._runner = runner
        self._status = status_var
```

Panels are created on demand by `_build_panel` and registered in a
factory dict:

```python
builders = {
    "dashboard": DashboardPanel,
    "inspect": InspectPanel,
    "doctor": DoctorPanel,
    "backup": BackupPanel,
    "edit": EditPanel,
    "dedupe": DedupePanel,
    "populate": PopulatePanel,
    "repair": RepairPanel,
    "schedule": SchedulePanel,
}
```

When the user clicks a sidebar button, `_show_panel` destroys the current
panel and creates a fresh one. Panels are not cached — this keeps them
simple (no stale-state bugs) and construction is fast.

### Adding a new panel

1. Create a class extending `_BasePanel` in `app.py` (or its own module).
1. Add it to the `builders` dict in `_build_panel`.
1. Add a sidebar entry in `markpickleApp._build_ui`:

```python
items = [
    ...
    ("my_panel", "My Panel"),
]
```

That's it. The sidebar button, panel lifecycle, and status bar integration
are automatic.

______________________________________________________________________

## Reusable widget helpers

| Helper | Returns | Purpose |
|-----------------------------------------|----------------|------------------------------------------------------|
| `_make_tree(parent, columns, height)` | `ttk.Treeview` | Themed treeview with scrollbar and colour tags |
| `_make_output(parent, height)` | `tk.Text` | Read-only scrolled text area for output/diff display |
| `_output_set(text_widget, content)` | — | Replace text content (handles enable/disable state) |
| `_make_scope_selector(parent, default)` | `tk.StringVar` | Row of radio buttons for system/user/all |
| `_make_toolbar(parent)` | `tk.Frame` | Horizontal button bar |
| `_toolbar_btn(bar, text, command)` | `tk.Button` | Themed button inside a toolbar |

These helpers handle scrollbar wiring, colour configuration, and layout
so that panel code stays focused on business logic.

______________________________________________________________________

## Confirmation and user input

The CLI uses `input()` for confirmations. The GUI replaces these with:

| CLI pattern | GUI replacement |
|--------------------------------------------|------------------------------------------|
| `_confirm("Apply?", force=flag)` | `messagebox.askyesno("Title", "Apply?")` |
| `_prompt_yes_no("Install?", default=True)` | `messagebox.askyesno(...)` |
| `input("Enter path: ")` | `filedialog.askdirectory(...)` |

These are modal but do not block the tkinter event loop.

______________________________________________________________________

## Testing

GUI tests live in `tests/test_gui.py`. Key patterns:

### Tk root fixture

```python
@pytest.fixture()
def root():
    try:
        r = tk.Tk()
        r.withdraw()
    except tk.TclError:
        pytest.skip("No display available")
    yield r
    r.destroy()
```

Tests create a hidden Tk root and never call `mainloop()`. Widget state
is inspected directly. The `pytest.importorskip("tkinter")` at module
level skips the entire file on headless CI.

### Mocking services

Panels call services in background threads. Tests mock the services to
return fake data:

```python
with patch("markpickle.services.read_current_report",
           return_value=(_fake_snapshot(), _fake_report())):
    panel = InspectPanel(root, runner, status)
    root.update()
    assert panel.winfo_exists()
```

### Background runner tests

Since `root.after()` requires a running main loop, runner tests use a
`MagicMock` root where `after` calls the callback immediately:

```python
mock_root = MagicMock()
mock_root.after = lambda _ms, fn, *a: fn(*a)
```

### Running tests

```bash
uv run pytest tests/test_gui.py -v
```

______________________________________________________________________

## Relationship to `services.py`

`services.py` was created alongside the GUI to extract shared
orchestration logic from `cli.py`. It provides:

- `read_current_report(scope)` — load config, read PATH, run diagnostics
- `get_snapshot_and_adapter()` — return (snapshot, adapter, os_name) tuple
- `backup_now(tag, note, force)` — create and prune a backup
- `recent_backups(limit)` — list recent backup records
- `select_backup(identifier)` — resolve a backup by name/number
- `format_backup_timestamp_utc(value)` — consistent timestamp formatting

The CLI retains its own copies of some of these (for backward
compatibility with existing test mocking), but new code should prefer
`services.py`.

______________________________________________________________________

## Style guidelines

- **Fonts**: `"Segoe UI"` for labels/buttons, `"Consolas"` for data
  (paths, timestamps, code-like output). Both are available on Windows;
  tkinter falls back gracefully on other platforms.
- **Padding**: `padx=8, pady=4` is the standard widget spacing.
  Section headings use `pady=(12, 4)`.
- **No emojis** in the GUI unless the user requests them.
- **Status bar**: Set `self._status.set("message")` at the start and end
  of operations. Keep messages short (under ~60 chars).
- **Error handling**: Catch exceptions in `on_error` callbacks and show
  them via `messagebox.showerror`. Never let exceptions silently die in
  background threads.
