# Contributing (Humans)

Thank you for contributing to markpickle! This guide covers everything you need to get
started — from setting up your environment to submitting a pull request.

## Development setup

markpickle uses [uv](https://docs.astral.sh/uv/) for environment and dependency management.

```bash
# Install uv (if you don't have it)
# https://docs.astral.sh/uv/getting-started/installation/

# Clone the repo
git clone https://github.com/matthewdeanmartin/markpickle.git
cd markpickle

# Install all dev and optional dependencies
uv sync --all-extras
```

All subsequent commands in this guide use `uv run` to invoke tools inside the managed
environment.

## Running tests

```bash
# Run all tests (doctests + unit tests) in parallel
make test

# Or directly with pytest
uv run pytest markpickle test -q
```

Tests live in `test/`. Doctests are embedded in module docstrings and run automatically.

### Test markers

| Marker | Meaning |
| ----------------- | --------------------------------------- |
| `compat` | Compatibility tests against v1.6.4 baseline |
| `documented_change` | Tests for intentional behavior changes since v1.x |

```bash
# Run only compat tests
make compat

# Run only tests tagged as documented changes
uv run pytest -m documented_change
```

## Linting and formatting

```bash
# Format code (isort + black + add missing future annotations)
make format

# Run pylint (requires score >= 9.9)
make lint-code

# Run ruff
make ruff
```

The `format-code` target also ensures every `.py` file has
`from __future__ import annotations` at the top. The script lives in
`scripts/add_future_annotations.py`.

## Type checking

```bash
# mypy only
make type-check-mypy

# pyright only
make type-check-pyright

# ty (Astral's type checker) only
make type-check-ty

# All three + pydoclint
make type-check-all
```

## Security and audit

```bash
# bandit static analysis
make security-check

# pip-audit for known CVEs in dependencies
make audit
```

## Documentation

```bash
# Check that all Markdown docs are formatted (mdformat --check)
make docs-format-check

# Build the MkDocs site locally
make docs-build

# Run doc-embedded code examples as tests
make docs-test

# Check for broken links
make docs-links
```

## Compatibility tests

The compat suite freezes the behavior of markpickle v1.6.4 and compares it with the
current code. See [Compatibility Tests](COMPAT_TESTS.md) for a full explanation.

```bash
# Run the compat suite against committed JSON fixtures
make compat

# Regenerate fixtures from the v1.6.4 baseline venv
make compat-refresh

# Full wheel check: build wheel, install, run compat
make compat-wheel
```

## Adding support for a new Python type

1. **`markpickle/config_class.py`** — Add an opt-in config flag if the new type needs
   one (e.g., `infer_uuid_types`).
2. **`markpickle/serialize.py`** — Handle the new type in `_serialize_value()`.
3. **`markpickle/deserialize.py`** — Handle inference in `extract_scalar()` or
   `process_list_of_tokens()`.
4. **`docs/examples.md`** — Add a usage example in the appropriate section.
5. **`docs/configuration.md`** — Document any new Config flags.
6. **`CHANGELOG.md`** — Add an entry under the upcoming version.
7. **Tests** — Add at least one round-trip test in `test/`.

## Python version compatibility

markpickle supports **Python 3.9+**. Keep these rules in mind:

- Always include `from __future__ import annotations` at the top of every `.py` file
  (the `make format` target does this automatically).
- Never use `X | Y` in runtime positions (`isinstance`, `cast`, `type()`) — use tuples
  for `isinstance` and string literals for `cast`.
- `zip(strict=True)` was added in 3.10 — do not use it.
- `dataclasses.__getstate__` was added in 3.11 — use `dataclasses.asdict()` as a fallback.

Run the tox suite to verify across supported versions:

```bash
uv run tox
```

## Submitting a pull request

1. Fork the repository and create a branch from `main`.
2. Make your changes, add tests, update docs.
3. Run `make check-code` (format + lint + type check + security + tests). All checks
   must pass.
4. Run `make compat` to ensure v1.6.4 behavior is preserved (or document intentional
   changes with the `documented_change` marker).
5. Update `CHANGELOG.md` with a summary of your change.
6. Open a pull request against `main` with a clear description.

## Commit style

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) conventions for
`CHANGELOG.md` entries (`Added`, `Changed`, `Fixed`, `Removed`).

Commit messages should be short and imperative: `Fix negative int deserialization`,
`Add UUID round-trip support`.

## Release process

See [Pre-Release Checklist](pre_release_checklist.md).
