from __future__ import annotations
from markpickle import dumps


def test_multireader():
    markdown = """
    ---
    6
    ---
    - a
    - b
    - c
    """
    result = dumps(markdown)
    assert result == markdown
