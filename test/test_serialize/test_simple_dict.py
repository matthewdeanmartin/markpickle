from markpickle import dumps


def test_empty_dict():
    result = dumps({})
    assert result == ""


def test_single_dict():
    result = dumps({"author": "jane", "title": "the little one", "pub_date": 1988})
    assert result == "# author\n\njane\n\n# title\n\nthe little one\n\n# pub_date\n\n1988\n"


def test_another_simple_dict():
    markdown = dumps(
        {
            "a": "1",
            "b": "2",
            "c": "2",
        }
    )
    assert markdown == "# a\n\n1\n\n# b\n\n2\n\n# c\n\n2\n"
