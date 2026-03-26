# Repository guidance

- Use `uv run` for Python commands in this repository, especially tests such as `uv run pytest`.
- Do not assume an activated virtual environment; plain `pytest` may fail due to missing dev dependencies.
- If the environment is missing synced dependencies, run `uv sync --all-extras` before retrying Python commands, unit tests depend on the extras.
