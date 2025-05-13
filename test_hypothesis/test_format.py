"""
Does it generate clean Markdown?
"""

from test.examples_of_supported_types import EXAMPLES

import mdformat

import markpickle


def test_format_of_all_examples():
    for example in EXAMPLES:
        unformatted = markpickle.dumps(example)
        # unformatted = "\n\n# A header\n\n"
        formatted = mdformat.text(unformatted)
        if formatted not in (unformatted, unformatted + "\n"):
            print(formatted)
            print()
        assert formatted in (unformatted, unformatted + "\n")
