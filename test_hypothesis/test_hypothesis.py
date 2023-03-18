# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import datetime
import markpickle
import markpickle.deserialize
import markpickle.serialize
import typing
from hypothesis import given, strategies as st
from markpickle import DeserializationConfig, SerializationConfig


@given(
    config=st.one_of(
        st.none(),
        st.builds(
            SerializationConfig,
            child_dict_as_table=st.one_of(st.just(True), st.booleans()),
            dict_as_table=st.one_of(st.just(False), st.booleans()),
            headers_are_dict_keys=st.one_of(st.just(True), st.booleans()),
        ),
        st.from_type(typing.Optional[markpickle.deserialize.DeserializationConfig]),
    ),
    root=st.one_of(st.none(), st.text()),
    value=st.one_of(
        st.none(),
        st.dates(),
        st.floats(),
        st.integers(),
        st.dictionaries(
            keys=st.text(),
            values=st.one_of(
                st.none(), st.dates(), st.floats(), st.integers(), st.text()
            ),
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
                    values=st.one_of(
                        st.none(), st.dates(), st.floats(), st.integers(), st.text()
                    ),
                ),
                st.lists(
                    st.one_of(
                        st.none(), st.dates(), st.floats(), st.integers(), st.text()
                    )
                ),
                st.text(),
            ),
        ),
        st.lists(
            st.one_of(st.none(), st.dates(), st.floats(), st.integers(), st.text())
        ),
        st.lists(
            st.dictionaries(
                keys=st.text(),
                values=st.one_of(
                    st.none(), st.dates(), st.floats(), st.integers(), st.text()
                ),
            )
        ),
        st.text(),
    ),
)
def test_roundtrip_dumps_loads(
        config: typing.Union[
            typing.Optional[markpickle.deserialize.DeserializationConfig],
            typing.Optional[markpickle.serialize.SerializationConfig],
        ],
        root: typing.Optional[str],
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
    if value in ([],{},(),"","0",None):
        # falsies will not roundtrip. 
        return
    value0 = markpickle.dumps(value=value, root=root, config=config)
    value1 = markpickle.loads(value=value0, config=config)
    assert value == value1, (value, value1)


@given(
    infer_scalar_types=st.booleans(),
    true_values=st.lists(st.text()),
    false_values=st.lists(st.text()),
    none_values=st.lists(st.text()),
    empty_string_is=st.just(""),
    root=st.one_of(st.none(), st.text()),
)
def test_fuzz_DeserializationConfig(
        infer_scalar_types: bool,
        true_values: list[str],
        false_values: list[str],
        none_values: list[str],
        empty_string_is: str,
        root: typing.Optional[str],
) -> None:
    markpickle.DeserializationConfig(
        infer_scalar_types=infer_scalar_types,
        true_values=true_values,
        false_values=false_values,
        none_values=none_values,
        empty_string_is=empty_string_is,
        root=root,
    )


@given(
    headers_are_dict_keys=st.booleans(),
    dict_as_table=st.booleans(),
    child_dict_as_table=st.booleans(),
)
def test_fuzz_SerializationConfig(
        headers_are_dict_keys: bool, dict_as_table: bool, child_dict_as_table: bool
) -> None:
    markpickle.SerializationConfig(
        headers_are_dict_keys=headers_are_dict_keys,
        dict_as_table=dict_as_table,
        child_dict_as_table=child_dict_as_table,
    )
