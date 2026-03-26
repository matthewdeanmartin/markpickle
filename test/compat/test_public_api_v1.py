from __future__ import annotations

import markpickle

from test.compat.helpers import (
    assert_signature_compatible,
    current_config_fields,
    load_fixture,
    signature_contract,
)

API_SNAPSHOT = load_fixture("api_snapshot.json")


def test_v1_exports_remain_in_public_api() -> None:
    current_exports = set(markpickle.__all__)
    missing_exports = [name for name in API_SNAPSHOT["exports"] if name not in current_exports]
    assert missing_exports == []


def test_v1_exports_remain_importable() -> None:
    missing_attributes = [name for name in API_SNAPSHOT["exports"] if not hasattr(markpickle, name)]
    assert missing_attributes == []


def test_v1_function_contracts_remain_compatible() -> None:
    for name, baseline_contract in API_SNAPSHOT["function_contracts"].items():
        current_contract = signature_contract(getattr(markpickle, name))
        assert_signature_compatible(current_contract, baseline_contract)


def test_v1_config_fields_remain_constructor_compatible() -> None:
    baseline_fields = API_SNAPSHOT["config_fields"]
    current_fields = current_config_fields(markpickle)
    assert current_fields[: len(baseline_fields)] == baseline_fields
