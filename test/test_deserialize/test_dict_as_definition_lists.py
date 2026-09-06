from __future__ import annotations

import mistune

import markpickle

_MISTUNE_MAJOR = int(mistune.__version__.split(".", maxsplit=1)[0])


def test_deserialized_dict_serialized_as_definition_list():
    marks = """
Apple
:   Pomaceous fruit of plants of the genus Malus in
    the family Rosaceae.

Orange
:   The fruit of an evergreen tree of the genus Citrus."""
    config = markpickle.Config()
    result = markpickle.loads(marks, config)

    if _MISTUNE_MAJOR >= 3:
        # mistune 3 correctly folds the indented continuation line into its definition.
        assert result == (
            {"Apple": "Pomaceous fruit of plants of the genus Malus in\nthe family Rosaceae."},
            {"Orange": "The fruit of an evergreen tree of the genus Citrus."},
        )
    else:
        # mistune 2 did not know the text continued, so the second line escaped as a
        # bare string sandwiched between the two definitions.
        assert result == (
            {"Apple": "Pomaceous fruit of plants of the genus Malus in"},
            "the family Rosaceae.\n\n",
            {"Orange": "The fruit of an evergreen tree of the genus Citrus."},
        )
