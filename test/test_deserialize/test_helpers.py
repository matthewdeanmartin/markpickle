import datetime

import markpickle
from markpickle.deserialize import extract_scalar, is_float


def test_is_float():
    assert is_float("1")
    assert is_float("1")
    assert is_float("1.2")

    assert not is_float(datetime.date(2202, 1, 1))
    assert not is_float("a")
    assert not is_float(None)


def test_extract_scalar():
    config = markpickle.Config()
    assert extract_scalar("1", config=config) == 1
    assert extract_scalar("1.2", config=config) == 1.2
    assert extract_scalar("2202-1-1", config=config) == datetime.date(2202, 1, 1)

    assert extract_scalar("abc", config=config) == "abc"
    assert extract_scalar("True", config=config) is True
    assert extract_scalar("False", config=config) is False
