"""
Subset of python types that markpickle will attempt to roundtrip
"""

from __future__ import annotations

import datetime
from typing import Any, Optional, TypeAlias, Union

# https://github.com/python/mypy/issues/14219#issuecomment-1528993478
ScalarTypes = Union[
    None,
    str,
    int,
    float,
    datetime.date,
]
# There are many ways to represent a table
ColumnsValuesTableType = list[tuple[str, ...] | list[Any]]
SerializableTypes: TypeAlias = (
    ColumnsValuesTableType
    | dict[str, "SerializableTypes"]
    | list["SerializableTypes"]
    | tuple["SerializableTypes"]
    | str
    | int
    | float
    | bool
    | datetime.date
    | None
)
DictTypes = dict[str, SerializableTypes]
ListTypes = list[SerializableTypes]

# Intermediate states for parsing AST
MistuneTokenList = list[dict[str, Any]]  # list[dict[Optional[str], Any]]
# for when the key is None because it is actually a list.
PossibleDictTypes = dict[Optional[str], SerializableTypes | MistuneTokenList]
