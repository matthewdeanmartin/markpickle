import pytest

import markpickle


@pytest.mark.skip("This fails both to do lists as dicts and to do nested lists!")
def tests_so_example():
    marks = """- launchers
    - say hello
      - command: echo "hello" | festival --tts
      - icon: shebang.svg
    - say world
      - command: echo "world" | festival --tts
      - icon: shebang.svg
    - say date
      - command: date | festival --tts"""
    result = markpickle.loads(marks)
    assert result
