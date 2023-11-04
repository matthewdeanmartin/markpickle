md_lint:
    npx markdownlint-cli docs/individual

test:
    poetry run pytest test

hypothesis:
    poetry shell pytest test_hypothesis
