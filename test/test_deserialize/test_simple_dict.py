import markpickle
from markpickle import loads


def test_empty_dict():
    config = markpickle.Config()
    config.empty_string_is = {}
    result = loads("", config)
    assert result == {}


def test_single_dict():
    result = loads("# author\njane\n# title\nthe little one\n# pub_date\n1988\n")
    assert result == {"author": "jane", "title": "the little one", "pub_date": 1988}


def test_single_dict_second_level_headers():
    result = loads("## author\njane\n## title\nthe little one\n## pub_date\n1988\n")
    assert result == {"author": "jane", "title": "the little one", "pub_date": 1988}
