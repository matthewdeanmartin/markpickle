import datetime
import io
import typing

from hypothesis import given
from hypothesis import strategies as st

import markpickle.config_class
import markpickle.serialize


@given(
    builder=st.just(io.StringIO()),
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
    indent=st.integers(),
    header_level=st.integers(),
)
def test_fuzz_render_dict(
    builder: io.IOBase,
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
    config: markpickle.config_class.Config,
    indent: int,
    header_level: int,
) -> None:
    markpickle.serialize.render_dict(
        builder=builder,
        value=value,
        config=config,
        indent=indent,
        header_level=header_level,
    )


@given(
    builder=st.just(io.StringIO()),
    value=st.lists(
        st.one_of(
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
        )
    ),
    config=st.just(markpickle.config_class.Config()),
    indent=st.integers(),
    header_level=st.integers(),
)
def test_fuzz_render_list(
    builder: io.IOBase,
    value: list[
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
        ]
    ],
    config: markpickle.config_class.Config,
    indent: int,
    header_level: int,
) -> None:
    markpickle.serialize.render_list(
        builder=builder,
        value=value,
        config=config,
        indent=indent,
        header_level=header_level,
    )
