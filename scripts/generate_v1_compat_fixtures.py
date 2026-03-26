"""Generate and validate the frozen 1.6.4 compatibility fixtures."""

from __future__ import annotations

import argparse
import base64
import dataclasses
import datetime as dt
import inspect
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "test" / "compat" / "fixtures" / "v1_6_4"
BASELINE_REF = "c80c4c4"
BASELINE_VERSION = "1.6.4"
BASELINE_VENV = ROOT / ".venv-compat-1.6.4"
WHEEL_VENV = ROOT / ".venv-compat-wheel"
GIT_EXE = shutil.which("git")
UV_EXE = shutil.which("uv")

API_FUNCTIONS = [
    "load",
    "load_all",
    "loads",
    "loads_all",
    "dump",
    "dump_all",
    "dumps",
    "dumps_all",
    "split_file",
    "convert_json_to_markdown",
    "convert_markdown_to_json",
]

BEHAVIOR_CASES: list[dict[str, Any]] = [
    {
        "id": "dumps_string",
        "description": "Serialize a plain string.",
        "operation": "dumps",
        "input": "hello",
    },
    {
        "id": "loads_int",
        "description": "Deserialize an integer scalar.",
        "operation": "loads",
        "input": "42",
    },
    {
        "id": "loads_bool_true",
        "description": "Deserialize a boolean scalar.",
        "operation": "loads",
        "input": "True",
    },
    {
        "id": "loads_date",
        "description": "Deserialize an ISO date scalar.",
        "operation": "loads",
        "input": "2024-01-15",
    },
    {
        "id": "dumps_list",
        "description": "Serialize a simple list.",
        "operation": "dumps",
        "input": ["a", "b"],
    },
    {
        "id": "loads_list",
        "description": "Deserialize a simple list.",
        "operation": "loads",
        "input": "- a\n- b\n",
    },
    {
        "id": "dumps_dict",
        "description": "Serialize a flat dict with the default ATX format.",
        "operation": "dumps",
        "input": {"Name": "Ringo", "Species": "Felix"},
    },
    {
        "id": "loads_dict",
        "description": "Deserialize a flat ATX-header dict.",
        "operation": "loads",
        "input": "# Name\n\nRingo\n\n# Species\n\nFelix\n",
    },
    {
        "id": "loads_infer_scalar_types_false",
        "description": "Keep numeric text as a string when inference is disabled.",
        "operation": "loads",
        "input": "42",
        "config": {"infer_scalar_types": False},
    },
    {
        "id": "dumps_all_two_documents",
        "description": "Serialize multiple documents with the string helper.",
        "operation": "dumps_all",
        "input": [{"a": "1"}, {"b": "2"}],
    },
]

DOCUMENTED_CHANGE_CASES: list[dict[str, Any]] = [
    {
        "id": "loads_negative_int",
        "description": "Negative integers now deserialize as int instead of float.",
        "operation": "loads",
        "input": "-5",
        "reference": "CHANGELOG 2.0.0 Fixed: Negative ints become float",
    },
    {
        "id": "loads_bool_no_infer",
        "description": "infer_scalar_types=False now leaves booleans as strings.",
        "operation": "loads",
        "input": "True",
        "config": {"infer_scalar_types": False},
        "reference": "CHANGELOG 2.0.0 Breaking Changes: infer_scalar_types=False now truly returns strings",
    },
    {
        "id": "loads_none_values_custom",
        "description": "none_values is now consulted during deserialization.",
        "operation": "loads",
        "input": "null",
        "config": {"none_values": ["None", "nil", "null", "N/A"]},
        "reference": "CHANGELOG 2.0.0 Breaking Changes: none_values config list is now consulted",
    },
    {
        "id": "dumps_datetime",
        "description": "datetime serialization now preserves the time component.",
        "operation": "dumps",
        "input": {"__type__": "datetime", "value": "2024-01-15T10:30:45"},
        "reference": "CHANGELOG 2.0.0 Fixed: datetime loses time",
    },
    {
        "id": "dump_all_two_documents",
        "description": "dump_all stream output now emits --- separators between documents.",
        "operation": "dump_all",
        "input": [{"a": "1"}, {"b": "2"}],
        "reference": "CHANGELOG 2.0.0 Fixed: dump_all stream bug",
    },
]


if GIT_EXE is None:
    raise RuntimeError("git executable not found on PATH")
if UV_EXE is None:
    raise RuntimeError("uv executable not found on PATH")


def _uv_python(venv_path: Path) -> Path:
    return venv_path / "Scripts" / "python.exe"


def _run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, check=True, text=True, capture_output=True)


def _encode_value(value: Any) -> Any:
    if isinstance(value, dt.datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, dt.date):
        return {"__type__": "date", "value": value.isoformat()}
    if isinstance(value, bytes):
        encoded = base64.b64encode(value).decode("ascii")
        return {"__type__": "bytes", "encoding": "base64", "value": encoded}
    if isinstance(value, tuple):
        return {"__type__": "tuple", "items": [_encode_value(item) for item in value]}
    if isinstance(value, list):
        return [_encode_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _encode_value(val) for key, val in value.items()}
    return value


