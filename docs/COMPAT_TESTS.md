# Compatibility Tests

This project now has a frozen compatibility harness for the `1.6.4` line. The goal is to answer a very specific release question:

> "If I publish the current version, what older consumer behavior did I accidentally break?"

The harness does **not** try to make every old test pass forever. Instead, it separates:

- compatibility we still promise
- changes that were intentional and documented

That split is what makes the results useful.

## What Counts as Compatibility

For `markpickle`, compatibility is currently defined in two layers:

1. **Public API compatibility**

   - names exported from `markpickle.__all__`
   - selected public callable signatures such as `load`, `loads`, `dump`, `dumps`, `load_all`, `loads_all`, `dump_all`, `dumps_all`, `split_file`, and `Config`

1. **Behavior compatibility**

   - a curated set of user-facing examples that passed on the frozen baseline and are still supposed to work now

This is intentionally narrower than "all historical behavior." Some old behavior was buggy, accidental, or explicitly changed in `2.0.0`.

## Current Layout

The compatibility harness currently lives in these places:

- `test\compat\test_public_api_v1.py`
- `test\compat\test_behavior_v1.py`
- `test\compat\test_documented_v2_changes.py`
- `test\compat\helpers.py`
- `test\compat\fixtures\v1_6_4\`
- `scripts\generate_v1_compat_fixtures.py`

The frozen baseline for the first generation of this harness is:

- git ref: `c80c4c4`
- release line: `1.6.4`

## How It Works

## 1. Freeze a baseline

The script `scripts\generate_v1_compat_fixtures.py` exports the baseline source from git, imports that version of `markpickle`, and records the contract we care about.

It captures:

- `markpickle.__all__`
- selected public function signatures via `inspect.signature`
- `Config` field order and presence
- outputs for a curated set of stable behavior cases
- outputs for a curated set of known, documented behavior changes

Those snapshots are committed to:

- `test\compat\fixtures\v1_6_4\api_snapshot.json`
- `test\compat\fixtures\v1_6_4\behavior_snapshot.json`
- `test\compat\fixtures\v1_6_4\documented_changes.json`

Because the fixtures are checked into the repo, normal CI runs do **not** need to go fetch an old version from PyPI every time.

## 2. Compare the current source tree to the frozen baseline

`test\compat\test_public_api_v1.py` verifies that:

- old exported names still exist
- those names are still importable
- public signatures are backward compatible
- old `Config` fields still exist in a compatible way

`test\compat\test_behavior_v1.py` runs curated behavior cases against the current code and compares them with the frozen `1.6.4` expectations.

## 3. Track intentional differences separately

`test\compat\test_documented_v2_changes.py` covers changes that are supposed to differ from the `1.6.4` baseline.

Examples include:

- `infer_scalar_types=False` becoming truly string-preserving
- `none_values` being consulted during deserialization
- negative ints loading as `int` instead of `float`
- `datetime` keeping its time portion
- `dump_all()` writing document separators correctly

These tests are important because they preserve context:

- a difference from `1.6.4` is not automatically a regression
- but it must be documented and intentional

## 4. Validate the built artifact, not just local imports

The wheel check builds the package, installs that wheel into a clean compat environment, and runs the frozen compatibility checks against the installed artifact.

This catches packaging issues such as:

- missing exports in the wheel
- missing package files
- different behavior between editable/local imports and the published artifact

## Venv Strategy

This repo uses `uv`, and the compatibility workflow uses **separate, explicit virtual environments** instead of trying to cram multiple versions into one env.

The practical layout is:

- `.venv` or the normal `uv run` environment for current development
- `.venv-compat-1.6.4` for the frozen baseline
- `.venv-compat-wheel` for installed-wheel validation

The helper script creates these environments directly and uses `--clear` so reruns are non-interactive.

That isolation is important because it prevents:

- import leakage between versions
- stale installed dependencies from hiding real problems
- confusion about whether a test exercised the source tree or the packaged wheel

## Commands

The main commands are:

```powershell
make compat
make compat-refresh
make compat-baseline-venv
make compat-wheel
```

Equivalent direct commands:

```powershell
uv run pytest test\compat -q
uv run python scripts\generate_v1_compat_fixtures.py generate
uv run python scripts\generate_v1_compat_fixtures.py create-baseline-venv
uv run python scripts\generate_v1_compat_fixtures.py run-wheel-check
```

## What to Run Before a Release

At minimum, run:

```powershell
make compat
make compat-wheel
```

If you intentionally changed compatibility expectations, also run:

```powershell
make compat-refresh
```

but only after deciding that the new baseline or fixture changes are correct and should be committed.

## How to Extend the Existing Compatibility Suite

Add new cases carefully. The suite is most useful when it stays small, high-signal, and consumer-facing.

Good candidates:

- public imports from `markpickle`
- stable README examples
- common `loads` / `dumps` / `loads_all` / `dumps_all` cases
- `Config` options that users are likely to depend on
- bugs fixed in a way that should now stay fixed forever

Poor candidates:

- GUI internals
- benchmarks
- unstable fuzz/property cases
- incidental formatting details you do not actually want to promise
- bugs from old versions that you do not want to preserve

### Extending the frozen v1 behavior corpus

1. Edit the case lists in `scripts\generate_v1_compat_fixtures.py`.
1. Add a new stable case to `BEHAVIOR_CASES` or a documented-difference case to `DOCUMENTED_CHANGE_CASES`.
1. Regenerate fixtures:

```powershell
make compat-refresh
```

4. Run:

```powershell
make compat
make compat-wheel
```

5. Review the fixture diff before committing it.

Never regenerate fixtures casually. A fixture diff is effectively a contract change.

## How to Set Up Future `v2` and `v3` Compatibility Lanes

Right now the harness is frozen against `1.6.4`. Future release lines should follow the same pattern.

## When to add a new lane

Add a new compatibility lane when a release line becomes a compatibility baseline you want to preserve.

Examples:

- before shipping `3.0.0`, freeze a `v2` baseline
- before shipping `4.0.0`, freeze a `v3` baseline
- if a late `2.x` patch release becomes the "best representative baseline," freeze that exact ref/version

In practice, the best time is:

- after the previous major line is stable
- before the next major line starts making large behavioral changes

## Recommended naming pattern

Use both a release-oriented name and a concrete fixture directory:

- tests:
  - `test\compat\test_public_api_v2.py`
  - `test\compat\test_behavior_v2.py`
  - `test\compat\test_documented_v3_changes.py`
- fixtures:
  - `test\compat\fixtures\v2_3_1\`
  - `test\compat\fixtures\v3_0_0\`

The directory should reflect the exact frozen baseline version, not just the major version.

## Recommended process for `v2 -> v3`

Suppose you are preparing `3.0.0` and want `2.x` compatibility coverage.

1. Pick the exact baseline version or git ref to freeze.

   - Example: `2.3.1`

1. Duplicate the existing pattern.

   - Add new fixture output directory such as `test\compat\fixtures\v2_3_1\`
   - Add a new generation path in the helper script, or refactor the script to take a baseline version/ref argument

1. Create the new test files.

   - `test_public_api_v2.py`
   - `test_behavior_v2.py`
   - `test_documented_v3_changes.py`

1. Freeze the new baseline.

   - capture exports
   - capture signatures
   - capture a curated stable behavior corpus
   - capture a curated list of intentional `v3` differences

1. Run both lanes if you still care about both.

   - maybe `v1` compatibility is still important
   - maybe only `v2` matters now

## Should old lanes be deleted?

Not automatically.

Keep an older lane if you still want to protect users coming from that line. Remove or retire it only when you intentionally stop treating that line as a supported compatibility target.

For example:

- keep `v1` checks if `3.x` should still be broadly safe for long-time users
- drop `v1` checks if you only promise compatibility relative to `2.x`

The right answer is a product policy question, not just a test question.

## A Good Rule for Major Releases

For each new major release:

1. decide which previous line is the compatibility target
1. freeze that line explicitly
1. split stable behavior from intentional changes
1. test the built wheel before publishing
1. document intentional breaks in both tests and changelog

That gives you a release process that is explainable, reviewable, and repeatable.

## Limitations of the Current Harness

The current implementation is intentionally conservative.

- It focuses on high-value public behavior, not every internal detail.
- It is currently wired around the `1.6.4` baseline.
- It uses curated examples rather than the entire historical test suite.
- It does not yet expose a fully generic CLI for arbitrary baseline versions.

That is okay. A small compatibility suite that people trust is more useful than a giant one nobody understands.

## Summary

The compatibility workflow in this repo is based on one idea:

> freeze an old version's public contract, then compare today's package against it on purpose

That is stronger than "run the old tests and hope," and more honest than pretending intentional changes are regressions.
