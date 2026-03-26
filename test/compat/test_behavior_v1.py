from __future__ import annotations

import pytest

import markpickle

from test.compat.helpers import evaluate_case, load_fixture

BEHAVIOR_SNAPSHOT = load_fixture("behavior_snapshot.json")


@pytest.mark.compat
@pytest.mark.parametrize("case", BEHAVIOR_SNAPSHOT["cases"], ids=[case["id"] for case in BEHAVIOR_SNAPSHOT["cases"]])
def test_v1_behavior_cases(case: dict[str, object]) -> None:
    actual = evaluate_case(markpickle, case)
    assert actual == case["baseline_expected"]
