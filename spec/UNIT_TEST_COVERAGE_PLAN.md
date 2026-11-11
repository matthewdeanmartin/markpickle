# Unit test coverage plan

## Baseline

On 2026-11-11, `uv run pytest --cov=markpickle --cov-report=term-missing -q` reported 402 passed, 5 skipped, and 73% statement coverage (2,275 statements; 612 missed). The largest coverage gaps were GUI panels, binary streams, file splitting, Unicode formatting, CLI branches, deserialization edge cases, and validation.

## Approach

Add behavior-focused unit tests in small groups. Prefer isolated functions and headless panel logic before GUI construction. Keep optional dependency tests skippable when the dependency is absent. Do not target a percentage by testing private implementation details where public behavior can be exercised instead.

## Work queue

1. **Binary streams and Unicode formatting** — cover data URL decoding and optional Pillow behavior; round-trip inline style conversion and Unicode-to-Markdown formatting. (Started in `test/test_binary_streams.py` and `test/test_unicode_text.py`.)
2. **File splitting** — cover accepted/rejected separator rows, blank lines, consecutive separators, and final unterminated sections.
3. **Validation** — cover headings, paragraph inline tokens, and malformed/unsupported token cases through `validate_markdown`.
4. **Core deserialization** — exercise uncovered table/list/scalar branches and the remaining missing-key and object-hook behavior through public load APIs.
5. **Serialization and table helpers** — cover custom defaults, falsy values, table rendering/parsing modes, and error paths through public APIs.
6. **CLI** — cover convert/validate/doctor success and failure paths with captured streams and temporary files.
7. **GUI logic** — prioritize non-window state/panel helper methods; use fake widgets or Tk only where the environment supports headless execution.
8. **Optional/compatibility modules** — test compatibility shims and optional Rust/image integrations with skip conditions when unavailable.

## Completion criteria

- Each group has focused tests and is run with `uv run pytest`.
- Re-run the full coverage command and record the changed total and remaining largest gaps here.
- Leave implementation behavior unchanged unless a test exposes a concrete defect; report any such fix separately.
