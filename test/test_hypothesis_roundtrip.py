from __future__ import annotations

import datetime
from typing import Any

from hypothesis import given, strategies as st

import markpickle

# Strategy for scalars that should round-trip cleanly as strings
scalar_roundtrip_st = st.one_of(
    st.none(),
    st.booleans(),
    st.text(min_size=1).filter(lambda x: not any(c in x for c in "#-*|>[]()`\n")),  # Avoid MD control chars for now
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.dates(),
)


def serializable_strategy():
    return st.recursive(
        scalar_roundtrip_st,
        lambda children: st.one_of(
            st.lists(children, min_size=1),
            st.dictionaries(
                st.text(min_size=1).filter(lambda x: ":" not in x and not x.startswith("#")), children, min_size=1
            ),
        ),
        max_leaves=10,
    )


@given(data=serializable_strategy())
def test_round_trip_with_inference(data: Any) -> None:
    # Use config that enables inference
    config = markpickle.Config(infer_scalar_types=True)

    # markpickle tends to treat a list as the root document if it's the only thing there.
    # If data is already a list, dumps(data) will be a list.
    # If data is a scalar, dumps(data) will be a scalar.

    serialized = markpickle.dumps(data, config=config)
    deserialized = markpickle.loads(serialized, config=config)

    # Normalize: markpickle.loads might return None for empty-ish inputs
    if data == [] and deserialized is None:
        return

    # Normalize: markpickle might return a single item list as a scalar or vice-versa
    # depending on formatting. This is one of the "lossy" aspects.
    # But for a basic round trip, we expect equality.
    assert deserialized == data


@given(data=serializable_strategy())
def test_round_trip_as_strings(data: Any) -> None:
    # Most reliable way: everything is a string
    config = markpickle.Config(infer_scalar_types=False)

    # Helper to convert everything to string-like representation for comparison
    def stringify(val: Any) -> Any:
        if val is None:
            return None
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float, datetime.date)):
            return str(val)
        if isinstance(val, list):
            return [stringify(i) for i in val]
        if isinstance(val, dict):
            return {str(k): stringify(v) for k, v in val.items()}
        return val

    expected = stringify(data)

    serialized = markpickle.dumps(data, config=config)
    deserialized = markpickle.loads(serialized, config=config)

    if data == [] and deserialized is None:
        return

    assert deserialized == expected
