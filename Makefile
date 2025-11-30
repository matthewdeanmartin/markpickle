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

check: test pylint bandit pre-commit mypy

.PHONY: publish
publish: check
	rm -rf dist && $(VENV) hatch build
