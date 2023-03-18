import markpickle


def test_zero():
    value = 0
    value0 = markpickle.dumps(value=value)
    value1 = markpickle.loads(value=value0)
    assert value == value1


def test_zero_dict():
    # 0 != {'0': 0}
    value = {"0": 0}
    value0 = markpickle.dumps(value=value)
    value1 = markpickle.loads(value=value0)
    assert value == value1


# def test_scalar_with_root_looks_like_dict():
#     # 0 != {'0': 0}
#     value = 0 # "{'0': 0}
#
#     value0 = markpickle.dumps(value=value, root="0")
#     value1 = markpickle.loads(value=value0)
#     assert value == value1
