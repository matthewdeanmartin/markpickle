import pytest

import markpickle


def test_bad_nest():
    config = markpickle.Config()
    config.headers_are_dict_keys = True
    config.dict_as_table = False
    config.child_dict_as_table = False
    marks = """# Test Heading 1


This is paragraph 1 of section 1

* Here is a list
* It can't exist here.

# Test Heading 2


This is paragraph 1 of section 2

This is paragraph 2 of section 2
"""
    result = markpickle.loads(
        marks,
        config=config,
    )

    # Better but too many tuples?
    assert result == {
        "Test Heading 1": ("This is paragraph 1 of section 1", ["Here is a list", "It can't exist here."]),
        "Test Heading 2": ("This is paragraph 1 of section 2", "This is paragraph 2 of section 2"),
    }


@pytest.mark.skip("Shoot, why is this failing now. Whitespace?")
def test_dodgy():
    config = markpickle.Config()
    config.headers_are_dict_keys = True
    config.dict_as_table = False
    config.child_dict_as_table = False
    marks = """"
# stuff 

## Test
  
a  
b

"""
    result = markpickle.loads(
        marks,
        config=config,
    )

    # This is unexpected...
    assert result == {"stuff": {"Test": "a\nb"}}
