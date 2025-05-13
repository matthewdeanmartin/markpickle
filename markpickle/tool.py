r"""Command-line tool to validate and pretty-print Markdown as simple Python types

Usage::

    $ echo '-a\n-b\n-c' | python -m markpickle.tool
    ["a", "b", "c"]

Source code modeled after json.tool https://github.com/python/cpython/blob/3.11/Lib/json/tool.py
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

import markpickle


def main(
    argv: Optional[Sequence[str]] = None,
):
    """CLI entry point"""
    prog = "python -m markpickle.tool"
    description = "Command-line tool to validate and pretty-print Markdown as simple Python types"
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument(
        "infile",
        nargs="?",
        type=argparse.FileType(encoding="utf-8"),
        help="a Markdown file to be pretty-printed",
        default=sys.stdin,
    )

    parser.add_argument(
        "--markdown-lines",  # Added the flag
        action="store_true",
        help="Process each line of the input as a separate Markdown document.",
    )

    parser.add_argument("outfile", nargs="?", type=Path, help="write the output of infile to outfile", default=None)
    options = parser.parse_args(argv)

    # dump_args:dict[str,str] = {}

    with options.infile as infile:
        try:
            if options.markdown_lines:
                objs: Any = (markpickle.loads(line) for line in infile)
            else:
                objs = (markpickle.load(infile),)

            if options.outfile is None:
                out = sys.stdout
            else:
                out = options.outfile.open("w", encoding="utf-8")
            # with out as outfile: # can't close this?
            outfile = out
            for obj in objs:
                # outfile.write(repr(objs))
                markpickle.dump(obj, outfile)  # , **dump_args)
                outfile.write("\n")
        except ValueError as error:
            raise SystemExit(error) from error


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError as exc:
        sys.exit(exc.errno)
