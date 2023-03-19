"""
Serialize a subset of python types to Markdown and deserialize those.

Will not be able to meaningfully serialize all Markdown to a sensible python type.
"""
from markpickle.config_class import Config
from markpickle.deserialize import load, loads
from markpickle.serialize import dump, dumps

__all__ = ["dump", "load", "dumps", "loads", "Config"]
