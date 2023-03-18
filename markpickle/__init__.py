"""
Serialize a subset of python types to Markdown and deserialize those.

Will not be able to meaningfully serialize all Markdown to a sensible python type.
"""
from markpickle.deserialize import DeserializationConfig, loads, load
from markpickle.serialize import dumps, SerializationConfig, dump

__all__ = ["dump", "load",
           "dumps", "loads",
           "SerializationConfig", "DeserializationConfig"]
