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
    # Ordered lists now become tuples by default (2.0.0)
    assert result == {
        "Second level heading": ["list1", "list2", "list3"],
        "2nd Second level heading": ("list4", "list5", "list6"),
    }
