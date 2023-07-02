md_lint:
    npx markdownlint-cli docs/individual

test:
    pipenv shell pytest test

hypothesis:
    pipenv shell pytest test_hypothesis