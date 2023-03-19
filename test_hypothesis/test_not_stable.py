import datetime
import io
import typing

from hypothesis import given
from hypothesis import strategies as st

import markpickle.config_class
import markpickle.deserialize


@given(
    value=st.text(),
    config=st.from_type(typing.Optional[markpickle.config_class.Config]),
)
def test_fuzz_loads(value: str, config: typing.Optional[markpickle.config_class.Config]) -> None:
    markpickle.deserialize.loads(value=value, config=config)


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
