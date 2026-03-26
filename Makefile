.DEFAULT_GOAL := help
MAKEFLAGS += --no-print-directory

UV_RUN := uv run
CODE_PATHS := markpickle test
DOC_FILE_PATHS := README.md CHANGELOG.md AGENTS.md tiny.md
DOC_DIR_PATHS := docs spec
DOC_PATHS := $(DOC_FILE_PATHS) $(DOC_DIR_PATHS)
PYTEST_N ?= auto
PYTEST_ARGS := -q -ra --maxfail=1 --doctest-modules --cov=markpickle --cov-report=html --cov-fail-under=50
PYTEST_XDIST_ARGS := -n $(PYTEST_N) --dist loadfile
PYTEST_IGNORE_ARGS := --ignore=test/test_benchmark.py
PYTEST_DISABLE_PLUGIN_ARGS := -p no:benchmark

ifdef PYTEST_SEED
PYTEST_RANDOM_ARGS := --randomly-seed=$(PYTEST_SEED)
endif

.PHONY: help lock sync format format-code format-docs lint lint-code ruff pylint type-check type-check-all type-check-mypy type-check-pyright type-check-ty type-check-docstrings security-check audit test compat compat-refresh compat-baseline-venv compat-wheel benchmark docs-format-check docs-links docs-build docs-test check-code check-docs check-all version-check release-status clean-dist build-package package-check publication-checks check publish build-rust build-rust-debug build-rust-wheel check-rust test-rust clean-rust

help:
	@printf "%s\n" \
	"make sync                # lock + install dev deps and all extras" \
	"make format              # format code and docs" \
	"make lint                # format code, then run pylint" \
	"make test                # run doctests + unit tests in parallel" \
	"make compat              # run frozen 1.x compatibility tests" \
	"make compat-refresh      # regenerate frozen 1.6.4 compatibility fixtures" \
	"make compat-baseline-venv # create .venv-compat-1.6.4 from the local 1.6.4 git baseline" \
	"make compat-wheel        # build wheel, install into .venv-compat-wheel, run compat checks" \
	"make type-check-mypy     # run mypy on markpickle" \
	"make type-check-pyright  # run pyright on markpickle" \
	"make type-check-ty       # run ty on markpickle" \
	"make type-check-docstrings # check docstring/signature type mismatches" \
	"make type-check-all      # run mypy, pyright, ty, pydoclint" \
	"make check-code          # code checks only" \
	"make docs-format-check   # verify markdown formatting" \
	"make check-docs          # documentation checks only" \
	"make check-all           # code + docs checks" \
	"make publication-checks  # release readiness checks" \
	"make publish             # alias for publication-checks"

lock:
	@echo "[lock]"
	uv lock

sync: lock
	@echo "[sync]"
	uv sync --all-extras

format: format-code format-docs

format-code:
	@echo "[format-code]"
	$(UV_RUN) metametameta pep621
	$(UV_RUN) isort --quiet $(CODE_PATHS)
	$(UV_RUN) black --quiet . --exclude .virtualenv --exclude .venv

format-docs:
	@echo "[format-docs]"
	$(UV_RUN) mdformat $(DOC_PATHS)

lint: format-code lint-code

lint-code:
	@echo "[lint]"
	$(UV_RUN) pylint markpickle --disable=C0415 --fail-under 9.9

ruff:
	@echo "[ruff]"
	$(UV_RUN) ruff check $(CODE_PATHS)

pylint: lint-code

type-check-mypy:
	@echo "[mypy]"
	$(UV_RUN) mypy markpickle

type-check-pyright:
	@echo "[pyright]"
	$(UV_RUN) pyright markpickle

type-check-ty:
	@echo "[ty]"
	$(UV_RUN) ty check markpickle

type-check-docstrings:
	@echo "[pydoclint]"
	@if $(UV_RUN) python -c "import shutil, sys; sys.exit(0 if shutil.which('pydoclint') else 1)"; then \
		$(UV_RUN) pydoclint markpickle; \
	else \
		echo "[skip] pydoclint unavailable for this Python"; \
	fi

