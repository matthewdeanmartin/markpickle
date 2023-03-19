# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import datetime
import typing

from hypothesis import given
from hypothesis import strategies as st

import markpickle.third_party_tables


@given(value=st.lists(st.lists(st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()))))
def test_fuzz_to_table_tablulate_style(value: list[list[typing.Union[None, str, int, float, datetime.date]]]) -> None:
    markpickle.third_party_tables.to_table_tablulate_style(value=value)
