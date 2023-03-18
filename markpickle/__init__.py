"""
Serialize a subset of python types to Markdown and deserialize those.

Will not be able to meaningfully serialize all Markdown to a sensible python type.
"""
from markpickle.deserialize import DeserializationConfig, load, loads
from markpickle.serialize import SerializationConfig, dump, dumps

__all__ = ["dump", "load", "dumps", "loads", "SerializationConfig", "DeserializationConfig"]
