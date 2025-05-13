"""
Scalars are just python repr or str. No not very portable.
"""

from markpickle import loads


def test_scalar_str():
    result = loads("a")
    assert result == "a"


def test_scalar_int():
    result = loads("1")
    assert result == 1


def test_scalar_float():
    result = loads("1.2")
    assert result == 1.2


def test_scalar_bool():
    result = loads("True")
    assert result is True
