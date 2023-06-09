"""
Public utility functions
"""
import json

import markpickle


def convert_json_to_markdown(json_string: str) -> str:
    """Convert from one string representation to another, json to markdown"""
    json_as_dict = json.loads(json_string)
    return markpickle.dumps(json_as_dict)


def convert_markdown_to_json(markdown_string: str) -> str:
    """Convert from one string representation to another, markdown to json"""
    markdown_as_dict = markpickle.loads(markdown_string)
    return json.dumps(markdown_as_dict)
