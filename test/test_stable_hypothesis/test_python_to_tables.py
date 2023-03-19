# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.


from hypothesis import given
from hypothesis import strategies as st

import markpickle.python_to_tables

# TODO: replace st.nothing() with an appropriate strategy

#
# @given(
#     data=st.one_of(
#         st.dictionaries(
#             keys=st.text(),
#             values=st.one_of(
#                 st.none(), st.dates(), st.floats(), st.integers(), st.text()
#             ),
#         ),
#         st.dictionaries(
#             keys=st.text(),
#             values=st.one_of(
#                 st.none(),
#                 st.dates(),
#                 st.floats(),
#                 st.integers(),
#                 st.dictionaries(
#                     keys=st.text(),
#                     values=st.one_of(
#                         st.none(), st.dates(), st.floats(), st.integers(), st.text()
#                     ),
#                 ),
#                 st.lists(
#                     st.one_of(
#                         st.none(), st.dates(), st.floats(), st.integers(), st.text()
#                     )
#                 ),
#                 st.text(),
#             ),
#         ),
#     ),
#     include_header=st.booleans(),
#     column_widths=st.one_of(
#         st.none(), st.dictionaries(keys=st.text(), values=st.integers())
#     ),
#     indent=st.integers(),
# )
# def test_fuzz_dict_to_markdown(
#     data: typing.Union[
#         dict[str, typing.Union[None, str, int, float, datetime.date]],
#         dict[
#             str,
#             typing.Union[
#                 None,
#                 str,
#                 int,
#                 float,
#                 datetime.date,
#                 list[typing.Union[None, str, int, float, datetime.date]],
#                 dict[str, typing.Union[None, str, int, float, datetime.date]],
#             ],
#         ],
#     ],
#     include_header: bool,
#     column_widths: typing.Optional[dict[str, int]],
#     indent: int,
# ) -> None:
#     markpickle.python_to_tables.dict_to_markdown(
#         data=data,
#         include_header=include_header,
#         column_widths=column_widths,
#         indent=indent,
#     )


# fails on memory error?!
# @given(
#     builder=st.just(io.StringIO()),
#     data=st.lists(
#         st.dictionaries(
#             keys=st.text(),
#             values=st.one_of(
#                 st.none(), st.dates(), st.floats(), st.integers(), st.text()
#             ),
#         )
#     ),
#     indent=st.integers(),
# )
# def test_fuzz_list_of_dict_to_markdown(
#     builder: io.IOBase,
#     data: list[dict[str, typing.Union[None, str, int, float, datetime.date]]],
#     indent: int,
# ) -> None:
#     markpickle.python_to_tables.list_of_dict_to_markdown(
#         builder=builder, data=data, indent=indent
#     )


@given(md_table=st.text())
def test_fuzz_parse_table(md_table) -> None:
    markpickle.python_to_tables.parse_table(md_table=md_table)


@given(md_table=st.text())
def test_fuzz_parse_table_with_regex(md_table: str) -> None:
    markpickle.python_to_tables.parse_table_with_regex(md_table=md_table)
