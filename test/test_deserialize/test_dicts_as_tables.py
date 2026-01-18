import markpickle


def test_deserialized_dict_serialized_as_table():
    marks = """
| 1          |
| ---------- |
| 2000-01-01 |
"""
    config = markpickle.Config()
    config.tables_become_list_of_lists = True
    result = markpickle.loads(marks, config)
    assert result == [["1"], ["2000-01-01"]]


def test_panda_style():
    marks = """| weekday   |   temperature |   precipitation |
|:----------|--------------:|----------------:|
| monday    |            20 |             100 |
| thursday  |            30 |             200 |
| wednesday |            25 |             150 |"""
    config = markpickle.Config()
    config.tables_become_list_of_lists = True
    result = markpickle.loads(marks, config)
    assert result == [
        ["weekday", "temperature", "precipitation"],
        ["monday", "20", "100"],
        ["thursday", "30", "200"],
        ["wednesday", "25", "150"],
    ]


def test_deserialized_dict_serialized_as_table_version_two():
    marks = """
| head1      | head2      |
| ---------- | ---------- |
| row1-head1 | row1-head2 |
| row2-head1 | row2-head2 |
"""
    config = markpickle.Config()
    config.tables_become_list_of_lists = False
    result = markpickle.loads(marks, config)
    assert result == [{"head1": "row1-head1", "head2": "row1-head2"}, {"head1": "row2-head1", "head2": "row2-head2"}]


def test_deserialized_dict_with_multi_word_headings():
    marks = """
| head1      | head2 with words |
| ---------- | ---------------- |
| row1-head1 | row1-head2       |
| row2-head1 | row2-head2       |
"""
    config = markpickle.Config()
    config.tables_become_list_of_lists = False
    result = markpickle.loads(marks, config)
    assert result == [
        {"head1": "row1-head1", "head2 with words": "row1-head2"},
        {"head1": "row2-head1", "head2 with words": "row2-head2"},
    ]


def test_deserialized_dict_with_multi_empty_headings():
    marks = """
| head1      |                | head3      |
| ---------- | -------------- | ---------- |
| row1-head1 | row1-blankhead | row1-head3 |
| row2-head1 | row2-blankhead | row2-head3 |
"""
    config = markpickle.Config()
    config.tables_become_list_of_lists = False
    result = markpickle.loads(marks, config)
    assert result == [
        {"head1": "row1-head1", "": "row1-blankhead", "head3": "row1-head3"},
        {"head1": "row2-head1", "": "row2-blankhead", "head3": "row2-head3"},
    ]
