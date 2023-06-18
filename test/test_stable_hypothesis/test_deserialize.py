# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import typing

import _io
from _io import StringIO
from hypothesis import given
from hypothesis import strategies as st

import markpickle.config_class
import markpickle.deserialize

# TODO: replace st.nothing() with appropriate strategies


@given(
    infer_scalar_types=st.booleans(),
    true_values=st.lists(st.text()),
    false_values=st.lists(st.text()),
    none_values=st.lists(st.text()),
    empty_string_is=st.text(),
    serialize_headers_are_dict_keys=st.booleans(),
    serialize_dict_as_table=st.booleans(),
    serialize_child_dict_as_table=st.booleans(),
    serialize_tables_tabulate_style=st.booleans(),
    none_string=st.text(),
    serialize_date_format=st.text(),
    serialized_datetime_format=st.text(),
)
def test_fuzz_Config(
    infer_scalar_types: bool,
    true_values: list[str],
    false_values: list[str],
    none_values: list[str],
    empty_string_is: str,
    serialize_headers_are_dict_keys: bool,
    serialize_dict_as_table: bool,
    serialize_child_dict_as_table: bool,
    serialize_tables_tabulate_style: bool,
    none_string: str,
    serialize_date_format: str,
    serialized_datetime_format: str,
) -> None:
    markpickle.deserialize.Config(
        infer_scalar_types=infer_scalar_types,
        true_values=true_values,
        false_values=false_values,
        none_values=none_values,
        empty_string_is=empty_string_is,
        serialize_headers_are_dict_keys=serialize_headers_are_dict_keys,
        serialize_dict_as_table=serialize_dict_as_table,
        serialize_child_dict_as_table=serialize_child_dict_as_table,
        serialize_tables_tabulate_style=serialize_tables_tabulate_style,
        none_string=none_string,
        serialize_date_format=serialize_date_format,
        serialized_datetime_format=serialized_datetime_format,
    )


@given(value=st.text(), config=st.just(markpickle.config_class.Config()))
def test_fuzz_extract_scalar(value: str, config: markpickle.config_class.Config) -> None:
    markpickle.deserialize.extract_scalar(value=value, config=config)


@given(value=st.text())
def test_fuzz_is_float(value: str) -> None:
    markpickle.deserialize.is_float(value=value)


@given(
    value=st.builds(StringIO),
    config=st.from_type(typing.Optional[markpickle.config_class.Config]),
)
def test_fuzz_load(value: _io.StringIO, config: typing.Optional[markpickle.config_class.Config]) -> None:
    markpickle.deserialize.load(value=value, config=config)


# no factory for a mistune AST
# @given(list_ast=st.from_type(Any), config=st.just(markpickle.config_class.Config()))
# def test_fuzz_process_list(
#     list_ast: typing.Any, config: markpickle.config_class.Config
# ) -> None:
#     markpickle.deserialize.process_list(list_ast=list_ast, config=config)
