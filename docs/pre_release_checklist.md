# Pre-Release Checklist

Use this checklist before publishing a new version of markpickle to PyPI.

## 1. Version and changelog

- [ ] Bump version in `markpickle/__about__.py`
- [ ] Verify `pyproject.toml` version matches `__about__.py`
- [ ] Add a new section to `CHANGELOG.md` with today's date and the new version number
- [ ] Summarize all changes under `Added`, `Changed`, `Fixed`, `Removed`, `Breaking Changes`
- [ ] Check that the `CHANGELOG.md` entry matches what is in git since the last release tag

```bash
# See commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

## 2. Code quality gates

Run the full code check suite. All checks must pass before release:

```bash
make check-code
```

This runs, in order:

| Step | Command | Threshold |
| ---- | ------- | --------- |
| Format | `make format` | No uncommitted changes after format |
| Lint | `make lint-code` | pylint score ≥ 9.9 |
| Security | `make security-check` | No high-severity bandit findings |
| Audit | `make audit` | No unmitigated CVEs in deps |
| Tests | `make test` | All pass, coverage ≥ 50% |

### Type checking (recommended)

```bash
make type-check-all
```

Runs mypy (strict), pyright, ty, and pydoclint. Failures here are blocking for releases.

## 3. Compatibility tests

```bash
make compat
```

All v1.6.4 compatibility fixture tests must pass. If you intentionally changed behavior,
verify those changes are tagged with the `documented_change` pytest marker and have a
`CHANGELOG.md` entry in `Breaking Changes`.

For extra confidence before a major release:

```bash
# Build and install the wheel, then run compat against the installed wheel
make compat-wheel
```

## 4. Documentation

```bash
# Check all Markdown is formatted correctly
make docs-format-check

# Build the MkDocs site — must complete with no errors
make docs-build

# Run doc-embedded code examples as tests
make docs-test
```

Verify manually:

- [ ] `docs/examples.md` — every code example matches actual API behavior
- [ ] `docs/getting_started.md` — installation and quickstart examples are accurate
- [ ] `docs/configuration.md` — every `Config` field is documented
- [ ] `docs/limitations.md` — known limitations are still accurate
- [ ] `README.md` — supported types, CLI, and documentation links are up to date

## 5. Python version matrix

```bash
uv run tox
```

All configured Python versions (currently 3.9, 3.10, 3.11, 3.14) must pass. If a version
was added or removed, update `tox.ini` and document it in `CHANGELOG.md`.

## 6. Package build and inspection

```bash
make package-check
```

This builds the wheel and source distribution, then runs:

- `twine check dist/*` — checks metadata and long description
- `check-wheel-contents dist/*.whl` — checks for common wheel issues

Verify the wheel manually:

```bash
# List wheel contents
unzip -l dist/*.whl | less

# Confirm markpickle/py.typed is present (PEP 561)
unzip -l dist/*.whl | grep py.typed
```

## 7. Release status check

```bash
make release-status
```

Runs `troml-dev-status` if available, which checks for signs that the release is in a
"in progress" state (e.g., version ending in `.dev`, changelog missing a date, etc.).

## 8. Version check

```bash
make version-check
```

Runs `jiggle_version check` to ensure the version in `__about__.py`, `pyproject.toml`,
and git tags are consistent.

## 9. Pre-publish dry run

```bash
# Verify PyPI credentials are configured
uv run twine check dist/*

# Upload to TestPyPI first
uv run twine upload --repository testpypi dist/*

# Install from TestPyPI and smoke-test
pip install --index-url https://test.pypi.org/simple/ markpickle
python -c "import markpickle; print(markpickle.__version__)"
markpickle doctor
```

## 10. Publish

```bash
# Upload to PyPI
uv run twine upload dist/*

# Tag the release
git tag v<version>
git push origin v<version>
```

## 11. Post-release

- [ ] Verify the package is available on PyPI
- [ ] Create a GitHub release from the tag with the CHANGELOG entry as the description
- [ ] If there is a ReadTheDocs project, verify the docs built for the new tag
- [ ] Update the compat baseline if this is a new stable release that will become the
  new reference point: `make compat-refresh`

---

## Full automation

The `make publication-checks` target chains together the most critical steps:

```bash
make publication-checks
# Equivalent to: check-all + version-check + release-status + package-check
```

Run this as a final gate before uploading to PyPI.
