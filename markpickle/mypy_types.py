"""
Subset of python types that markpickle will attempt to roundtrip
"""
from __future__ import annotations

import datetime
from typing import Any, Optional, Union, TypeAlias

# this isn't 3.9 compatible. Can't catch ModuleNotFound!
# try:
#     from typing_extensions import TypeAlias
# except ModuleNotFoundError:
#     from typing import TypeAlias  # type: ignore[no-redef,attr-defined]
# except ImportError:
#    from typing import TypeAlias  # type: ignore[no-redef,attr-defined]


# https://github.com/python/mypy/issues/14219#issuecomment-1528993478
ScalarTypes = Union[
    None,
    str,
    int,
    float,
    datetime.date,
]
# There are many ways to represent a table
ColumnsValuesTableType = list[Union[tuple[str, ...], list[Any]]]
SerializableTypes: TypeAlias = Union[
    ColumnsValuesTableType,
    # ATX headers
    dict[str, "SerializableTypes"],
    # lists and nested lists
    list["SerializableTypes"],
    # series of paragraphs/lists/etc
    tuple["SerializableTypes"],
    str,
    int,
    float,
    bool,
    datetime.date,
    None,
    # bytes
    # images
    # urls
]
DictTypes = dict[str, SerializableTypes]
ListTypes = list[SerializableTypes]

# Intermediate states for parsing AST
MistuneTokenList = list[dict[str, Any]]  # list[dict[Optional[str], Any]]
# for when the key is None because it is actually a list.
PossibleDictTypes = dict[Optional[str], Union[SerializableTypes, MistuneTokenList]]
