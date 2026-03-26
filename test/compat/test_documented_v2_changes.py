from __future__ import annotations

import pytest

import markpickle

from test.compat.helpers import evaluate_case, load_fixture

DOCUMENTED_CHANGES = load_fixture("documented_changes.json")


@pytest.mark.documented_change
@pytest.mark.parametrize(
    "case",
    DOCUMENTED_CHANGES["cases"],
    ids=[case["id"] for case in DOCUMENTED_CHANGES["cases"]],
)
def test_documented_v2_changes_are_explicit(case: dict[str, object]) -> None:
    actual = evaluate_case(markpickle, case)
    baseline = case["baseline_expected"]
    assert actual == case["current_expected"]
    assert actual != baseline or type(actual) is not type(baseline)
