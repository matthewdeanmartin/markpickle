"""
String -> Python

Strings made by markpickle should pass and create a variety of simple Python types.

Arbitrary strings might not pass or may pass but create values that still have unparsed markdown in them.
"""
import datetime
import io
import logging
import textwrap
from typing import Any, Generator, Optional, cast

import mistune

import markpickle.python_to_tables as python_to_tables
from markpickle.binary_streams import extract_bytes
from markpickle.config_class import Config
from markpickle.mypy_types import DictTypes, ListTypes, ScalarTypes, SerializableTypes


def loads(value: str, config: Optional[Config] = None, object_hook=None) -> SerializableTypes:
    """
    Convert certain markdown strings into simple Python types

    >>> loads("- a\\n- b\\n - c\\n")
    ['a', 'b', 'c']
    """
    if not config:
        config = Config()
    stream = io.StringIO(value)
    return load(stream, config, object_hook)


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
    except (TypeError, ValueError):
        return False


def extract_scalar(value: str, config: Config) -> ScalarTypes:
    """
    Infer datatypes, mostly expecting Python-like string representations.

    >>> extract_scalar("1",Config())
    1
    """
    # Handle special cases for None, True, and False
    if value == config.none_string:
        return None
    if value in config.true_values:
        return True
    if value in config.false_values:
        return False

    # Attempt to parse as int or float if infer_scalar_types is enabled
    if config.infer_scalar_types:
        if value.isnumeric():
            try:
                return int(value)
            except ValueError:
                pass
        if is_float(value):
            return float(value)

    # Attempt to parse as a date
    if value.count("-") == 2:
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            # that wasn't a date!
            pass

    # Return the value as a string if no other type matched
    return value


def process_list(list_ast: Any, config: Config) -> Optional[ListTypes]:
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


def load_all(
    value: io.StringIO, config: Optional[Config] = None, object_hook=None
) -> Generator[SerializableTypes, None, None]:
    """Load multiple documents from a single stream"""
    part = io.StringIO()
    has_data = False
    while True:
        line = value.readline()
        if line is None:
            break
        if line.startswith("---") and not has_data:
            continue
        if line.startswith("---"):
            part.seek(0)
            yield load(part, config, object_hook)
            has_data = False
            part = io.StringIO()
            continue
        part.write(line)
        has_data = True
    if has_data:
        part.seek(0)
        yield load(part, config, object_hook)


def loads_all(
    value: str, config: Optional[Config] = None, object_hook=None
) -> Generator[SerializableTypes, None, None]:
    """Load multiple documents from a single string"""
    part = io.StringIO()
    has_data = False
    stream = io.StringIO(value)
    while True:
        line = stream.readline()
        if line.startswith("---"):
            doc = part.read()
            yield loads(doc, config, object_hook)
            part = io.StringIO()
            break
        part.write(line)
        has_data = True
    if has_data:
        yield loads(part.read(), config, object_hook)


