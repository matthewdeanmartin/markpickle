from markpickle import loads


def test_single_dict_second_level_headers():
    result = loads(
        """
# first book

## author
Jane Doe
## title
The little one
## pub_date
1988

# second book

## author
John Doe
## title
The big one
## pub_date
1942
"""
    )
    assert result == {
        "first book": {"author": "Jane Doe", "title": "The little one", "pub_date": 1988},
        "second book": {"author": "John Doe", "title": "The big one", "pub_date": 1942},
    }
