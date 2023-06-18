"""
String -> Python

Strings made by markpickle should pass and create a variety of simple Python types.

Arbitrary strings might not pass or may pass but create values that still have unparsed markdown in them.
"""
import datetime
import io
import logging
import textwrap
import urllib.parse
from typing import Any, Generator, Optional, cast

import mistune

import markpickle.python_to_tables as python_to_tables
from markpickle.atx_as_dictionary import parse_outermost_dict, strip_formatting
from markpickle.binary_streams import extract_bytes
from markpickle.config_class import Config
from markpickle.mypy_types import (
    DictTypes,
    ListTypes,
    MistuneTokenList,
    PossibleDictTypes,
    ScalarTypes,
    SerializableTypes,
)


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


def process_list(list_ast: Any, config: Config) -> ListTypes:
    """Deserialize a markdown list in AST form"""
    current_list: ListTypes = []
    for token in list_ast["children"]:
        if token["type"] == "list_item":
            for child in token["children"]:
                if child["type"] in ("block_text", "paragraph"):
                    block_text = child
                    if block_text["children"][0]["type"] == "text":
                        # This fails if not all text!
                        current_value = strip_formatting(block_text, ",")
                        scalar = extract_scalar(current_value, config)
                        current_list.append(scalar)
                    elif block_text["children"][0]["type"] == "link":
                        # Doesn't handle title or text
                        url = urllib.parse.urlparse(block_text["children"][0]["link"])
                        # HACK: Turn off type checking
                        current_list.append(cast(Any, url))
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


def process_list_of_tokens(list_of_tokens: MistuneTokenList, config: Config) -> Optional[SerializableTypes]:
    """Process a list of tokens to lists and scalars and so on."""
    # Tokens that are not ATX-dict-like headers
    return_value: Optional[SerializableTypes] = None

    accumulate_a_tuple: list[SerializableTypes] = []
    for token in list_of_tokens:
        if token["type"] == "newline":
            # Whitespace, no impact on datatype
            continue

        if token["type"] == "list":
            # Dict value of type list
            if token["children"][0]["type"] == "text":
                list_contents_as_text = cast(Optional[ListTypes], strip_formatting(token, ","))
                accumulate_a_tuple.append(list_contents_as_text)
            elif token["children"][0]["type"] == "list_item":
                sublist = process_list(token, config)
                accumulate_a_tuple.append(sublist)
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
            if current_text_value.count("|") >= 2:
                return python_to_tables.parse_table_to_list_of_dict(current_text_value)

            some_scalar = extract_scalar(current_text_value, config)
            accumulate_a_tuple.append(some_scalar)

        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and all(_.get("type") in ("text", "codespan", "strong") for _ in token["children"])
        ):
            # E.g. "Cat *and* Dog", which is 3 child tokens because of formatting
            current_value: str = strip_formatting(token)
            scalar = extract_scalar(current_value, config)
            accumulate_a_tuple.append(scalar)
        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and len(token["children"]) == 1
            and token["children"][0]["type"] == "text"
        ):
            # Handle images
            if token["children"][0]["type"] == "image":
                scalar = extract_bytes(token["children"][0]["src"], config)
            else:
                raise NotImplementedError()
            accumulate_a_tuple.append(scalar)
        elif token["type"] == "block_code":
            # See markmodule for treating block_code as code. Can't easily do it here.
            # Treat block code as just more text, no "styling"
            continuation_value: str = token["text"]
            scalar = extract_scalar(continuation_value, config)
            # continuation of text
            if return_value:
                # mypy isn't sure if scalar is always a string.
                accumulate_a_tuple.append(str(return_value) + "\n\n" + str(scalar))
            else:
                accumulate_a_tuple.append(scalar)
        elif token["type"] == "heading":
            # handled elsewhere?
            raise TypeError("Unconsumed header... shouldn't be in AST by this point.")
        elif token["type"] == "def_list":
            list_header = None
            list_item = None
            for item in token["children"]:
                if item["type"] == "def_list_header" and list_header is None:
                    list_header = cast(str, item["text"])
                elif item["type"] == "def_list_item" and list_item is None:
                    list_item = cast(str, item["text"])
                else:
                    raise TypeError("Expected only list header/list item in definition list")
            # TODO: Support full dictionary
            if list_header and list_item:
                accumulate_a_tuple.append({list_header: list_item})
            else:
                raise TypeError("Malformed definition-as-dictionary")
        else:
            # This is probably mixed content.
            # e.g. a paragraph + list + something + something
            raise NotImplementedError(
                f"Probably mixed content (tuple) where a single scalar/list/dict was expected. {token['type']}"
            )
    if len(accumulate_a_tuple) == 0:
        # Found nothing.
        return None
    if len(accumulate_a_tuple) == 1:
        # Found only 1 thing.
        return accumulate_a_tuple[0]

    # This probably means that the markdown is more of a DOM than a data structure.
    # Found a mixture of things. I guess those are tuples.
    return cast(SerializableTypes, tuple(accumulate_a_tuple))


def missing_top_key(result: MistuneTokenList):
    """The ATX-header root dictionary will discard the top part of the document without an starting key,
    e.g. a h1/# token"""
    found: list[dict[str, Any]] = []
    for token in result:
        if token["type"] == "newline":
            continue
        if token["type"] == "paragraph" and token.get("children"):
            possible_whitespace = strip_formatting(token)
            if possible_whitespace.strip() == "":
                continue
        if token["type"] == "heading" and not found:
            return False
        found.append(token)
    return True


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

    # Enable def_list by default for another dictionary format.
    parser = mistune.create_markdown(renderer="ast", plugins=["def_list"])
    result = parser.parse(string_value)

    # Process a list
    if len(result) == 1 and result[0]["type"] == "list":
        return process_list(result[0], config)

    dict_wrapper = False
    # handle ATX-dict-like headers
    has_headers = any(item["type"] == "heading" for item in result)

    if has_headers:
        # handle people skipping to ## or ###
        minimum = min(item["level"] if item["type"] == "heading" else 100000000 for item in result)
        if missing_top_key(result) and config.deserialized_add_missing_key:
            result = parser.parse("#" * minimum + f" {config.deserialized_missing_key_name}\n\n" + string_value)
        outermost_dict = parse_outermost_dict(result, minimum)
        outermost_dict = walk_dict(cast(PossibleDictTypes, outermost_dict), config)
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
        # mypy can't tell what is going on with dict_wrapper
        return cast(SerializableTypes, outermost_dict.get(None))
    # mypy can't tell what is going on with dict_wrapper
    return cast(SerializableTypes, outermost_dict)


def walk_dict(outermost_dict: PossibleDictTypes, config: Config):
    """Process all lists of tokens found anywhere in this dictionary"""
    if isinstance(outermost_dict, dict):
        for current_key, list_or_dict_of_tokens in outermost_dict.items():
            if isinstance(list_or_dict_of_tokens, list):
                outermost_dict[current_key] = process_list_of_tokens(
                    cast(MistuneTokenList, list_or_dict_of_tokens), config
                )
            elif isinstance(list_or_dict_of_tokens, dict):
                outermost_dict[current_key] = walk_dict(cast(PossibleDictTypes, list_or_dict_of_tokens), config)
            else:
                raise NotImplementedError("Expected list or dict")
    return outermost_dict


def handle_series_of_children(config: Config, most_recent_key: str, possible_dict: DictTypes, series_of_children):
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
        # HACK: str() to make mypy happy.
        possible_dict[most_recent_key] = str(possible_dict[most_recent_key]) + "\n\n" + str(scalar)

    return most_recent_key