def _decode_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode_value(item) for item in value]
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
        return tuple(_decode_value(item) for item in value["items"])
    return {key: _decode_value(val) for key, val in value.items()}


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dt.datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, dt.date):
        return {"__type__": "date", "value": value.isoformat()}
    if isinstance(value, tuple):
        return {"__type__": "tuple", "items": [_normalize_value(item) for item in value]}
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _normalize_value(val) for key, val in value.items()}
    return value


def _signature_contract(callable_obj: Any) -> list[dict[str, Any]]:
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


def _build_config(markpickle_module: Any, case: dict[str, Any]) -> Any | None:
    overrides = case.get("config", {})
    if not overrides:
        return None
    config = markpickle_module.Config()
    for name, value in overrides.items():
        setattr(config, name, _decode_value(value))
    return config


def _evaluate_case(markpickle_module: Any, case: dict[str, Any]) -> Any:
    config = _build_config(markpickle_module, case)
    payload = _decode_value(case["input"])
    operation = case["operation"]

    if operation == "loads":
        return markpickle_module.loads(payload, config=config)
    if operation == "dumps":
        return markpickle_module.dumps(payload, config=config)
    if operation == "loads_all":
        return list(markpickle_module.loads_all(payload, config=config))
    if operation == "dumps_all":
        return markpickle_module.dumps_all(payload, config=config)
    if operation == "dump_all":
        stream = io.StringIO()
        markpickle_module.dump_all(payload, stream, config=config)
        return stream.getvalue()
    if operation == "split_file":
        return list(markpickle_module.split_file(io.BytesIO(payload)))

    msg = f"Unknown operation {operation!r}"
    raise ValueError(msg)


def _capture_api_snapshot() -> dict[str, Any]:
    import markpickle

    config_fields = [field.name for field in dataclasses.fields(markpickle.Config)]
    return {
        "baseline_version": BASELINE_VERSION,
        "baseline_ref": BASELINE_REF,
        "exports": list(markpickle.__all__),
        "function_contracts": {name: _signature_contract(getattr(markpickle, name)) for name in API_FUNCTIONS},
        "config_fields": config_fields,
    }


def _capture_case_results(cases: list[dict[str, Any]]) -> dict[str, Any]:
    import markpickle

    captured_cases: list[dict[str, Any]] = []
    for case in cases:
        expected = _normalize_value(_evaluate_case(markpickle, case))
        captured_case = dict(case)
        captured_case["expected"] = expected
        captured_cases.append(captured_case)
    return {"baseline_version": BASELINE_VERSION, "baseline_ref": BASELINE_REF, "cases": captured_cases}


def _export_git_ref(ref: str, destination: Path) -> Path:
    archive_path = destination / "baseline.zip"
    subprocess.run(
        [GIT_EXE, "archive", "--format=zip", "-o", str(archive_path), ref],
        cwd=ROOT,
        check=True,
    )
    source_dir = destination / "baseline-src"
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(source_dir)
    return source_dir


