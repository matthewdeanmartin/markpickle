"""
Handle a convention for putting multiple serialized objects into a single file.
"""
import io
from typing import Generator


def split_file(file: io.FileIO) -> Generator[str, None, None]:
    """
    Split a file into a list of lines.
    """
    current_section = []
    last_row_is_blank = False

    def is_separator(row: bytes) -> bool:
        """Is this a markdown horizontal rule"""
        return (
            (row.startswith(b"___") and all(_ == b"_" for _ in row))
            or (row.startswith(b"***") and all(_ == b"*" for _ in row))
            or (last_row_is_blank and row.startswith(b"---") and all(_ == b"-" for _ in row))
        )

    for row in file:
        if is_separator(row):
            if current_section:
                yield "".join(current_section)
                current_section = []
        else:
            current_section.append(row.decode("utf-8"))
        last_row_is_blank = row == b"\n"

    if current_section:
        yield "".join(current_section)
