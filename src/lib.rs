use pyo3::prelude::*;

/// Returns `True` to confirm the Rust extension is loaded.
/// Use this at runtime to check whether Rust speedups are available.
///
/// ```python
/// from markpickle._rust_speedups import HAS_RUST_SPEEDUPS
/// if HAS_RUST_SPEEDUPS:
///     print("Rust speedups active")
/// ```
#[pyfunction]
pub fn has_rust_speedups() -> bool {
    true
}

/// Phase 0 placeholder – future Rust-accelerated serializer entry point.
///
/// This will eventually accept a Python object and return a Markdown string
/// faster than the pure-Python implementation.  For now it raises
/// `NotImplementedError` so the Python shim falls back transparently.
#[pyfunction]
pub fn dumps_fast(_py: Python<'_>, _value: &Bound<'_, PyAny>) -> PyResult<String> {
    Err(pyo3::exceptions::PyNotImplementedError::new_err(
        "dumps_fast: Rust implementation not yet available – use Python fallback",
    ))
}

/// Phase 0 placeholder – future Rust-accelerated deserializer entry point.
///
/// This will eventually accept a Markdown string and return a Python object
/// faster than the pure-Python implementation.  For now it raises
/// `NotImplementedError` so the Python shim falls back transparently.
#[pyfunction]
pub fn loads_fast(_py: Python<'_>, _value: &str) -> PyResult<PyObject> {
    Err(pyo3::exceptions::PyNotImplementedError::new_err(
        "loads_fast: Rust implementation not yet available – use Python fallback",
    ))
}

/// The native extension module exposed as `markpickle._markpickle`.
#[pymodule]
fn _markpickle(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(has_rust_speedups, m)?)?;
    m.add_function(wrap_pyfunction!(dumps_fast, m)?)?;
    m.add_function(wrap_pyfunction!(loads_fast, m)?)?;
    Ok(())
}
