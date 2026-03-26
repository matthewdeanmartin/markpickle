from __future__ import annotations
import markpickle


def test_dictionary_of_lists():
    marks = """# Second level heading
- list1
- list2
- list3

# 2nd Second level heading
1. list4
2. list5
3. list6
"""
    config = markpickle.Config()
    # config.root = "Top level heading"
    result = markpickle.loads(marks, config)
    # ordered_list_as_tuple defaults to False — ordered lists are plain lists
    assert result == {
        "Second level heading": ["list1", "list2", "list3"],
        "2nd Second level heading": ["list4", "list5", "list6"],
    }
