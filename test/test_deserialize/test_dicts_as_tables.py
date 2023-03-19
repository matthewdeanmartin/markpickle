import datetime

import pytest

import markpickle


def test_deserialized_dict_serialized_as_table():
    marks = """
| 1          |
| ---------- |
| 2000-01-01 |
"""
    config = markpickle.Config()
    with pytest.raises(NotImplementedError):
        result = markpickle.loads(marks, config)
        assert result == {"1": datetime.date(2000, 1, 1)}
