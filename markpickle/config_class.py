"""
Config for serializing and deserializing. They need to be the same for increasing the odds of successful round tripping.
"""
import dataclasses
import datetime

from markpickle.mypy_types import ScalarTypes


@dataclasses.dataclass
class Config:
    """Both serialization and deserialization config."""

    infer_scalar_types: bool = True
    true_values: list[str] = dataclasses.field(default_factory=lambda: ["True", "true"])
    false_values: list[str] = dataclasses.field(default_factory=lambda: ["False", "false"])
    none_values: list[str] = dataclasses.field(default_factory=lambda: ["None", "nil", "nil"])
    empty_string_is: str = ""

    serialize_headers_are_dict_keys: bool = True
    serialize_dict_as_table: bool = False
    serialize_child_dict_as_table: bool = True
    none_string: str = "None"
    serialize_run_formatter: bool = False
    serialize_date_format: str = "%Y-%m-%d"
    """Strftime compatible"""
    serialized_datetime_format: str = "%Y-%m-%d %H:%M:%S"


def unsafe_falsy_type(value: ScalarTypes) -> bool:
    """Warn user that blank structures don't have equivallent in markdown"""
    if value in ([], {}, (), "", "0", None):
        # falsies will not roundtrip.
        return True
    if isinstance(value, dict):
        if any(key in ([], {}, (), "", "0", None) for key in value.keys()):
            return True
        if any(dict_value in ([], {}, (), "", "0", None) for dict_value in value.values()):
            return True
    if isinstance(value, list):
        if any(list_value in ([], {}, (), "", "0", None) for list_value in value):
            return True
        for inner in value:
            if isinstance(inner, dict):
                if any(key in ([], {}, (), "", "0", None) for key in inner.keys()):
                    return True
                if any(dict_value in ([], {}, (), "", "0", None) for dict_value in inner.values()):
                    return True
    return False


def unsafe_scalar_type(value: ScalarTypes) -> bool:
    """Warn user that non-string types won't roundtrip"""
    if isinstance(
        value,
        (
            int,
            float,
            datetime.date,
        ),
    ):
        # we either get 0->"0" and then "0" is inferred to 0
        # and we also get "0"->"0" and then "0" is inferred to 0
        # or vica versa, for everything except strings.
        return True
    if isinstance(value, dict):
        if any(
            isinstance(
                key,
                (
                    int,
                    float,
                    datetime.date,
                ),
            )
            for key in value.keys()
        ):
            return True
        if any(
            isinstance(
                dict_value,
                (
                    int,
                    float,
                    datetime.date,
                ),
            )
            for dict_value in value.values()
        ):
            return True
    if isinstance(value, list):
        if any(
            isinstance(
                list_value,
                (
                    int,
                    float,
                    datetime.date,
                ),
            )
            for list_value in value
        ):
            return True
    return False
