"""
Function created with help of ChatGPT
"""
import io
from typing import Any, Optional

from markpickle.mypy_types import DictTypes, ScalarTypes


def list_of_dict_to_markdown(builder: io.IOBase, data: list[dict[str, ScalarTypes]], indent: int = 0):
    """
    Create a markdown table. Assumes dict are compatible (have similar keys) and shallow (no dicts of dict values)
    """
    row_id = 0

    column_widths: dict[str, int] = {}
    for schema in data:
        column_widths = column_widths | {key: 0 for key in schema.keys()}

    for datum in data:
        for key, value in datum.items():
            # TODO: doesn't handle complex types (and maybe can't? markdown doesn't support nested tables, AFAIK)
            max_width = max(len(str(key)), len(str(value)))
            if max_width > column_widths[key]:
                column_widths[key] = max_width

    for datum in data:
        include_header = row_id == 0
        builder.write(dict_to_markdown(datum, include_header, column_widths, indent))
        row_id += 1


def dict_to_markdown(
    data: DictTypes, include_header: bool = True, column_widths: Optional[dict[str, int]] = None, indent: int = 0
) -> str:
    """Convert dict to a header-value pair, or a header-value pair where values can be tables."""
    indentation = indent * " "
    # Extract the keys and values from the dictionary
    keys = list(data.keys())
    # values = list(data.values())

    # Determine the maximum length of each key and value
    # max_key_length = max(len(str(key)) for key in keys)

    # why not used?
    # max_value_length = max(len(str(value)) for value in values)

    if not column_widths:
        column_widths = {key: 0 for key in data.keys()}
        for key, value in data.items():
            # TODO: doesn't handle complex types (and maybe can't? markdown doesn't support nested tables, AFAIK)
            max_width = max(len(str(key)), len(str(value)))
            if max_width > column_widths[key]:
                column_widths[key] = max_width

    # Build the header row
    header = ""
    separator = ""
    if include_header:
        header = "| " + " | ".join([str(key).ljust(column_widths[key]) for key in keys]) + " |\n"
        separator = f"{indentation}| " + " | ".join(["-" * column_widths[key] for key in keys]) + " |\n"

    # Build the rows of the table
    row = f"{indentation}| "
    row += " | ".join(str(value).ljust(column_widths[key]) for key, value in data.items())
    row += " |\n"

    # Combine the header, separator, and rows into a single table
    if include_header:
        table = header + separator + row
    else:
        table = row

    return f"{indentation}{table}"
