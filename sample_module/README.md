# How much can we code in python embedded in markdown?

## Build tools

- See markmodule for start of `import foo` from foo.md
- [blacken-docs](https://github.com/adamchainz/blacken-docs) works.
- [flake8-markdown](https://github.com/johnfraney/flake8-markdown) works.

### Four different ways to run tests

Good ones

- [pytest-markdown-docs](https://github.com/modal-labs/pytest-markdown-docs) Best at the moment for simple test runner.
- [pytest_codeblocks](https://pypi.org/project/pytest_codeblocks/)

Problematic ones (as of May 14, 2023)

- [pytest-markdown](https://github.com/Jc2k/pytest-markdown) is buggy (not pytest 7 compatible?)
- [markdown-pytest](https://github.com/mosquito/markdown-pytest) all python code blocks are "tests" and named with HTML comment.
- [pytest2md](https://github.com/axiros/pytest2md) quirky combination of test runner, test results generator, documenation generator.
- [pytest-markdoctest](https://pypi.org/project/pytest-markdoctest/) handles *doctests* in markdown. pypi packages are broken as of May 14, 2023. See my branch for a fix. Also, only compatible with pytest 6.2.5 (?)

## Gaps

- Not so much for a test runner that is maintained and just runs tests in markdown.
