"""
Increase odds of successful serialization by converting to simpler types
"""

from dataclasses import is_dataclass
from typing import Any


def can_class_to_dict(obj) -> bool:
    """Can we treat this as a dict"""
    if is_dataclass(obj):
        return True
    if isinstance(obj, type):
        return True
    if hasattr(obj, "__dict__"):
        return True
    return False


def class_to_dict(obj) -> dict[str, Any]:
    """
    Converts classes to dict

    Function written with ChatGPT 3.5 Turbo
    """
    if is_dataclass(obj):
        return obj.__dict__
    if isinstance(obj, type):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("__")}
    return obj.__dict__
