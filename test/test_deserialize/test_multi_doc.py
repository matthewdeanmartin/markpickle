from __future__ import annotations
from markpickle import loads_all


def test_loads_all():
    marks = """1
---
2
---
3
"""
    result = list(loads_all(marks))
    # shouldn't be any blanks
    assert not any([_ == "" for _ in result])
    # docs 1,2,3 (integers because infer_scalar_types=True by default)
    assert result[0] == 1
    assert result[1] == 2
    assert result[2] == 3
    # 3 total
    assert len(result) == 3
