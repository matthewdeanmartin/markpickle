"""
markpickle CLI — convert, validate, doctor, gui subcommands.

Usage:
    markpickle convert <infile> [outfile]   # markdown -> json (or '-' for stdin)
    markpickle validate <infile>            # check safe round-trip
    markpickle doctor                       # show installed optional libraries
    markpickle gui                          # launch tkinter GUI
"""

import argparse
import importlib.metadata
import json
import platform
import sys
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _version(pkg: str) -> str:
    """Return installed version string or 'NOT INSTALLED'."""
    try:
        return importlib.metadata.version(pkg)
    except importlib.metadata.PackageNotFoundError:
        return "NOT INSTALLED"


def _tkinter_status() -> str:
    try:
        import tkinter  # noqa: F401

        return "available (stdlib)"
    except ImportError:
        return "NOT AVAILABLE (missing from this Python build)"


def _col(text: str, width: int) -> str:
    return text.ljust(width)


# ---------------------------------------------------------------------------
# Subcommand: doctor
# ---------------------------------------------------------------------------


def cmd_doctor(_args: argparse.Namespace) -> int:
    rows = [
        ("Python", platform.python_version()),
        ("mistune", _version("mistune")),
        ("tabulate [tables]", _version("tabulate")),
        ("Pillow [images]", _version("pillow")),
        ("mdformat [format]", _version("mdformat")),
        ("tkinter", _tkinter_status()),
    ]
    w0, w1 = 24, 40
    sep = "-" * (w0 + w1 + 3)
    print(sep)
    print(_col("Package", w0), _col("Status", w1))
    print(sep)
    for name, status in rows:
        ok = status not in ("NOT INSTALLED", "NOT AVAILABLE (missing from this Python build)")
        marker = "ok" if ok else "!!"
        print(f"[{marker}] {_col(name, w0 - 5)} {status}")
    print(sep)
    hint = "pip install markpickle[all]  # installs tabulate, Pillow, mdformat"
    print(f"\nTo install all optional extras:\n  {hint}\n")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: convert
# ---------------------------------------------------------------------------


def cmd_convert(args: argparse.Namespace) -> int:
    from markpickle.deserialize import load

    infile_arg: str = args.infile
    outfile_arg: Optional[str] = args.outfile

    try:
        if infile_arg == "-":
            infile = sys.stdin
        else:
            path = Path(infile_arg)
            if not path.exists():
                print(f"error: file not found: {infile_arg}", file=sys.stderr)
                return 1
            infile = path.open(encoding="utf-8")

        with infile:
            obj = load(infile)

        result = json.dumps(obj, default=str, indent=2)

        if outfile_arg is None:
            print(result)
        else:
            Path(outfile_arg).write_text(result + "\n", encoding="utf-8")
            print(f"Written to {outfile_arg}")

    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


# ---------------------------------------------------------------------------
# Subcommand: validate
# ---------------------------------------------------------------------------


def cmd_validate(args: argparse.Namespace) -> int:
    import markpickle

    path = Path(args.infile)
    if not path.exists():
        print(f"error: file not found: {args.infile}", file=sys.stderr)
        return 1

    issues: list[str] = []

    try:
        with path.open(encoding="utf-8") as fh:
            original_text = fh.read()

        obj = markpickle.loads(original_text)
        round_tripped = markpickle.dumps(obj)
        obj2 = markpickle.loads(round_tripped)

        if obj != obj2:
            issues.append("Round-trip produced a different object (lossy conversion).")

    except NotImplementedError as exc:
        issues.append(f"Unsupported construct: {exc}")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"Parse error: {exc}")

    if issues:
        print(f"FAIL  {args.infile}")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print(f"OK    {args.infile}  (round-trip safe)")
        return 0


# ---------------------------------------------------------------------------
# Subcommand: gui
# ---------------------------------------------------------------------------


def cmd_gui(_args: argparse.Namespace) -> int:
    try:
        from markpickle.gui.app import launch_gui  # noqa: PLC0415

        launch_gui()
        return 0
    except ImportError as exc:
        print(f"error: could not launch GUI: {exc}", file=sys.stderr)
        print("Make sure tkinter is available in your Python installation.", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="markpickle",
        description="Convert between Markdown and Python data structures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  markpickle convert data.md             # convert to JSON, print to stdout
  markpickle convert data.md out.json    # convert to JSON file
  markpickle convert -                   # read markdown from stdin
  markpickle validate data.md            # check if file round-trips safely
  markpickle doctor                      # show optional library status
  markpickle gui                         # launch the GUI
""",
    )
    parser.add_argument("--version", action="version", version=f"markpickle {_version('markpickle')}")

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # convert
    p_convert = sub.add_parser("convert", help="Convert a markdown file to JSON")
    p_convert.add_argument(
        "infile",
        help="markdown file to convert, or '-' to read from stdin",
    )
    p_convert.add_argument(
        "outfile",
        nargs="?",
        default=None,
        help="output file (default: stdout)",
    )

    # validate
    p_validate = sub.add_parser("validate", help="Check if a markdown file can be safely round-tripped")
    p_validate.add_argument("infile", help="markdown file to validate")

    # doctor
    sub.add_parser("doctor", help="Show installed optional libraries and diagnostic info")

    # gui
    sub.add_parser("gui", help="Launch the tkinter GUI")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    dispatch: dict[str, Any] = {
        "convert": cmd_convert,
        "validate": cmd_validate,
        "doctor": cmd_doctor,
        "gui": cmd_gui,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(run())
