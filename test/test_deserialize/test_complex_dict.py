import markpickle


def test_dictionary_of_lists():
    marks = """
    # Top level heading

    ## Second level heading
    - list1
    - list2
    - list3

    ## 2nd Second level heading
    1. list4
    2. list5
    3. list6
        """
    config = markpickle.DeserializationConfig()
    config.root = "Top level heading"
    result = markpickle.loads(marks, config)
    assert result == {
        "Second level heading": ["list1", "list2", "list3"],
        "2nd Second level heading": ["list4", "list5", "list6"],
    }