def _run_capture(kind: str, *, python: Path, cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    command = [str(python), str(Path(__file__).resolve()), "capture", "--kind", kind]
    completed = _run(command, cwd=cwd, env=env)
    return json.loads(completed.stdout)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _current_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    return env


def _baseline_env(source_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(source_dir)
    return env


def create_baseline_venv() -> int:
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        source_dir = _export_git_ref(BASELINE_REF, temp_dir)
        subprocess.run([UV_EXE, "venv", "--clear", str(BASELINE_VENV)], cwd=ROOT, check=True)
        subprocess.run(
            [UV_EXE, "pip", "install", "--python", str(_uv_python(BASELINE_VENV)), str(source_dir)],
            cwd=ROOT,
            check=True,
        )
    print(f"Created {BASELINE_VENV}")
    return 0


def generate_fixtures() -> int:
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        source_dir = _export_git_ref(BASELINE_REF, temp_dir)

        baseline_api = _run_capture(
            "api",
            python=Path(sys.executable),
            cwd=temp_dir,
            env=_baseline_env(source_dir),
        )
        baseline_behavior = _run_capture(
            "behavior",
            python=Path(sys.executable),
            cwd=temp_dir,
            env=_baseline_env(source_dir),
        )
        baseline_changes = _run_capture(
            "documented-changes",
            python=Path(sys.executable),
            cwd=temp_dir,
            env=_baseline_env(source_dir),
        )

    current_changes = _run_capture(
        "documented-changes",
        python=Path(sys.executable),
        cwd=ROOT,
        env=_current_env(),
    )

    documented_changes = {
        "baseline_version": BASELINE_VERSION,
        "baseline_ref": BASELINE_REF,
        "cases": [],
    }
    for baseline_case, current_case in zip(
        baseline_changes["cases"],
        current_changes["cases"],
        strict=True,
    ):
        merged_case = dict(baseline_case)
        merged_case["baseline_expected"] = merged_case.pop("expected")
        merged_case["current_expected"] = current_case["expected"]
        documented_changes["cases"].append(merged_case)

    for case in baseline_behavior["cases"]:
        case["baseline_expected"] = case.pop("expected")

    _write_json(FIXTURE_DIR / "api_snapshot.json", baseline_api)
    _write_json(FIXTURE_DIR / "behavior_snapshot.json", baseline_behavior)
    _write_json(FIXTURE_DIR / "documented_changes.json", documented_changes)

    print(f"Wrote fixtures to {FIXTURE_DIR}")
    return 0


def run_installed_checks() -> int:
    api_snapshot = json.loads((FIXTURE_DIR / "api_snapshot.json").read_text(encoding="utf-8"))
    behavior_snapshot = json.loads((FIXTURE_DIR / "behavior_snapshot.json").read_text(encoding="utf-8"))

    import markpickle

    missing_exports = [name for name in api_snapshot["exports"] if name not in markpickle.__all__]
    if missing_exports:
        print(f"Missing exports: {missing_exports}")
        return 1

    missing_attributes = [name for name in api_snapshot["exports"] if not hasattr(markpickle, name)]
    if missing_attributes:
        print(f"Missing attributes: {missing_attributes}")
        return 1

    for name, baseline_contract in api_snapshot["function_contracts"].items():
        current_contract = _signature_contract(getattr(markpickle, name))
        if len(current_contract) < len(baseline_contract):
            print(f"Function {name} lost parameters.")
            return 1
        if current_contract[: len(baseline_contract)] != baseline_contract:
            print(f"Function {name} changed its baseline parameter contract.")
            return 1
        if any(parameter["required"] for parameter in current_contract[len(baseline_contract) :]):
            print(f"Function {name} added required parameters.")
            return 1

    current_config_fields = [field.name for field in dataclasses.fields(markpickle.Config)]
    baseline_fields = api_snapshot["config_fields"]
    if current_config_fields[: len(baseline_fields)] != baseline_fields:
        print("Config fields are not backward compatible.")
        return 1

    for case in behavior_snapshot["cases"]:
        actual = _normalize_value(_evaluate_case(markpickle, case))
        if actual != case["baseline_expected"]:
            print(f"Behavior mismatch for {case['id']}:")
            print(json.dumps({"expected": case["baseline_expected"], "actual": actual}, indent=2, sort_keys=True))
            return 1

    print("Installed package passed the frozen v1 compatibility checks.")
    return 0


def run_wheel_check() -> int:
    if not FIXTURE_DIR.joinpath("api_snapshot.json").exists():
        generate_fixtures()

    dist_dir = ROOT / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    subprocess.run([sys.executable, "-m", "build"], cwd=ROOT, check=True)

    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        print("No wheel was produced.")
        return 1

    wheel_path = wheels[-1]
    subprocess.run([UV_EXE, "venv", "--clear", str(WHEEL_VENV)], cwd=ROOT, check=True)
    subprocess.run(
        [UV_EXE, "pip", "install", "--python", str(_uv_python(WHEEL_VENV)), "--force-reinstall", str(wheel_path)],
        cwd=ROOT,
        check=True,
    )

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        completed = subprocess.run(
            [str(_uv_python(WHEEL_VENV)), str(Path(__file__).resolve()), "run-installed-checks"],
            cwd=temp_dir,
            text=True,
            check=False,
        )
        return completed.returncode


def capture(kind: str) -> int:
    if kind == "api":
        payload = _capture_api_snapshot()
    elif kind == "behavior":
        payload = _capture_case_results(BEHAVIOR_CASES)
    elif kind == "documented-changes":
        payload = _capture_case_results(DOCUMENTED_CHANGE_CASES)
    else:
        msg = f"Unknown capture kind {kind!r}"
        raise ValueError(msg)

    sys.stdout.write(json.dumps(payload))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("generate", help="Refresh the frozen v1 fixtures from the local git baseline")
    subparsers.add_parser("create-baseline-venv", help=f"Create {BASELINE_VENV.name} from the frozen baseline")
    subparsers.add_parser("run-wheel-check", help=f"Install the built wheel into {WHEEL_VENV.name} and run checks")
    subparsers.add_parser("run-installed-checks", help="Validate an installed package against the frozen fixtures")

    capture_parser = subparsers.add_parser("capture", help="Internal helper for subprocess capture")
    capture_parser.add_argument("--kind", choices=["api", "behavior", "documented-changes"], required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "generate":
        return generate_fixtures()
    if args.command == "create-baseline-venv":
        return create_baseline_venv()
    if args.command == "run-wheel-check":
        return run_wheel_check()
    if args.command == "run-installed-checks":
        return run_installed_checks()
    if args.command == "capture":
        return capture(args.kind)
    msg = f"Unsupported command {args.command!r}"
    raise ValueError(msg)


if __name__ == "__main__":
    raise SystemExit(main())
