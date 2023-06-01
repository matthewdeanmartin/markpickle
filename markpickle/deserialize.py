"""
String -> Python

Strings made by markpickle should pass and create a variety of simple Python types.

Arbitrary strings might not pass or may pass but create values that still have unparsed markdown in them.
"""
import datetime
import io
import logging
import textwrap
import urllib
from typing import Any, Generator, Optional, cast

import mistune

import markpickle.python_to_tables as python_to_tables
from markpickle.atx_as_dictionary import parse_outermost_dict
from markpickle.binary_streams import extract_bytes
from markpickle.config_class import Config
from markpickle.mypy_types import ListTypes, ScalarTypes, SerializableTypes


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
            for child in token["children"]:
                if child["type"] == "block_text":
                    block_text = child
                    if block_text["children"][0]["type"] == "text":
                        # This fails if not all text!
                        current_value = ",".join(str(text.get("text")) for text in block_text["children"])
                        scalar = extract_scalar(current_value, config)
                        current_list.append(scalar)
                    elif block_text["children"][0]["type"] == "link":
                        # Doesn't handle title or text
                        url = urllib.parse.urlparse(block_text["children"][0]["link"])
                        current_list.append(url)
                    else:
                        raise NotImplementedError(block_text["children"])
                elif child["type"] == "list":
                    current_list.append(process_list(child, config))
                else:
                    raise NotImplementedError(child["type"])
        else:
            raise NotImplementedError()
    return current_list


def load_all(
    value: io.StringIO, config: Optional[Config] = None, object_hook=None
) -> Generator[SerializableTypes, None, None]:
    """Load multiple documents from a single stream"""
    part = io.StringIO()
    has_data = True
    while True:
        line = value.readline()
        if line is None or line == "":
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
    # last part
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


def process_list_of_tokens(list_of_tokens: list[dict[str, Any]], config: Config):
    """Process a list of tokens to lists and scalars and so on."""
    # Tokens that are not ATX-dict-like headers
    return_value = None
    for token in list_of_tokens:
        if token["type"] == "newline":
            # Whitespace, no impact on datatype
            continue

        # if token["type"] == "heading" and current_key is None:
        #     # Dict key, value not found yet
        #     if not all("text" in _ for _ in token["children"]):
        #         print("uh oh")
        #     current_key = ",".join([_["text"] for _ in token["children"]])
        #     possible_dict[current_key] = None
        # elif token["type"] == "heading" and current_key is not None:
        #     # New dict key, value not found yet
        #     if not all("text" in _ for _ in token["children"]):
        #         print("uh oh")
        #     current_key = ",".join([_["text"] for _ in token["children"]])
        #     possible_dict[current_key] = None
        if token["type"] == "list":
            # Dict value of type list
            if token["children"][0]["type"] == "text":
                return_value = [",".join(_["text"] for _ in item["children"]) for item in token["children"]]
            elif token["children"][0]["type"] == "list_item":
                return_value = process_list(token, config)
            else:
                raise NotImplementedError()

        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and len(token["children"]) == 1
            and token["children"][0]["type"] in ("text", "image")
        ):
            if token["children"][0]["type"] == "image":
                return extract_bytes(token["children"][0]["src"], config)

            # Root scalar
            current_text_value: str = token["children"][0]["text"]
            if current_text_value.count("|") >= 2 and config.tables_become_list_of_tuples:
                return python_to_tables.parse_table_with_regex(current_text_value)
            elif current_text_value.count("|") >= 2:
                return python_to_tables.parse_table_to_list_of_dict(current_text_value)

            return extract_scalar(current_text_value, config)

        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and len(token["children"]) == 1
            and token["children"][0]["type"] == "text"
        ):
            # Root scalar
            if token["children"][0]["type"] == "text":
                current_value: str = token["children"][0]["text"]
                scalar = extract_scalar(current_value, config)
            elif token["children"][0]["type"] == "image":
                scalar = extract_bytes(token["children"][0]["src"], config)
            else:
                raise NotImplementedError()
            return_value = scalar
        # what was this?
        # elif (
        #         token["type"] == "paragraph"
        #         and token.get("children")
        #         # and len(token["children"]) == 1
        #         # and token["children"][0]["type"] == "text"
        # ):
        #     series_of_children = token["children"]
        #     most_recent_key = handle_series_of_children(config, most_recent_key, outermost_dict, series_of_children)
        #     current_key = None
        elif token["type"] == "block_code":
            # Treat block code as just more text, no "styling"
            continuation_value: str = token["text"]
            scalar = extract_scalar(continuation_value, config)
            # continuation of text
            if return_value:
                return_value += "\n\n" + scalar
            else:
                return_value = scalar
        elif token["type"] == "heading":
            # handled elsewhere?
            pass
        # else:
        #     raise NotImplementedError(token["type"])
    return return_value


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

    dict_wrapper = False
    # handle ATX-dict-like headers
    has_headers = any(True if item["type"] == "heading" else False for item in result)
    if has_headers:
        minimum = min(item["level"] if item["type"] == "heading" else 100000000 for item in result)
        outermost_dict = parse_outermost_dict(result, minimum)
        outermost_dict = walk_dict(outermost_dict, config)
    else:
        dict_wrapper = True
        outermost_dict = {None: process_list_of_tokens(result, config)}

    # if possible_dict and possible_dict.get("python_type"):
    #     python_type = possible_dict.get("python_type")
    #     if constructor := globals().get(python_type):
    #         if hasattr(constructor, "__getstate__"):
    #             possible_dict = constructor.__setstate__(possible_dict)
    #         else:
    #             constructor(**possible_dict)

    # really? do I misunderstand this?
    if object_hook:
        return object_hook(outermost_dict)

    if dict_wrapper:
        # Not ATX
        return outermost_dict.get(None)
    return outermost_dict


def walk_dict(outermost_dict: dict[str, Any], config: Config):
    """Process all lists of tokens found anywhere in this dictionary"""
    if isinstance(outermost_dict, dict):
        for current_key, list_or_dict_of_tokens in outermost_dict.items():
            if isinstance(list_or_dict_of_tokens, list):
                outermost_dict[current_key] = process_list_of_tokens(list_or_dict_of_tokens, config)
            elif isinstance(list_or_dict_of_tokens, dict):
                outermost_dict[current_key] = walk_dict(list_or_dict_of_tokens, config)
            else:
                raise NotImplementedError("Expected list or dict")
    return outermost_dict


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

    return most_recent_key
