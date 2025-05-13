# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import datetime
import io
import typing

from hypothesis import given
from hypothesis import strategies as st

import markpickle.config_class
import markpickle.serialize

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
    markpickle.serialize.Config(
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


@given(
    value=st.one_of(
        st.none(),
        st.dates(),
        st.floats(),
        st.integers(),
        st.dictionaries(
            keys=st.text(),
            values=st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()),
        ),
        st.dictionaries(
            keys=st.text(),
            values=st.one_of(
                st.none(),
                st.dates(),
                st.floats(),
                st.integers(),
                st.dictionaries(
                    keys=st.text(),
                    values=st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()),
                ),
                st.lists(st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text())),
                st.text(),
            ),
        ),
        st.lists(st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text())),
        st.lists(
            st.dictionaries(
                keys=st.text(),
                values=st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()),
            )
        ),
        st.text(),
    ),
    stream=st.just(io.StringIO()),
    config=st.just(markpickle.config_class.Config()),
)
def test_fuzz_dump(
    value: typing.Union[
        None,
        str,
        int,
        float,
        datetime.date,
        dict[str, typing.Union[None, str, int, float, datetime.date]],
        dict[
            str,
            typing.Union[
                None,
                str,
                int,
                float,
                datetime.date,
                list[typing.Union[None, str, int, float, datetime.date]],
                dict[str, typing.Union[None, str, int, float, datetime.date]],
            ],
        ],
        list[typing.Union[None, str, int, float, datetime.date]],
        list[dict[str, typing.Union[None, str, int, float, datetime.date]]],
    ],
    stream: io.IOBase,
    config: typing.Optional[markpickle.config_class.Config],
) -> None:
    markpickle.serialize.dump(value=value, stream=stream, config=config)


@given(
    value=st.one_of(
        st.none(),
        st.dates(),
        st.floats(),
        st.integers(),
        st.dictionaries(
            keys=st.text(),
            values=st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()),
        ),
        st.dictionaries(
            keys=st.text(),
            values=st.one_of(
                st.none(),
                st.dates(),
                st.floats(),
                st.integers(),
                st.dictionaries(
                    keys=st.text(),
                    values=st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()),
                ),
                st.lists(st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text())),
                st.text(),
            ),
        ),
        st.lists(st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text())),
        st.lists(
            st.dictionaries(
                keys=st.text(),
                values=st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()),
            )
        ),
        st.text(),
    ),
    config=st.just(markpickle.config_class.Config()),
)
def test_fuzz_dumps(
    value: typing.Union[
        None,
        str,
        int,
        float,
        datetime.date,
        dict[str, typing.Union[None, str, int, float, datetime.date]],
        dict[
            str,
            typing.Union[
                None,
                str,
                int,
                float,
                datetime.date,
                list[typing.Union[None, str, int, float, datetime.date]],
                dict[str, typing.Union[None, str, int, float, datetime.date]],
            ],
        ],
        list[typing.Union[None, str, int, float, datetime.date]],
        list[dict[str, typing.Union[None, str, int, float, datetime.date]]],
    ],
    config: typing.Optional[markpickle.config_class.Config],
) -> None:
    markpickle.serialize.dumps(value=value, config=config)


@given(value=st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()))
def test_fuzz_unsafe_falsy_type(value: typing.Union[None, str, int, float, datetime.date]) -> None:
    markpickle.serialize.unsafe_falsy_type(value=value)


@given(value=st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text()))
def test_fuzz_unsafe_scalar_type(value: typing.Union[None, str, int, float, datetime.date]) -> None:
    markpickle.serialize.unsafe_scalar_type(value=value)
