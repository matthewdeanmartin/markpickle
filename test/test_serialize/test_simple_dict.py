from markpickle import dumps


def test_empty_dict():
    result = dumps({})
    assert result == ""


def test_single_dict():
    result = dumps({"author": "jane", "title": "the little one", "pub_date": 1988})
    assert result == "# author\njane\n# title\nthe little one\n# pub_date\n1988\n"


def test_another_simple_dict():
    markdown = dumps(
        {
            "a": "1",
            "b": "2",
            "c": "2",
        }
    )
    assert markdown == "# a\n1\n# b\n2\n# c\n2\n"
