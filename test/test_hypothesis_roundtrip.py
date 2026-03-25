from __future__ import annotations

import datetime
from typing import Any

from hypothesis import assume, given, settings, strategies as st

import markpickle

# Safe text: no markdown control chars, no whitespace, no backslashes
# (backslashes get un-escaped by markdown parsers)
safe_text_st = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs", "Zs", "Cc"),  # No surrogates, spaces, control chars
        blacklist_characters="#-*+|>[]()`\n\r\x00:\\/_",
    ),
    min_size=1,
)

# Safe dict keys
safe_key_st = safe_text_st.filter(lambda x: not x.startswith("#") and x.strip())


def _looks_numeric(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


# Scalars that round-trip with infer_scalar_types=True
scalar_inference_st = st.one_of(
    st.none(),
    st.booleans(),
    safe_text_st.filter(lambda x: x not in ("True", "true", "False", "false", "None", "nil") and not _looks_numeric(x)),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.dates(),
)

# Scalars that round-trip with infer_scalar_types=False
# Dates are excluded: with infer_scalar_types=False, dates still get inferred back
scalar_strings_st = st.one_of(
    st.none(),
    st.booleans(),
    safe_text_st.filter(lambda x: x not in ("True", "true", "False", "false", "None", "nil") and not _looks_numeric(x)),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
)


def _is_safe_list(lst: list) -> bool:
    """Only allow lists that markpickle can safely round-trip."""
    if not lst:
        return True
    has_dict = any(isinstance(x, dict) for x in lst)
    has_non_dict = any(not isinstance(x, dict) for x in lst)
    # Mixed lists (dict + non-dict) cause table serialization errors
    if has_dict and has_non_dict:
        return False
    # Nested lists lose a nesting level during round-trip
    if any(isinstance(x, list) for x in lst):
        return False
    # Lists of dicts must have uniform keys (otherwise table has jagged rows)
    if has_dict:
        key_sets = [frozenset(d.keys()) for d in lst]
        if len(set(key_sets)) > 1:
            return False
    return True


def _dict_has_only_scalar_values(d: dict) -> bool:
    """Dicts with list/dict values don't round-trip cleanly.

    Known limitations:
    - Dict values that are lists serialize as nested bullet lists, losing the key.
    - Nested dicts only work at the 1st level (known bug).
    """
    return not any(isinstance(v, (list, dict)) for v in d.values())


def serializable_strategy(scalar_st):
    return st.recursive(
        scalar_st,
        lambda children: st.one_of(
            st.lists(children, min_size=1).filter(_is_safe_list),
            st.dictionaries(safe_key_st, children, min_size=1).filter(_dict_has_only_scalar_values),
        ),
        max_leaves=8,
    )


def _has_none_in_collection(data: Any) -> bool:
    """Returns True if any dict value or list element (nested) is None."""
    if data is None:
        return True
    if isinstance(data, dict):
        for v in data.values():
            if _has_none_in_collection(v):
                return True
    if isinstance(data, list):
        for item in data:
            if _has_none_in_collection(item):
                return True
    return False


@given(data=serializable_strategy(scalar_inference_st))
@settings(max_examples=100)
def test_round_trip_with_inference(data: Any) -> None:
    # Skip inputs with None inside dicts — table cells don't preserve None type
    # (known limitation: parse_table_to_list_of_dict doesn't infer cell types
    # when the serialized table has inconsistent columns with None)
    assume(not _has_none_in_collection(data))

    config = markpickle.Config(infer_scalar_types=True)

    serialized = markpickle.dumps(data, config=config)
    deserialized = markpickle.loads(serialized, config=config)

    if data == [] and deserialized is None:
        return

    assert deserialized == data


@given(data=serializable_strategy(scalar_strings_st))
@settings(max_examples=100)
def test_round_trip_as_strings(data: Any) -> None:
    # Skip inputs with None inside dicts — table cells don't preserve None type
    assume(not _has_none_in_collection(data))

    config = markpickle.Config(infer_scalar_types=False)

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
