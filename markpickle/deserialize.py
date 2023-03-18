"""
String -> Python

Strings made by markpickle should pass and create a variety of simple python types.

Arbitrary strings might not pass or may pass but create values that still have unparsed markdown in them.
"""
import dataclasses
import datetime
import io
import textwrap
from typing import Any, Optional, cast, Union
import mistune


from markpickle.mypy_types import DictTypes, ListTypes, ScalarTypes, SerializableTypes

@dataclasses.dataclass
class DeserializationConfig():
    infer_scalar_types: bool= True
    true_values: list[str]= dataclasses.field(default_factory=lambda: ["True", "true"])
    false_values: list[str]= dataclasses.field(default_factory=lambda: ["False", "false"])
    none_values:list[str]= dataclasses.field(default_factory=lambda: ["None", "nil", "nil"])
    empty_string_is:str = ""
    root: Optional[str]=None


def loads(value: str, config: Optional[DeserializationConfig] = None) -> SerializableTypes:
    """
    Convert certain markdown strings into simple python types

    >>> loads("- a\\n- b\\n - c\\n")
    ['a', 'b', 'c']
    """
    if not config:
        config = DeserializationConfig()
    stream = io.StringIO(value)
    return load(stream, config)


def is_float(value: str) -> bool:
    """
    True if is parsable as a float

    >>> is_float("1")
    True

    >>> is_float("a")
    False
    """
    try:
        float(value)
        return True
    except TypeError:
        return False
    except ValueError:
        return False


def extract_scalar(value:str, config:DeserializationConfig) -> ScalarTypes:
    """
    Infer datatypes, mostly expecting python-like string representations.

    >>> extract_scalar("1")
    1
    """
    if value in config.true_values:
        return True
    if value in config.false_values:
        return False
    if value.isnumeric() and config.infer_scalar_types:
        return int(value)
    if "-" in value:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    if "." in value and is_float(value) and config.infer_scalar_types:
        return float(value)
    return value


def process_list(list_ast: Any, config: DeserializationConfig) -> Optional[ListTypes]:
    """Deserialize a markdown list in AST form"""
    current_list = []
    for token in list_ast["children"]:
        if token["type"] == "list_item":
            if token["children"][0]["type"] == "block_text":
                block_text = token["children"][0]
                if block_text["children"][0]["type"] == "text":
                    current_value = ",".join(text["text"] for text in block_text["children"])
                    scalar = extract_scalar(current_value, config)
                    current_list.append(scalar)
                else:
                    raise NotImplementedError()
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()
    return current_list


def load(value: io.StringIO, config: Optional[DeserializationConfig] = None) -> SerializableTypes:
    """
    Convert certain markdown streams into simple python types

    >>> import io
    >>> load(io.StringIO("- a\\n- b\\n - c\\n"))
    ['a', 'b', 'c']
    """
    if not config:
        config = DeserializationConfig()

    # too much is RawText?
    # d = Document([marks.read()])
    # output = ast_renderer.get_ast(d)
    # assert output

    # Better!
    # markdown = marko.Markdown(renderer=ASTRenderer)
    # rerendered = markdown(marks.read())
    # assert rerendered

    string_value = value.read()
    # TODO: maybe only do this if top level is block_code
    string_value = textwrap.dedent(string_value)
    # empty document
    if not string_value:
        # Exists to improve round tripping for unit tests
        return cast(SerializableTypes, config.empty_string_is)

    parser = mistune.create_markdown(renderer="ast")
    result = parser.parse(string_value)

    if len(result) == 1 and result[0]["type"] == "list":
        return process_list(result[0], config)

    possible_dict: DictTypes = {}

    current_key = None
    for token in result:
        if token["type"] == "newline":
            # whitespace, no impact on datatype
            continue
        if token["type"] == "heading" and token["level"] == 1 and config.root:
            # skip roots, this would correspond to the name of the variable holding a dict
            continue
        if token["type"] == "heading" and current_key is None:
            # dict key, value not found yet
            current_key = ",".join([_["text"] for _ in token["children"]])
            possible_dict[current_key] = None

        elif token["type"] == "list" and current_key is not None:
            # dict value of type list
            if token["children"][0]["type"] == "text":
                possible_dict[current_key] = [
                    ",".join(_["text"] for _ in item["children"]) for item in token["children"]
                ]
                current_key = None
            elif token["children"][0]["type"] == "list_item":
                possible_dict[current_key] = process_list(token, config)
                current_key = None
            else:
                raise NotImplementedError()
        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and len(token["children"]) == 1
            and token["children"][0]["type"] == "text"
            and not possible_dict
        ):
            # root scalar
            current_text_value: str = token["children"][0]["text"]
            return extract_scalar(current_text_value, config)
        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and len(token["children"]) == 1
            and token["children"][0]["type"] == "text"
            and possible_dict
            and current_key
        ):
            # root scalar
            current_value: str = token["children"][0]["text"]
            scalar = extract_scalar(current_value, config)
            possible_dict[current_key] = scalar
            current_key = None
        else:
            raise NotImplementedError()

    return possible_dict
