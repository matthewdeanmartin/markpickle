import markpickle


def test_deserialized_dict_serialized_as_definition_list():
    marks = """
Apple
:   Pomaceous fruit of plants of the genus Malus in
    the family Rosaceae.

Orange
:   The fruit of an evergreen tree of the genus Citrus."""
    config = markpickle.Config()
    result = markpickle.loads(marks, config)

    # mistune doesn't know that the text continues
    assert result == (
        {"Apple": "Pomaceous fruit of plants of the genus Malus in"},
        "the family Rosaceae.\n\n",
        {"Orange": "The fruit of an evergreen tree of the genus Citrus."},
    )
