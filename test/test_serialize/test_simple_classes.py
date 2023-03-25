import markpickle


class C:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_some_class():
    value = C(1, 2)
    result = markpickle.dumps(value)
    assert result

    def object_hook(value):
        if "python_type" in value:
            del value["python_type"]
        return C(**value)

    rehydrated = markpickle.loads(result, object_hook=object_hook)
    assert rehydrated.x == value.x and rehydrated.y == value.y
