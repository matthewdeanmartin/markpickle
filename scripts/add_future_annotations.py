"""
Ensure every .py file under the given directories starts with
``from __future__ import annotations`` (after the module docstring, if any).

Usage:
    python scripts/add_future_annotations.py [dir ...]

Defaults to ``markpickle`` and ``test`` when no arguments are given.
"""

from __future__ import annotations

import sys
from pathlib import Path

SENTINEL = "from __future__ import annotations"


def _insert_after_docstring(text: str) -> str:
    """Return *text* with the sentinel inserted after the leading docstring."""
    lines = text.splitlines(keepends=True)
    i = 0

    # Skip leading blank lines.
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Skip over a module-level docstring.
    if i < len(lines) and (lines[i].startswith('"""') or lines[i].startswith("'''")):
        quote = lines[i][:3]
        single_line = lines[i].strip().endswith(quote) and len(lines[i].strip()) > 3
        if single_line:
            i += 1
        else:
            i += 1
            while i < len(lines):
                if quote in lines[i]:
                    i += 1
                    break
                i += 1

    insert_at = i
    new_lines = lines[:insert_at] + [SENTINEL + "\n"] + lines[insert_at:]
    return "".join(new_lines)


def process_file(path: Path) -> bool:
    """Add the sentinel to *path* if absent. Returns True if the file was changed."""
    text = path.read_text(encoding="utf-8")
    if SENTINEL in text:
        return False
    updated = _insert_after_docstring(text)
    path.write_text(updated, encoding="utf-8")
    return True


def process_dirs(dirs: list[Path]) -> None:
    changed = 0
    for directory in dirs:
        for path in sorted(directory.rglob("*.py")):
            if process_file(path):
                print(f"updated {path}")
                changed += 1
    if changed == 0:
        print("all files already have the import")
    else:
        print(f"{changed} file(s) updated")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    root = Path(__file__).resolve().parents[1]
    dirs = [Path(a) for a in args] if args else [root / "markpickle", root / "test"]
    process_dirs(dirs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