type-check-all: type-check-mypy type-check-pyright type-check-ty type-check-docstrings

type-check: type-check-all

security-check:
	@echo "[bandit]"
	$(UV_RUN) bandit markpickle -r --skip B311,B110

audit:
	@echo "[pip-audit]"
	$(UV_RUN) pip-audit --ignore-vuln CVE-2026-4539

test:
	@echo "[test] workers=$(PYTEST_N)"
	$(UV_RUN) pytest $(CODE_PATHS) $(PYTEST_IGNORE_ARGS) $(PYTEST_DISABLE_PLUGIN_ARGS) $(PYTEST_ARGS) $(PYTEST_XDIST_ARGS) $(PYTEST_RANDOM_ARGS)

compat:
	@echo "[compat]"
	$(UV_RUN) pytest test\compat -q

compat-refresh:
	@echo "[compat-refresh]"
	$(UV_RUN) python scripts\generate_v1_compat_fixtures.py generate

compat-baseline-venv:
	@echo "[compat-baseline-venv]"
	$(UV_RUN) python scripts\generate_v1_compat_fixtures.py create-baseline-venv

compat-wheel:
	@echo "[compat-wheel]"
	$(UV_RUN) python scripts\generate_v1_compat_fixtures.py run-wheel-check

benchmark:
	@echo "[benchmark]"
	$(UV_RUN) pytest test\test_benchmark.py --benchmark-only

docs-format-check:
	@echo "[docs-format-check]"
	$(UV_RUN) mdformat --check $(DOC_PATHS)

docs-links:
	@echo "[docs-links]"
	$(UV_RUN) linkcheckMarkdown -local docs
	$(UV_RUN) linkcheckMarkdown -local spec
	$(UV_RUN) linkcheckMarkdown -local README.md
	$(UV_RUN) linkcheckMarkdown -local CHANGELOG.md
	$(UV_RUN) linkcheckMarkdown -local AGENTS.md
	$(UV_RUN) linkcheckMarkdown -local tiny.md

docs-build:
	@echo "[docs-build]"
	$(UV_RUN) mkdocs build

docs-test:
	@echo "[docs-test]"
	$(UV_RUN) pytest --markdown-docs -q README.md docs spec

check-code: lint security-check audit test

check-docs: docs-links docs-build

check-all: check-code check-docs

check: check-all

version-check:
	@echo "[version-check]"
	$(UV_RUN) jiggle_version check

release-status:
	@echo "[release-status]"
	@if $(UV_RUN) python -c "import shutil, sys; sys.exit(0 if shutil.which('troml-dev-status') else 1)"; then \
		$(UV_RUN) troml-dev-status validate .; \
	else \
		echo "[skip] troml-dev-status unavailable for this Python"; \
	fi

clean-dist:
	@echo "[clean-dist]"
	$(UV_RUN) python -c "import shutil; shutil.rmtree('dist', ignore_errors=True)"

build-package: clean-dist
	@echo "[build-package]"
	$(UV_RUN) python -m build

package-check: build-package
	@echo "[package-check]"
	$(UV_RUN) twine check dist/*
	$(UV_RUN) check-wheel-contents dist/*.whl

publication-checks: check-all version-check release-status package-check

publish: publication-checks

# ---------------------------------------------------------------------------
# Rust / maturin targets
# ---------------------------------------------------------------------------

build-rust:
	@echo "[build-rust]"
	$(UV_RUN) maturin develop --release

build-rust-debug:
	@echo "[build-rust-debug]"
	$(UV_RUN) maturin develop

build-rust-wheel:
	@echo "[build-rust-wheel]"
	$(UV_RUN) maturin build --release --out dist

check-rust:
	@echo "[check-rust]"
	cargo check
	cargo clippy -- -D warnings

test-rust:
	@echo "[test-rust]"
	cargo test

clean-rust:
	@echo "[clean-rust]"
	-cargo clean
	-$(UV_RUN) python -c "from pathlib import Path; [path.unlink() for path in Path('markpickle').glob('_markpickle*.so')]; [path.unlink() for path in Path('markpickle').glob('_markpickle*.pyd')]"
