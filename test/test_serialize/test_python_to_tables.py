import io

from markpickle.python_to_tables import list_of_dict_to_markdown


def test_list_of_dict_to_markdown():
    stream = io.StringIO()
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    list_of_dict_to_markdown(stream, data)
    stream.seek(0)
    markdown = stream.read()
    assert (
        markdown
        == """| a | b |
| - | - |
| 1 | 2 |
| 3 | 4 |
"""
    )
