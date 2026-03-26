# Contributing (LLMs / AI Agents)

This document is written for AI coding assistants (Claude, Copilot, Cursor, etc.) working
on the markpickle codebase. It summarizes conventions, pitfalls, and what to check before
declaring work done.

## Project in one paragraph

markpickle is a **lossy Python ↔ Markdown serialization library**. It serializes Python
data structures (dicts, lists, scalars, dates, etc.) to Markdown using ATX headers for
dicts and bullet lists for lists, then deserializes by parsing the Markdown AST via
`mistune`. It is intentionally lossy — Markdown lacks the expressiveness of JSON. The
public API mirrors `json`/`pickle` (`dumps`, `loads`, `dump`, `load`).

## Key source files

| File | Role |
| -------------------------------- | ------------------------------------------------- |
| `markpickle/__init__.py` | Public API surface — everything exported here |
| `markpickle/serialize.py` | Python → Markdown |
| `markpickle/deserialize.py` | Markdown → Python (AST-based via mistune) |
| `markpickle/config_class.py` | All configuration options (`Config` dataclass) |
| `markpickle/python_to_tables.py` | Dict/list ↔ Markdown table conversion |
| `markpickle/atx_as_dictionary.py`| ATX header parsing for nested dicts |
| `markpickle/simplify_types.py` | Type simplification helpers |
| `markpickle/unicode_text.py` | Unicode formatting preservation |
| `markpickle/validate.py` | AST-based structural validation |
| `markpickle/__main__.py` | CLI entry point (4 subcommands) |
| `markpickle/gui/app.py` | tkinter GUI application |
| `markpickle/gui/panels/` | One file per GUI panel |
| `markpickle/config_file.py` | Load Config from pyproject.toml |
| `markpickle/sugar.py` | JSON ↔ Markdown convenience helpers |
| `test/` | All tests (pytest + doctests) |
| `scripts/` | Maintenance scripts |

## Coding conventions

### Always use `uv run`

The project uses a `uv`-managed virtual environment. Never use bare `python`, `pytest`,
`mypy`, etc. — always prefix with `uv run`:

```bash
uv run pytest test/
uv run mypy markpickle
```

The `Makefile` targets already do this; prefer `make test`, `make lint`, etc. when
running the full suite.

### `from __future__ import annotations` is required

Every `.py` file in `markpickle/` and `test/` must start with
`from __future__ import annotations`. This allows `X | Y` union syntax in **annotations**
on Python 3.9+. The `make format` target (`scripts/add_future_annotations.py`) enforces
this automatically.

### Python 3.9+ compatibility rules

markpickle supports Python 3.9+. The following patterns break on 3.9 and must be avoided:

| Bad (3.10+) | Good (3.9+) |
| -------------------------------- | ------------------------------------ |
| `isinstance(x, A \| B)` | `isinstance(x, (A, B))` |
| `cast(A \| B, x)` at runtime | `cast("A \| B", x)` (string literal) |
| `zip(a, b, strict=True)` | `zip(a, b)` (add a manual length check) |
| `dataclass.__getstate__()` | `dataclasses.asdict(obj)` as fallback |

Do not remove `from __future__ import annotations` thinking it's unnecessary — it is the
only thing making `X | Y` legal in annotation positions on 3.9.

### Type annotations

The project uses mypy in strict mode and pyright. Run `make type-check-all` before
submitting changes. Common gotchas:

- `mistune` has no stubs; imports from it are covered by `# type: ignore` or `Any`.
- `SerializableTypes` is a recursive `TypeAlias` defined in `markpickle/mypy_types.py`.
- `cast()` calls are used frequently to help mypy — do not remove them without
  understanding why they are there.

## Testing conventions

- Unit tests live in `test/`. Doctests live inline in module docstrings.
- Run everything with `make test` (uses pytest-xdist for parallelism).
- GUI tests (`test/test_gui_panels.py`, `test/test_gui_app.py`) use
  `pytest.importorskip("tkinter")` — they skip automatically when tkinter is unavailable.
- Benchmark tests live in `test/test_benchmark.py` and are excluded from the normal
  test run.

## Compatibility tests

The `test/compat/` directory contains frozen behavioral snapshots of markpickle v1.6.4.
These tests run against committed JSON fixtures (no external venv needed). If you change
behavior that was present in v1.6.4, either:

- Justify it as a bug fix and document with the `documented_change` pytest marker, or
- Add a note to `CHANGELOG.md` under `Breaking Changes`.

Run `make compat` to check. If fixtures need updating after an intentional behavior
change, run `make compat-refresh` (requires the baseline venv — see
[Compatibility Tests](COMPAT_TESTS.md)).

## Before calling work done

Run this checklist locally:

```bash
make format          # formatting + future annotations
make lint            # pylint (must score >= 9.9)
make type-check-all  # mypy + pyright + ty
make test            # doctests + unit tests
make compat          # v1.6.4 behavioral compatibility
make docs-build      # MkDocs site builds without errors
```

Or run them all at once:

```bash
make check-code
```

## Common pitfalls

- **Don't add functions to `__init__.py` without also adding them to `__all__`** — the
  public API is explicit.
- **Don't reference functions in docs that don't exist** — `examples.md` once referenced
  `loads_with_frontmatter()` which was never implemented. Verify against `__init__.py`
  before documenting.
- **Tables in Markdown are detected by pipe count**, not by a dedicated token in some
  mistune configurations. Check `python_to_tables.py` before changing table parsing.
- **`None` serializes to an empty string** — this is intentional and documented in
  `limitations.md`. Do not "fix" it without understanding the design trade-offs.
- **Falsy values in general are lossy** — `0`, `False`, `[]`, `{}` all round-trip
  imperfectly. This is documented behavior.
- **The GUI requires tkinter** — any code path that imports from `markpickle.gui` must
  handle `ImportError` gracefully.

## Architecture sketch

```
dumps(value)
  └─ serialize.py: _serialize_value()
       ├─ scalar → str
       ├─ list   → "- item\n..." or "1. item\n..." (tuple)
       ├─ dict   → "# key\n\nval\n" or table
       └─ object → __getstate__ / dataclasses.asdict / __dict__

loads(text)
  └─ deserialize.py: load()
       ├─ mistune.parse() → token list
       ├─ has headers? → parse_outermost_dict() → walk_dict()
       └─ no headers?  → process_list_of_tokens()
                              ├─ list token    → process_list()
                              ├─ paragraph     → extract_scalar()
                              └─ table (pipe)  → parse_table_to_list_of_dict()
```
