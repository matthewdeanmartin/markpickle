"""
Creative Commons license: https://stackoverflow.com/questions/54125181/how-to-convert-markdown-to-json
"""

import markpickle

DATA = """
```{python}
from __future__ import division
from deltasigma import *
```

#### 5th-order modulator: NTF *with* zeros optimization

This time we enable the zeros optimization, setting `opt=1` when calling synthesizeNTF(), then replot the NTF as above.

* 0 -> not optimized,
* 1 -> optimized,
* 2 -> optimized with at least one zero at band-center,
* 3 -> optimized zeros (with optimizer)
* 4 -> same as 3, but with at least one zero at band-center
* [z] -> zero locations in complex form
"""


def test_it():
    result = markpickle.loads(DATA)
    # Adding a missing key and inventing "tuples" instead of node-children was best I could do.
    assert result == {
        "Missing Key": "from __future__ import division\nfrom deltasigma import *\n",
        "5th-order modulator: NTF  with  zeros optimization": (
            "This time we enable the zeros optimization, setting  opt=1  when calling synthesizeNTF(), then replot the NTF as above.",
            [
                "0 -> not optimized,",
                "1 -> optimized,",
                "2 -> optimized with at least one zero at band-center,",
                "3 -> optimized zeros (with optimizer)",
                "4 -> same as 3, but with at least one zero at band-center",
                "[z], -> zero locations in complex form",
            ],
        ),
    }


def test_some_nested_lists():
    # CC license
    # https://stackoverflow.com/questions/75742315/using-python-to-remove-the-unordered-lists-that-do-not-have-unordered-sublists-i
    nested_lists = """# Known

* Languages with Latin alphabet:
  * English
  * French
  * Portuguese

* Languages with Greek alphabet:
  * Greek

* Languages with Armenian alphabet:

* Languages with Ethiopic script:

* Languages with Tamil script:

* Languages with Hiragana characters:
  * Japanese

* Languages with Klingon script:

# Wanted

**These wanted languages:**

* Languages with Sumero-Akkadian script:

* Languages with Hangul characters:
  * Korean

* Languages with Linear A script:"""

    # These wanted languages is what screws it up as a data structure.
    result = markpickle.loads(nested_lists)
    assert result
