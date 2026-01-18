"""
Function created with help of ChatGPT
"""

import io
from typing import Optional, TextIO, Union, cast

from markpickle.mypy_types import ColumnsValuesTableType, DictTypes, ListTypes


def list_of_dict_to_markdown(builder: Union[io.IOBase, TextIO], data: list[DictTypes], indent: int = 0) -> None:
    """
    Create a markdown table. Assumes dict are compatible (have similar keys) and shallow (no dicts of dict values)
    """
    row_id = 0

    column_widths: dict[str, int] = {}
    for schema in data:
        column_widths = column_widths | {key: 0 for key in schema}

    for datum in data:
        for key, value in datum.items():
            # TODO: doesn't handle complex types (and maybe can't? markdown doesn't support nested tables, AFAIK)
            max_width = max(len(str(key)), len(str(value)))
            column_widths[key] = max(column_widths[key], max_width)

    for row_id, datum in enumerate(data):
        include_header = row_id == 0
        builder.write(dict_to_markdown(datum, include_header, column_widths, indent))


def dict_to_markdown(
    data: DictTypes, include_header: bool = True, column_widths: Optional[dict[str, int]] = None, indent: int = 0
) -> str:
    """Convert dict to a header-value pair, or a header-value pair where values can be tables."""
    # indentation = indent * " "
    if indent > 1:
        raise TypeError("Formatters will remove leading space on tables.")

    # Extract the keys and values from the dictionary
    keys = list(data.keys())
    # values = list(data.values())

    # Determine the maximum length of each key and value
    # max_key_length = max(len(str(key)) for key in keys)

    # why not used?
    # max_value_length = max(len(str(value)) for value in values)

    if not column_widths:
        column_widths = {key: 0 for key in data}
        for key, value in data.items():
            # TODO: doesn't handle complex types (and maybe can't? markdown doesn't support nested tables, AFAIK)
            max_width = max(len(str(key)), len(str(value)))
            column_widths[key] = max(column_widths[key], max_width)

    # Build the header row
    header = ""
    separator = ""
    if include_header:
        header = "| " + " | ".join([str(key).ljust(column_widths[key]) for key in keys]) + " |\n"
        separator = "| " + " | ".join(["-" * column_widths[key] for key in keys]) + " |\n"

    # Build the rows of the table
    row = "| "
    row += " | ".join(str(value).ljust(column_widths[key]) for key, value in data.items())
    row += " |\n"

    # Combine the header, separator, and rows into a single table
    if include_header:
        table = header + separator + row
    else:
        table = row

    return f"{table}"


def parse_table_to_list_of_dict(md_table: str) -> ListTypes:
    """Treat tables as list of dictionaries"""
    tuple_stuff = parse_table_with_regex(md_table)
    headers = tuple_stuff[0]
    rows = tuple_stuff[1:]
    dict_stuff = []
    for row in rows:
        dict_row = {}
        for column_id, column in enumerate(row):
            dict_row[headers[column_id]] = column
        dict_stuff.append(dict_row)
    # mypy complains, but list[dict[str,str]] is a subtype of ListTypes!
    return cast(ListTypes, dict_stuff)


def parse_table_with_regex(md_table: str) -> ColumnsValuesTableType:
    """
    Created by ChatGPT 3.5 Turbo model.

    First element is headers, subsequent elements are rows.
    """
    rows = md_table.strip().split("\n")
    # Get the column names from the first row
    col_names = [r.strip() for r in rows[0].strip().split("|")]
    # Ignore before the first and after the last pipe mark
    col_names = col_names[1:-1]
    num_cols = len(col_names)
    # Initialize the table data as a list of empty lists
    table_data: list[list[str]] = [[] for i in range(num_cols)]
    # Parse the remaining rows
    for row in rows[2:]:
        # Split the row into cells
        # cells = re.findall(r"\| *([^\|\n]+?) *", row)
        cells = [_.strip() for _ in row.strip().split("|")[1:-1]]
        # Check that the row has the correct number of cells
        if len(cells) != num_cols:
            raise ValueError(f"Row has {len(cells)} cells, but expected {num_cols}")
        # Add each cell to the appropriate column in the table data
        for i, cell in enumerate(cells):
            table_data[i].append(cell)
    # Combine the column names with the table data and return the result
    return [col_names] + list(zip(*table_data, strict=True))


def parse_table(md_table: str) -> ColumnsValuesTableType:
    """
    Created by ChatGPT 3.5 Turbo model
    """
    rows = md_table.strip().split("\n")
    # Get the column names from the first row
    col_names = [cell.strip() for cell in rows[0].split("|")[1:-1]]
    num_cols = len(col_names)
    # Initialize the table data as a list of empty lists
    table_data: list[list[str]] = [[] for _ in range(num_cols)]
    # Parse the remaining rows
    for row in rows[2:]:
        # Split the row into cells
        cells = [cell.strip() for cell in row.split("|")[1:-1]]
        # Check that the row has the correct number of cells
        if len(cells) != num_cols:
            raise ValueError(f"Row has {len(cells)} cells, but expected {num_cols}")
        # Add each cell to the appropriate column in the table data
        for i, cell in enumerate(cells):
            table_data[i].append(cell)
    # Combine the column names with the table data and return the result
    return [col_names] + list(zip(*table_data, strict=True))
