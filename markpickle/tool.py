r"""Command-line tool to validate and pretty-print Markdown as simple Python types

Usage::

    $ echo '-a\n-b\n-c' | python -m markpickle.tool
    ["a", "b", "c"]

Source code modeled after json.tool https://github.com/python/cpython/blob/3.11/Lib/json/tool.py
"""
import argparse
import sys
from pathlib import Path

import markpickle


def main():
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
    parser.add_argument("outfile", nargs="?", type=Path, help="write the output of infile to outfile", default=None)
    options = parser.parse_args()

    dump_args = {}

    with options.infile as infile:
        try:
            if options.json_lines:
                objs = (markpickle.loads(line) for line in infile)
            else:
                objs = (markpickle.load(infile),)

            if options.outfile is None:
                out = sys.stdout
            else:
                out = options.outfile.open("w", encoding="utf-8")
            with out as outfile:
                for obj in objs:
                    markpickle.dump(obj, outfile, **dump_args)
                    outfile.write("\n")
        except ValueError as error:
            raise SystemExit(error) from error


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError as exc:
        sys.exit(exc.errno)
