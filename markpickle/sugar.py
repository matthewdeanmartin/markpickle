"""
Public utility functions
"""

import json

from markpickle.deserialize import loads
from markpickle.serialize import dumps


def convert_json_to_markdown(json_string: str) -> str:
    """Convert from one string representation to another, json to markdown"""
    json_as_dict = json.loads(json_string)
    return dumps(json_as_dict)


def convert_markdown_to_json(markdown_string: str) -> str:
    """Convert from one string representation to another, markdown to json"""
    markdown_as_dict = loads(markdown_string)
    return json.dumps(markdown_as_dict)
