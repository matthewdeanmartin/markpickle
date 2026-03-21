ifeq ($(origin VIRTUAL_ENV),undefined)
    VENV := uv run
else
    VENV :=
endif

uv.lock: pyproject.toml
	@echo "Installing dependencies"
	@uv lock && uv sync

# tests can't be expected to pass if dependencies aren't installed.
# tests are often slow and linting is fast, so run tests on linted code.
test: pylint bandit uv.lock
	@echo "Running unit tests"
	$(VENV) pytest markpickle --doctest-modules
	# $(VENV) python -m unittest discover
	$(VENV) py.test test --cov=markpickle --cov-report=html --cov-fail-under 50

isort:  
	@echo "Formatting imports"
	$(VENV) isort markpickle markmodule

black:  isort 
	@echo "Formatting code"
	$(VENV) metametameta pep621
	$(VENV) black . --exclude .virtualenv --exclude .venv

pre-commit:  isort black
	@echo "Pre-commit checks"
	$(VENV) pre-commit run --all-files

bandit:  
	@echo "Security checks"
	$(VENV)  bandit markpickle -r


.PHONY: pylint
pylint:  isort black 
	@echo "Linting with pylint"
	$(VENV) pylint markpickle --fail-under 9.9

mypy:  
	@echo "Security checks"
	$(VENV)  mypy markpickle

pip-audit:
	@echo "Auditing dependencies"
	$(VENV) pip-audit || (echo "Vulnerability found, attempting to relock..." && uv lock --upgrade && uv sync && $(VENV) pip-audit)

benchmark:
	@echo "Running benchmarks"
	$(VENV) pytest test/test_benchmark.py --benchmark-only

# ---------------------------------------------------------------------------
# Rust / maturin targets
#
# Prerequisites:
#   - Rust toolchain  (https://rustup.rs)
#   - maturin         (installed via `uv sync`)
#
# build-rust        Compile an optimised release build and install into the
#                   current venv so `import markpickle._markpickle` works.
# build-rust-debug  Same but with debug symbols (faster compile, slower runtime).
# build-rust-wheel  Produce a distributable .whl in dist/.
# check-rust        Run `cargo check` + clippy on the Rust source.
# test-rust         Run Rust unit tests via `cargo test`.
# clean-rust        Remove Rust build artefacts and any installed .pyd/.so.
#
# The Python package works without these; they are purely optional speedups.
# ---------------------------------------------------------------------------

.PHONY: build-rust
build-rust:
	@echo "Building Rust extension (release) with maturin"
	$(VENV) maturin develop --release

.PHONY: build-rust-debug
build-rust-debug:
	@echo "Building Rust extension (debug) with maturin"
	$(VENV) maturin develop

.PHONY: build-rust-wheel
build-rust-wheel:
	@echo "Building Rust wheel with maturin"
	$(VENV) maturin build --release --out dist

.PHONY: check-rust
check-rust:
	@echo "Checking Rust code"
	cargo check
	cargo clippy -- -D warnings

.PHONY: test-rust
test-rust:
	@echo "Running Rust unit tests"
	cargo test

.PHONY: clean-rust
clean-rust:
	@echo "Removing Rust build artefacts"
	cargo clean 2>/dev/null || true
	rm -f markpickle/_markpickle*.so markpickle/_markpickle*.pyd 2>/dev/null || true

check: test pylint bandit pre-commit mypy pip-audit

.PHONY: publish
publish: check
	rm -rf dist && $(VENV) hatch build
