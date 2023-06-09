"""
Get Class source for de/serialization
"""
import inspect


def serialize_source(obj) -> str:
    return inspect.getsource(obj)


class Foobar:
    def __init__(self, x, y):
        self.x = x
        self.y = y


if __name__ == "__main__":
    foobar = Foobar(123, 456)
    result = serialize_source(type(foobar))
    assert result
