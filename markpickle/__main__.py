"""
CLI support
"""
import argparse
import json
import sys
from pathlib import Path

import markpickle

if __name__ == "__main__":

    def run() -> None:
        """CLI entry point"""
        program = "python -m markpickle"
        description = "Command-line tool to convert some markdown to json"
        parser = argparse.ArgumentParser(prog=program, description=description)
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
                objs = (markpickle.load(infile),)

                if options.outfile is None:
                    out = sys.stdout
                else:
                    out = options.outfile.open("w", encoding="utf-8")
                with out as outfile:
                    for obj in objs:
                        json.dump(obj, outfile, **dump_args)
                        outfile.write("\n")
            except ValueError as error:
                raise SystemExit(error) from error

    run()
