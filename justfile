md_lint:
    npx markdownlint-cli docs/individual

test:
    uv run  pytest test

hypothesis:
    uv run pytest test_hypothesis
