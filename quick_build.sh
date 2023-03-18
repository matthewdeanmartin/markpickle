#!/usr/bin/env bash
# set -euo pipefail
PROJECT=markpickle
mypy $PROJECT
pylint $PROJECT
pytest test
pytest markpickle --doctest-modules