from __future__ import annotations
import pytest

import markpickle


@pytest.fixture
def complex_data():
    return {
        "project": "markpickle",
        "version": "1.6.4",
        "nested": {"list": [1, 2, 3, {"a": "b"}], "bool": True, "none": None},
        "table": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
    }


def test_benchmark_dumps(benchmark, complex_data):
    benchmark(markpickle.dumps, complex_data)


def test_benchmark_loads(benchmark, complex_data):
    markdown = markpickle.dumps(complex_data)
    benchmark(markpickle.loads, markdown)
