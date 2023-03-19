"""
Use 3rd party library to create tables
"""
import tabulate

from markpickle.mypy_types import ScalarTypes


# from pytablewriter import MarkdownTableWriter
#
# def main():
#     writer = MarkdownTableWriter(
#         table_name="example_table",
#         headers=["int", "float", "str", "bool", "mix", "time"],
#         value_matrix=[
#             [0,   0.1,      "hoge", True,   0,      "2017-01-01 03:04:05+0900"],
#             [2,   "-2.23",  "foo",  False,  None,   "2017-12-23 45:01:23+0900"],
#             [3,   0,        "bar",  "true",  "inf", "2017-03-03 33:44:55+0900"],
#             [-10, -9.9,     "",     "FALSE", "nan", "2017-01-01 00:00:00+0900"],
#         ],
#     )
#     writer.write_table()
def to_table_tablulate_style(value: list[list[ScalarTypes]]):
    """
    The following tabular data types are supported:

    list of lists or another iterable of iterables
    list or another iterable of dicts (keys as columns)
    dict of iterables (keys as columns)
    list of dataclasses (Python 3.7+ only, field names as columns)
    two-dimensional NumPy array
    NumPy record arrays (names as columns)
    pandas.DataFrame
    """
    return tabulate.tabulate(value, tablefmt="github")
