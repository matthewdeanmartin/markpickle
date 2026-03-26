from __future__ import annotations

import base64
import dataclasses
import datetime as dt
import inspect
import io
import json
from pathlib import Path
from typing import Any

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "v1_6_4"


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def decode_value(value: Any) -> Any:
    if isinstance(value, list):
        return [decode_value(item) for item in value]
    if not isinstance(value, dict):
        return value

    value_type = value.get("__type__")
    if value_type == "datetime":
        return dt.datetime.fromisoformat(value["value"])
    if value_type == "date":
        return dt.date.fromisoformat(value["value"])
    if value_type == "bytes":
        return base64.b64decode(value["value"])
    if value_type == "tuple":
        return tuple(decode_value(item) for item in value["items"])
    return {key: decode_value(item) for key, item in value.items()}


def normalize_value(value: Any) -> Any:
    if isinstance(value, dt.datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, dt.date):
        return {"__type__": "date", "value": value.isoformat()}
    if isinstance(value, tuple):
        return {"__type__": "tuple", "items": [normalize_value(item) for item in value]}
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): normalize_value(item) for key, item in value.items()}
    return value


def build_config(markpickle_module: Any, case: dict[str, Any]) -> Any | None:
    overrides = case.get("config", {})
    if not overrides:
        return None
    config = markpickle_module.Config()
    for name, value in overrides.items():
        setattr(config, name, decode_value(value))
    return config


def evaluate_case(markpickle_module: Any, case: dict[str, Any]) -> Any:
    config = build_config(markpickle_module, case)
    payload = decode_value(case["input"])
    operation = case["operation"]

    if operation == "loads":
        return normalize_value(markpickle_module.loads(payload, config=config))
    if operation == "dumps":
        return normalize_value(markpickle_module.dumps(payload, config=config))
    if operation == "loads_all":
        return normalize_value(list(markpickle_module.loads_all(payload, config=config)))
    if operation == "dumps_all":
        return normalize_value(markpickle_module.dumps_all(payload, config=config))
    if operation == "dump_all":
        stream = io.StringIO()
        markpickle_module.dump_all(payload, stream, config=config)
        return normalize_value(stream.getvalue())
    if operation == "split_file":
        return normalize_value(list(markpickle_module.split_file(io.BytesIO(payload))))

    msg = f"Unknown operation {operation!r}"
    raise ValueError(msg)


def current_config_fields(markpickle_module: Any) -> list[str]:
    return [field.name for field in dataclasses.fields(markpickle_module.Config)]


def signature_contract(callable_obj: Any) -> list[dict[str, Any]]:
    signature = inspect.signature(callable_obj)
    contract: list[dict[str, Any]] = []
    for parameter in signature.parameters.values():
        contract.append(
            {
                "name": parameter.name,
                "kind": parameter.kind.name,
                "required": parameter.default is inspect.Signature.empty,
            }
        )
    return contract


def assert_signature_compatible(current: list[dict[str, Any]], baseline: list[dict[str, Any]]) -> None:
    assert len(current) >= len(baseline)
    assert current[: len(baseline)] == baseline
    for parameter in current[len(baseline) :]:
        assert parameter["required"] is False
