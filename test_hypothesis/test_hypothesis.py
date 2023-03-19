# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import datetime
import io
import typing
from io import IOBase

import _io
from _io import StringIO
from hypothesis import given
from hypothesis import strategies as st

import markpickle
import markpickle.config_class
from markpickle import Config
from markpickle.config_class import unsafe_falsy_type, unsafe_scalar_type


@given(
    # config class creates garbage if messed up
    config=st.just(
        markpickle.config_class.Config(infer_scalar_types=False)
    ),  # .from_type(typing.Optional[markpickle.config_class.Config]),
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
)
def test_roundtrip_dumps_loads(
    config: typing.Optional[markpickle.config_class.Config],
    value: typing.Union[
        typing.Union[
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
        str,
    ],
) -> None:
    if unsafe_falsy_type(value):
        # falsies will not roundtrip.
        return
    if unsafe_scalar_type(value):
        # non-strings will not roundtrip.
        return

    value0 = markpickle.dumps(value=value, config=config)
    value1 = markpickle.loads(value=value0, config=config)
    if value != value1:
        print("whoa")
    assert value == value1, (value, value1)


@given(
    infer_scalar_types=st.booleans(),
    true_values=st.lists(st.text()),
    false_values=st.lists(st.text()),
    none_values=st.lists(st.text()),
    empty_string_is=st.text(),
    serialize_headers_are_dict_keys=st.booleans(),
    serialize_dict_as_table=st.booleans(),
    serialize_child_dict_as_table=st.booleans(),
    none_string=st.text(),
    serialize_run_formatter=st.booleans(),
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
    none_string: str,
    serialize_run_formatter: bool,
) -> None:
    markpickle.Config(
        infer_scalar_types=infer_scalar_types,
        true_values=true_values,
        false_values=false_values,
        none_values=none_values,
        empty_string_is=empty_string_is,
        serialize_headers_are_dict_keys=serialize_headers_are_dict_keys,
        serialize_dict_as_table=serialize_dict_as_table,
        serialize_child_dict_as_table=serialize_child_dict_as_table,
        none_string=none_string,
        serialize_run_formatter=serialize_run_formatter,
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
    stream=st.just(io.StringIO),
    config=st.from_type(typing.Optional[markpickle.config_class.Config]),
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
    markpickle.dump(value=value, stream=stream, config=config)


@given(
    value=st.builds(StringIO),
    config=st.from_type(typing.Optional[markpickle.config_class.Config]),
)
def test_fuzz_load(value: _io.StringIO, config: typing.Optional[markpickle.config_class.Config]) -> None:
    markpickle.load(value=value, config=config)
