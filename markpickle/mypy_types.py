"""
Subset of python types that markpickle will attempt to roundtrip
"""
import datetime
from typing import Union

ScalarTypes = Union[
    None,
    str,
    int,
    float,
    datetime.date,
]
DictTypes = Union[
    dict[str, ScalarTypes],
    # not sure if mypy support recursion here?
    dict[str, Union[ScalarTypes, list[ScalarTypes], dict[str, ScalarTypes]]],
]
ListTypes = Union[
    list[ScalarTypes],
    list[dict[str, ScalarTypes]],
]
ComplexTypes = Union[DictTypes, ListTypes]
SerializableTypes = Union[ScalarTypes, ComplexTypes]
