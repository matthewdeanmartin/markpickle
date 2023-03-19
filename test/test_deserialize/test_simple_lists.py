import markpickle
from markpickle import dumps, loads


def test_empty_list():
    config = markpickle.Config()
    config.empty_string_is = []
    result = loads("", config)
    assert result == []


def test_list_of_str():
    result = loads("- a\n- b\n- c\n")
    assert result == ["a", "b", "c"]


def test_list_of_int():
    result = loads("- 1\n- 2\n- 3\n")
    assert result == [1, 2, 3]


def test_list_of_dict_same_schema():
    result = dumps(
        [
            {"author": "jane", "title": "the little one", "pub_date": 1988},
            {"author": "janet", "title": "the big one", "pub_date": 2010},
        ]
    )
    assert (
        result
        == """| author | title          | pub_date |
| ------ | -------------- | -------- |
| jane   | the little one | 1988     |
| janet  | the big one    | 2010     |
"""
    )
