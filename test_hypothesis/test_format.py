"""
Does it generate clean Markdown?
"""
import mdformat

import markpickle
from test.examples_of_supported_types import EXAMPLES


def test_format_of_all_examples():
    for example in EXAMPLES:
        unformatted = markpickle.dumps(example)
        # unformatted = "\n\n# A header\n\n"
        formatted = mdformat.text(unformatted)
        if not (formatted == unformatted or formatted == unformatted + "\n"):
            print(formatted)
            print()
        assert formatted == unformatted or formatted == unformatted + "\n"
