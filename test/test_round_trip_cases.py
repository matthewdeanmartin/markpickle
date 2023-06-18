import markpickle


def test_zero():
    value = 0
    value0 = markpickle.dumps(value=value)
    value1 = markpickle.loads(value=value0)
    assert value == value1


def test_round_trip_date():
    config = markpickle.Config()
    value = [{"1": "2000-01-01"}]
    markdown = markpickle.dumps(value=value, config=config)
    value1 = markpickle.loads(value=markdown, config=config)
    assert value == value1

    # This can't happen deterministicly
    markdown = markpickle.dumps(value=value, config=config)
    value1 = markpickle.loads(value=markdown, config=config)
    assert value1 == [{"1": "2000-01-01"}]


def test_zero_dict():
    # 0 != {'0': 0}
    value = {"0": 0}
    value0 = markpickle.dumps(value=value)
    value1 = markpickle.loads(value=value0)
    assert value == value1


def test_scalar_with_root_looks_like_dict():
    # 0 != {'0': 0}
    value = 0  # "{'0': 0}

    value0 = markpickle.dumps(value=value)
    # '# 0\n0'
    value1 = markpickle.loads(value=value0)
    assert value == value1
