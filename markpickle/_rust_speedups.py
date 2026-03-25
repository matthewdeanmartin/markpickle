"""Optional Rust-accelerated implementations for markpickle.

Attempts to import the compiled ``_markpickle`` native extension built with
maturin/pyo3.  If the extension is absent (e.g. wheels not built, platform not
supported), every symbol falls back to a pure-Python equivalent so the package
continues to work without Rust.

Usage::

    from markpickle._rust_speedups import HAS_RUST_SPEEDUPS, dumps_fast, loads_fast

    result = dumps_fast(value)   # uses Rust when available, Python otherwise
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Try to import the compiled native extension
# ---------------------------------------------------------------------------
try:
    from markpickle._markpickle import (
        dumps_fast as _rust_dumps_fast,  # type: ignore[import]
    )
    from markpickle._markpickle import has_rust_speedups as _rust_has
    from markpickle._markpickle import loads_fast as _rust_loads_fast

    HAS_RUST_SPEEDUPS: bool = True
except ImportError:
    HAS_RUST_SPEEDUPS = False
    _rust_has = None
    _rust_dumps_fast = None
    _rust_loads_fast = None


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def has_rust_speedups() -> bool:
    """Return ``True`` if the compiled Rust extension is loaded."""
    return HAS_RUST_SPEEDUPS


def dumps_fast(value: Any) -> str:
    """Serialize *value* to a Markdown string.

    Uses the Rust-accelerated path when available; falls back to the pure-Python
    :func:`markpickle.dumps` implementation otherwise.
    """
    if HAS_RUST_SPEEDUPS and _rust_dumps_fast is not None:
        try:
            return _rust_dumps_fast(value)  # type: ignore[no-any-return]
        except NotImplementedError:
            pass
    # Pure-Python fallback (import here to avoid circular imports)
    from markpickle.serialize import dumps  # noqa: PLC0415

    return dumps(value)


def loads_fast(value: str) -> Any:
    """Deserialize a Markdown string to a Python object.

    Uses the Rust-accelerated path when available; falls back to the pure-Python
    :func:`markpickle.loads` implementation otherwise.
    """
    if HAS_RUST_SPEEDUPS and _rust_loads_fast is not None:
        try:
            return _rust_loads_fast(value)
        except NotImplementedError:
            pass
    # Pure-Python fallback
    from markpickle.deserialize import loads  # noqa: PLC0415

    return loads(value)
