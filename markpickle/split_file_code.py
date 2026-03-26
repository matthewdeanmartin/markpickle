"""
Handle a convention for putting multiple serialized objects into a single file.
"""

import io
from typing import Generator


def is_markdown_separator(row: str, last_row_blank: bool) -> bool:
    """Return ``True`` when a line is a markdown document separator."""
    compact = row.strip().replace(" ", "")
    if len(compact) < 3:
        return False
    if set(compact) in ({"_"}, {"*"}):
        return True
    if set(compact) == {"-"}:
        return True
    return False


def split_file(file: io.FileIO) -> Generator[str, None, None]:
    """
    Split a file into a list of lines.
    """
    current_section: list[str] = []
    last_row_is_blank = False

    for row in file:
        decoded_row = row.decode("utf-8")
        if is_markdown_separator(decoded_row, last_row_is_blank):
            if current_section:
                yield "".join(current_section)
                current_section = []
        else:
            current_section.append(decoded_row)
        last_row_is_blank = row == b"\n"

    if current_section:
        yield "".join(current_section)