def load(value: io.StringIO, config: Optional[Config] = None, object_hook=None) -> SerializableTypes:
    """
    Convert certain markdown streams into simple Python types

    >>> import io
    >>> load(io.StringIO("- a\\n- b\\n - c\\n"))
    ['a', 'b', 'c']
    """
    if not config:
        config = Config()

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

    # Empty document
    if not string_value:
        # Exists to improve round-tripping for unit tests
        return cast(SerializableTypes, config.empty_string_is)

    parser = mistune.create_markdown(renderer="ast")
    result = parser.parse(string_value)

    # Process a list
    if len(result) == 1 and result[0]["type"] == "list":
        return process_list(result[0], config)

    possible_dict: DictTypes = {}
    current_key = None

    # Use this key when we find more text, ie a subsequent token that is just more text.
    most_recent_key = None

    # Iterate through tokens in the parsed result
    for token in result:
        if token["type"] == "newline":
            # Whitespace, no impact on datatype
            continue

        if token["type"] == "heading" and current_key is None:
            # Dict key, value not found yet
            if not all("text" in _ for _ in token["children"]):
                print("uh oh")
            current_key = ",".join([_["text"] for _ in token["children"]])
            possible_dict[current_key] = None
        elif token["type"] == "heading" and current_key is not None:
            # New dict key, value not found yet
            if not all("text" in _ for _ in token["children"]):
                print("uh oh")
            current_key = ",".join([_["text"] for _ in token["children"]])
            possible_dict[current_key] = None
        elif token["type"] == "list" and current_key is not None:
            # Dict value of type list
            if token["children"][0]["type"] == "text":
                possible_dict[current_key] = [
                    ",".join(_["text"] for _ in item["children"]) for item in token["children"]
                ]
                most_recent_key = current_key
                current_key = None
            elif token["children"][0]["type"] == "list_item":
                possible_dict[current_key] = process_list(token, config)
                most_recent_key = current_key
                current_key = None
            else:
                raise NotImplementedError()

        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and len(token["children"]) == 1
            and token["children"][0]["type"] in ("text", "image")
            and not possible_dict
        ):
            if token["children"][0]["type"] == "image":
                return extract_bytes(token["children"][0]["src"], config)

            # Root scalar
            current_text_value: str = token["children"][0]["text"]
            if current_text_value.count("|") >= 2 and config.tables_become_list_of_tuples:
                return python_to_tables.parse_table_with_regex(current_text_value)

            return extract_scalar(current_text_value, config)

        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and len(token["children"]) == 1
            and token["children"][0]["type"] == "text"
            and possible_dict
            and current_key
        ):
            # Root scalar
            if token["children"][0]["type"] == "text":
                current_value: str = token["children"][0]["text"]
                scalar = extract_scalar(current_value, config)
            elif token["children"][0]["type"] == "image":
                scalar = extract_bytes(token["children"][0]["src"], config)
            else:
                raise NotImplementedError()
            possible_dict[current_key] = scalar
            most_recent_key = current_key
            current_key = None
        elif (
            token["type"] == "paragraph"
            and token.get("children")
            # and len(token["children"]) == 1
            # and token["children"][0]["type"] == "text"
            and possible_dict
            and most_recent_key
            and not current_key
        ):
            series_of_children = token["children"]
            most_recent_key = handle_series_of_children(config, most_recent_key, possible_dict, series_of_children)
            current_key = None
        elif token["type"] == "block_code" and possible_dict:
            # Treat block code as just more text, no "styling"
            continuation_value: str = token["text"]
            scalar = extract_scalar(continuation_value, config)
            # continuation of text
            if most_recent_key and not current_key:
                possible_dict[most_recent_key] += "\n\n" + scalar
                current_key = None
            elif current_key:
                possible_dict[current_key] = scalar
            else:
                raise TypeError("This shouldn't happen")
        else:
            raise NotImplementedError(token["type"])

    # if possible_dict and possible_dict.get("python_type"):
    #     python_type = possible_dict.get("python_type")
    #     if constructor := globals().get(python_type):
    #         if hasattr(constructor, "__getstate__"):
    #             possible_dict = constructor.__setstate__(possible_dict)
    #         else:
    #             constructor(**possible_dict)

    # really? do I misunderstand this?
    if object_hook:
        return object_hook(possible_dict)

    return possible_dict


def handle_series_of_children(config: Config, most_recent_key: str, possible_dict: dict[str, Any], series_of_children):
    """Handle a series of children, which may be text, images, or links."""
    for inner_token in series_of_children:
        if inner_token["type"] == "image":
            possible_dict[most_recent_key] += extract_bytes(inner_token["src"], config)
        elif inner_token["type"] in ("image", "link"):
            logging.warning("not handling image or link")
            continue
        if "text" not in inner_token:
            raise NotImplementedError("Not text like?")
        continuation_value: str = inner_token["text"]
        scalar = extract_scalar(continuation_value, config)
        # continuation of text
        possible_dict[most_recent_key] += "\n\n" + scalar
        most_recent_key = most_recent_key

    return most_recent_key
