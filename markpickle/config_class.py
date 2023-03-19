"""
Config for serializing and deserializing. They need to be the same for increasing the odds of successful round tripping.
"""
import dataclasses


@dataclasses.dataclass
class Config:
    """Both serialization and deserialization config."""

    infer_scalar_types: bool = True
    true_values: list[str] = dataclasses.field(default_factory=lambda: ["True", "true"])
    false_values: list[str] = dataclasses.field(default_factory=lambda: ["False", "false"])
    none_values: list[str] = dataclasses.field(default_factory=lambda: ["None", "nil", "nil"])
    empty_string_is: str = ""
    tables_become_list_of_tuples = True

    serialize_headers_are_dict_keys: bool = True
    serialize_dict_as_table: bool = False
    serialize_child_dict_as_table: bool = True
    serialize_tables_tabulate_style: bool = False
    none_string: str = "None"
    serialize_run_formatter: bool = False
    serialize_date_format: str = "%Y-%m-%d"
    """Strftime compatible"""
    serialized_datetime_format: str = "%Y-%m-%d %H:%M:%S"
