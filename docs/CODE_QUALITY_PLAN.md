# Code Quality Plan - markpickle

This document outlines the strategy for improving the semantic correctness, robustness, and maintainability of `markpickle`.

## 1. Project Philosophy
`markpickle` is a **lossy** serialization format. Unlike JSON or YAML, Markdown does not have native support for all Python types. Our quality goal is not "perfection" in representing every object, but **predictability** and **transparency** regarding what is lost.

## 2. Identified Flaws & Known Bugs

### Functional Bugs (High Priority)
- **`loads_all` is broken**: Multi-document streams (separated by `---`) do not deserialize correctly.
- **Nested ATX Headers**: `serialize.py` only handles the first level of nested dictionaries as ATX headers; deeper levels are lost or improperly formatted.
- **Type Inference Heuristics**: `extract_scalar` frequently misinterprets strings that "look like" dates or numbers, leading to unintended type changes during round-trips.
- **Whitespace Handling**: `test_dodgy` indicates failures in preserving or correctly ignoring leading/trailing whitespace in strings.

### Structural Flaws
- **Stubbed Logic**: `python_to_atx_header` in `serialize.py` is a `print("Not implemented yet")` stub.
- **Mixed Content Ambiguity**: Paragraphs mixed with lists or code blocks often raise `NotImplementedError` rather than being treated as tuples or joined strings.
- **Lack of Validation**: There is no "dry run" mechanism to tell a user if their data will survive a round-trip before they write it to disk.

---

## 3. Quality Initiatives

### A. Semantic Round-trip Validation
Move beyond simple fuzzing. We will use `hypothesis` to generate complex, valid Python data structures and assert:
1. `loads(dumps(x)) == x` (where `x` is a string-heavy dict/list).
2. If `loads(dumps(x)) != x`, the difference must be documented and predictable (e.g., ints becoming strings if type inference is off).

### B. Dependency & Security Auditing
Maintain a "Clean Lock" policy.
- **Pip-Audit**: Integrated into `make check`. If a vulnerability is found in `uv.lock`, the build fails unless a relock/upgrade resolves it.
- **Bandit**: Continued use for static security analysis of the source code.

### C. Performance Benchmarking
Prevent regressions in serialization speed, especially for large tables and deeply nested structures.
- **Pytest-Benchmark**: Integrated into `make benchmark`. Baseline metrics established for common data patterns.

### D. Mutation Testing
Use `mutmut` to ensure our tests are actually testing the logic. If a line of code in `serialize.py` can be changed without a test failing, the test suite is insufficient.

### E. Documentation Integrity
Every code block in `README.md` and `docs/` must be tested. We use `pytest-codeblocks` to ensure the "Source of Truth" for users doesn't drift from the implementation.

---

## 4. Implementation Checklist

### Phase 1: Fixing Core Defects
- [ ] Implement `python_to_atx_header` to support nested dicts as headers.
- [ ] Fix `loads_all` logic for multi-document streams.
- [ ] Resolve `test_dodgy` whitespace issues.
- [ ] Replace `print` stubs with `NotImplementedError` or actual logic.

### Phase 2: Tooling & Automation
- [x] Integrate `pip-audit` into `Makefile`.
- [x] Integrate `pytest-benchmark` and create `test/test_benchmark.py`.
- [ ] Add `mutmut` to dev dependencies and run initial audit.
- [ ] Configure `pytest-codeblocks` to fail on any invalid documentation example.

### Phase 3: Semantic Improvements
- [ ] Implement `markpickle.validate(data)` to report "lossy" elements before serialization.
- [ ] Add a `strict` mode to `Config` to raise errors on ambiguous mixed content.
- [ ] Refine `extract_scalar` heuristics to reduce false-positive type conversions.
- [ ] Expand `hypothesis` strategies to cover all `SerializableTypes`.

---

## 5. Maintenance Commands
- `make check`: Runs all linters, tests, and security audits.
- `make benchmark`: Runs performance tests.
- `make pip-audit`: Checks for dependency vulnerabilities and attempts auto-fix via `uv`.
