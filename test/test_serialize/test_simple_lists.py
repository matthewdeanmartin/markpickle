from markpickle import dumps


def test_empty_list():
    result = dumps([])
    assert result == ""


def test_list_of_str():
    result = dumps(["a", "b", "c"])
    assert result == "- a\n- b\n- c\n"


def test_list_of_int():
    result = dumps([1, 2, 3])
    assert result == "- 1\n- 2\n- 3\n"


def test_rooted_list():
    markdown = dumps(["a", "b", "c"], "list")
    assert markdown == "# list\n- a\n- b\n- c\n"


def test_rooted_mixed_list():
    markdown = dumps([1, "b", 1.2], "mixed type values")
    assert markdown == "# mixed type values\n- 1\n- b\n- 1.2\n"


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
