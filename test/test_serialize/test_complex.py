from markpickle import dumps


def test_rooted_dictionary_of_list_values():
    markdown = dumps(
        {
            "a": ["1", "2", "3"],
            "b": ["4", "5", "6"],
            "c": ["7", "8", "9"],
        }
    )
    assert (
        markdown
        == """- a
  - 1
  - 2
  - 3
- b
  - 4
  - 5
  - 6
- c
  - 7
  - 8
  - 9"""
    )


def test_rooted_dict_of_list_of_objects():
    markdown = dumps(
        {
            "book1": [{"author": "jane", "pub_date": 1988}, {"author": "janet", "pub_date": 2010}],
            "book2": [{"author": "john", "pub_date": 1922}, {"author": "john", "pub_date": 1800}],
        }
    )
    assert (
        markdown
        == """# book1
| author | pub_date |
| ------ | -------- |
| jane   | 1988     |
| janet  | 2010     |
# book2
| author | pub_date |
| ------ | -------- |
| john   | 1922     |
| john   | 1800     |"""
    )


def test_rooted_list_of_objects():
    markdown = dumps(
        [
            {"author": "jane", "title": "the little one", "pub_date": 1988},
            {"author": "janet", "title": "the big one", "pub_date": 2010},
        ]
    )
    assert (
        markdown
        == """| author | title          | pub_date |
| ------ | -------------- | -------- |
| jane   | the little one | 1988     |
| janet  | the big one    | 2010     |"""
    )


def test_dict_of_dicts_as_tables():
    markdown = dumps({"Best Cat": {"animal": "cat", "name": "Frisky"}, "Best Dog": {"animal": "dog", "name": "Fido"}})

    assert (
        markdown
        == """# Best Cat

 | animal | name   |
 | ------ | ------ |
 | cat    | Frisky |

# Best Dog

 | animal | name |
 | ------ | ---- |
 | dog    | Fido |
"""
    )
