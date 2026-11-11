from __future__ import annotations

import pytest

from markpickle import _rust_speedups as speedups
from markpickle.deserialize import loads
from markpickle.serialize import dumps


def test_has_rust_speedups_reports_extension_state():
    assert speedups.has_rust_speedups() is speedups.HAS_RUST_SPEEDUPS


def test_dumps_fast_uses_python_fallback_without_extension(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(speedups, "HAS_RUST_SPEEDUPS", False)

    assert speedups.dumps_fast(["alpha", "beta"]) == dumps(["alpha", "beta"])


def test_loads_fast_uses_python_fallback_without_extension(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(speedups, "HAS_RUST_SPEEDUPS", False)

    assert speedups.loads_fast("- alpha\n- beta\n") == loads("- alpha\n- beta\n")


def test_dumps_fast_falls_back_when_extension_rejects_value(monkeypatch: pytest.MonkeyPatch):
    def reject(_value):
        raise NotImplementedError

    monkeypatch.setattr(speedups, "HAS_RUST_SPEEDUPS", True)
    monkeypatch.setattr(speedups, "_rust_dumps_fast", reject)

    assert speedups.dumps_fast({"key": "value"}) == dumps({"key": "value"})


def test_loads_fast_falls_back_when_extension_rejects_input(monkeypatch: pytest.MonkeyPatch):
    def reject(_value):
        raise NotImplementedError

    monkeypatch.setattr(speedups, "HAS_RUST_SPEEDUPS", True)
    monkeypatch.setattr(speedups, "_rust_loads_fast", reject)

    assert speedups.loads_fast("# answer\n\n42\n") == loads("# answer\n\n42\n")


def test_fast_helpers_use_extension_results_when_supported(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(speedups, "HAS_RUST_SPEEDUPS", True)
    monkeypatch.setattr(speedups, "_rust_dumps_fast", lambda _value: "rust markdown")
    monkeypatch.setattr(speedups, "_rust_loads_fast", lambda _value: "rust object")

    assert speedups.dumps_fast(object()) == "rust markdown"
    assert speedups.loads_fast("input") == "rust object"
