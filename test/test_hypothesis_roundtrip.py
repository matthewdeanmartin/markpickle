from __future__ import annotations

import datetime
from typing import Any

from hypothesis import given, strategies as st, assume, settings

import markpickle

# Exclude None since it doesn't round-trip (serializes to empty string)
# Also exclude whitespace-only strings and strings with control chars
_MD_UNSAFE = set("#-*|>[]()`\n\r\t_~")


def _safe_text():
    return st.text(min_size=1).filter(
        lambda x: not any(c in x for c in _MD_UNSAFE)
        and x.strip() == x
        and x.strip()
        # Avoid strings that look like other types (would be inferred differently)
        and not x.isdigit()
        and x not in ("True", "true", "False", "false", "None", "nil")
    )


scalar_roundtrip_st = st.one_of(
    st.booleans(),
    _safe_text(),
    st.integers(min_value=0),  # Only non-negative ints (negative was buggy pre-2.0)
    st.floats(allow_nan=False, allow_infinity=False, min_value=0),
    st.dates(),
)


def serializable_strategy():
    return st.recursive(
        scalar_roundtrip_st,
        lambda children: st.one_of(
            # Only flat lists (nested lists can flatten)
            st.lists(children.filter(lambda x: not isinstance(x, (list, dict))), min_size=1),
            st.dictionaries(
                _safe_text().filter(lambda x: ":" not in x),
                children.filter(lambda x: not isinstance(x, (list, dict))),
                min_size=1,
            ),
        ),
        max_leaves=5,
    )


@given(data=serializable_strategy())
def test_round_trip_with_inference(data: Any) -> None:
    config = markpickle.Config(infer_scalar_types=True)

    serialized = markpickle.dumps(data, config=config)
    deserialized = markpickle.loads(serialized, config=config)

    if data == [] and deserialized is None:
        return

    assert deserialized == data


@given(data=serializable_strategy())
def test_round_trip_as_strings(data: Any) -> None:
    config = markpickle.Config(infer_scalar_types=False)

    def stringify(val: Any) -> Any:
        if val is None:
            return "None"
        if isinstance(val, bool):
            return str(val)
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
