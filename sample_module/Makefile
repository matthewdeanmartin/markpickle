# if you wrap everything in pipenv run, it runs slower.
ifeq ($(origin VIRTUAL_ENV),undefined)
    VENV := pipenv run
else
    VENV :=
endif

test:
	@echo "Running .py unit tests"
	$(VENV) py.test test

test_md_docs:
	@echo "Running unit tests for pytests found in blocks"
	$(VENV) py.test test --markdown-docs

test_md_codeblocks:
	@echo "Running pytests and code in blocks as if it was a pytest"
	$(VENV) py.test test --codeblocks

.PHONY: black
black:
	@echo "Formatting code"
	$(VENV) black .
	$(VENV) blacken-docs **/*.md --skip-errors

lint: black
	@echo "Linting code"
	$(VENV) flake8-markdown **/*.md

check: black lint markdown_tests
