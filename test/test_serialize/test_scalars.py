"""
Scalars are just python repr or str. No not very portable.
"""
from markpickle import dumps


def test_list_of_str():
    result = dumps("a")
    assert result == "a"


def test_list_of_int():
    result = dumps(1)
    assert result == "1"


def test_list_of_float():
    result = dumps(1.2)
    assert result == "1.2"


def test_list_of_bool():
    result = dumps(True)
    assert result == "True"
