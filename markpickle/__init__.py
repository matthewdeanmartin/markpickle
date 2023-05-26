"""
Serialize a subset of python types to Markdown and deserialize those.

Will not be able to meaningfully serialize all Markdown to a sensible python type.
"""
from markpickle.config_class import Config
from markpickle.deserialize import load, load_all, loads, loads_all
from markpickle.serialize import dump, dump_all, dumps, dumps_all
from markpickle.split_file_code import split_file

__all__ = [
    "load",
    "load_all",
    "loads",
    "loads_all",
    "dump",
    "dump_all",
    "dumps",
    "dumps_all",
    "Config",
    "split_file",
]
