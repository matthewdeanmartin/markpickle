"""
Config for serializing and deserializing. They need to be the same for increasing the odds of successful round tripping.
"""

import dataclasses
from typing import Callable, Optional


@dataclasses.dataclass
class Config:
    """Both serialization and deserialization config."""

    infer_scalar_types: bool = True
    """If true, infer scalar types from the string representation. If false, leave everything as a string"""

    true_values: list[str] = dataclasses.field(default_factory=lambda: ["True", "true"])
    """What to write when a value is True or False"""

    false_values: list[str] = dataclasses.field(default_factory=lambda: ["False", "false"])
    """What to write when a value is True or False"""

    none_values: list[str] = dataclasses.field(default_factory=lambda: ["None", "nil", "nil"])
    """What to write when a value is None"""

    empty_string_is: str = ""

    tables_become_list_of_tuples = False
    """If true, tables become list of tuples. If false, tables become list of dicts"""

    serialize_headers_are_dict_keys: bool = True
    """If true, use dict keys as headers when serializing a dict as a table"""

    serialize_dict_as_table: bool = False
    """If true, serialize a dict as a table if it is not a child of a dict"""

    serialize_child_dict_as_table: bool = True
    """If true, serialize a dict as a table if it is a child of a dict"""

    serialize_tables_tabulate_style: bool = False
    """If true, use tabulate to render tables. If false, use a custom renderer"""

    serialize_force_final_newline: bool = False
    """If true, all serializations must end in newline"""

    serialize_bytes_mime_type: str = "image/png"
    """If something reasonable, like `application/octet-stream`, some markdown parsers assume it is malicious 
    and will treat the whole URL as text."""

    none_string: str = "None"
    """What to write when a value is None"""

    serialize_date_format: str = "%Y-%m-%d"
    """Strftime compatible format for dates"""

    serialized_datetime_format: str = "%Y-%m-%d %H:%M:%S"
    """Strftime compatible format for datetimes"""

    list_bullet_style: str = "-"
    """Specifies the bullet style to use for lists in the serialized markdown (e.g., "-", "*", "+")."""

    serialize_include_python_type: bool = False
    """Help deserializer find correct constructor"""

    serialize_images_to_pillow: bool = False

    default: Optional[Callable[[object], str]] = None

    deserialized_add_missing_key: bool = True
    """If document has ATX headers add missing initial ATX header"""

    deserialized_missing_key_name: str = "Missing Key"
    """Add `# Missing Key` to head of document if missing."""
