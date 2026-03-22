"""
String -> Python

Strings made by markpickle should pass and create a variety of simple Python types.

Arbitrary strings might not pass or may pass but create values that still have unparsed markdown in them.
"""

import datetime
import decimal
import io
import logging
import re
import textwrap
import urllib.parse
import uuid
from typing import Any, Generator, Optional, cast

import mistune

from markpickle import python_to_tables
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

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)
_COMPLEX_RE = re.compile(r"^\(?[+-]?(\d+\.?\d*|\d*\.?\d+)[+-](\d+\.?\d*|\d*\.?\d+)j\)?$")


def _is_int(value: str) -> bool:
    """Check if a string represents an integer, including negative numbers."""
    if not value:
        return False
    if value[0] in "+-":
        return value[1:].isdigit() if len(value) > 1 else False
    return value.isdigit()


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
    if not config.infer_scalar_types:
        # When inference is off, return everything as a string
        return value

    # Handle special cases for None, True, and False
    if value in config.none_values or value == config.none_string:
        return None
    if value in config.true_values:
        return True
    if value in config.false_values:
        return False

    # UUID detection (before numeric, since UUIDs contain hex digits)
    if config.infer_uuid_types and _UUID_RE.match(value):
        return cast(Any, uuid.UUID(value))

    # Complex number detection
    if config.infer_complex_types and _COMPLEX_RE.match(value):
        try:
            return cast(Any, complex(value))
        except ValueError:
            pass

    # Attempt to parse as int or float
    if _is_int(value):
        try:
            return int(value)
        except ValueError:
            pass
    if config.infer_decimal_types:
        if is_float(value) and not value.isalpha():
            try:
                return cast(Any, decimal.Decimal(value))
            except decimal.InvalidOperation:
                pass
    elif is_float(value):
        return float(value)

    # Attempt to parse as a date
    dashes_in_year_month = 2
    if value.count("-") == dashes_in_year_month:
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
                elif child["type"] == "block_code":
                    current_list.append(child["text"])
                else:
                    raise NotImplementedError(child["type"])
        else:
            raise NotImplementedError()
    return current_list


def _is_ordered_list(list_ast: Any) -> bool:
    """Check if an AST list node represents an ordered (numbered) list."""
    return list_ast.get("attrs", {}).get("ordered", False) or list_ast.get("ordered", False)


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
            # Check if it's an ordered list -> tuple
            if _is_ordered_list(token) and config.ordered_list_as_tuple:
                sublist = process_list(token, config)
                accumulate_a_tuple.append(tuple(sublist))
            elif token["children"][0]["type"] == "text":
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
            if current_text_value.count("|") >= 2:
                if config.tables_become_list_of_lists:
                    return python_to_tables.parse_table_to_lists(current_text_value)
                return python_to_tables.parse_table_to_list_of_dict(current_text_value)

            some_scalar = extract_scalar(current_text_value, config)
            accumulate_a_tuple.append(some_scalar)

        elif (
            token["type"] == "paragraph"
            and token.get("children")
            and all(_.get("type") in ("text", "codespan", "strong") for _ in token["children"])
        ):
            # E.g. "Cat *and* Dog", which is 3 child tokens because of formatting
            if config.preserve_formatting_as_unicode:
                from markpickle.unicode_text import markdown_inline_to_unicode
                current_value: str = _reconstruct_inline_markdown(token)
                current_value = markdown_inline_to_unicode(current_value)
            else:
                current_value = strip_formatting(token)
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
            # This used to crash with TypeError. Now we handle sub-headers
            # by treating them as a nested dict structure.
            remaining_tokens = list_of_tokens[list_of_tokens.index(token):]
            sub_dict = _process_sub_headers(remaining_tokens, config)
            if sub_dict:
                accumulate_a_tuple.append(cast(SerializableTypes, sub_dict))
            # We consumed all remaining tokens
            break
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
            pass
            # This is probably mixed content.
            # e.g. a paragraph + list + something + something
            # raise NotImplementedError(
            #     f"Probably mixed content (tuple) where a single scalar/list/dict was expected. {token['type']}"
            # )
    if len(accumulate_a_tuple) == 0:
        # Found nothing.
        return None
    if len(accumulate_a_tuple) == 1:
        # Found only 1 thing.
        return accumulate_a_tuple[0]

    # This probably means that the markdown is more of a DOM than a data structure.
    # Found a mixture of things. I guess those are tuples.
    return cast(SerializableTypes, tuple(accumulate_a_tuple))


def _reconstruct_inline_markdown(token: dict) -> str:
    """Reconstruct inline markdown from AST children (bold, italic, code)."""
    parts = []
    for child in token.get("children", []):
        if child["type"] == "text":
            parts.append(child.get("text", ""))
        elif child["type"] == "strong":
            inner = strip_formatting(child)
            parts.append(f"**{inner}**")
        elif child["type"] == "emphasis":
            inner = strip_formatting(child)
            parts.append(f"*{inner}*")
        elif child["type"] == "codespan":
            parts.append(f"`{child.get('text', '')}`")
        else:
            parts.append(strip_formatting(child))
    return "".join(parts)


def _process_sub_headers(tokens: MistuneTokenList, config: Config) -> Optional[dict]:
    """Process heading tokens found inside a value position (3+ level nesting)."""
    if not tokens:
        return None

    parser = mistune.create_markdown(renderer="ast", plugins=["def_list"])

    # Find the minimum heading level
    min_level = min(t["level"] for t in tokens if t["type"] == "heading")

    result: dict = {}
    current_key = None
    current_tokens: MistuneTokenList = []

    for token in tokens:
        if token["type"] == "newline":
            continue
        if token["type"] == "heading" and token["level"] == min_level:
            if current_key is not None:
                # Process accumulated tokens for previous key
                result[current_key] = process_list_of_tokens(current_tokens, config)
            current_key = strip_formatting(token)
            current_tokens = []
        else:
            current_tokens.append(token)

    # Process last key
    if current_key is not None:
        result[current_key] = process_list_of_tokens(current_tokens, config)

    return result if result else None


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


def _strip_yaml_frontmatter(text: str) -> tuple[Optional[dict], str]:
    """Extract YAML front matter from the beginning of a document.

    Returns (frontmatter_dict, remaining_body) or (None, original_text).
    """
    if not text.startswith("---"):
        return None, text

    lines = text.split("\n")
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, text

    frontmatter_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])

    # Simple YAML parser for key: value pairs
    fm_dict: dict[str, Any] = {}
    for line in frontmatter_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            # Simple type inference for front matter values
            if val.lower() in ("true", "yes"):
                fm_dict[key] = True
            elif val.lower() in ("false", "no"):
                fm_dict[key] = False
            elif val.startswith("[") and val.endswith("]"):
                # Simple list: [a, b, c]
                items = [item.strip().strip("'\"") for item in val[1:-1].split(",")]
                fm_dict[key] = items
            else:
                # Try numeric
                try:
                    fm_dict[key] = int(val)
                except ValueError:
                    try:
                        fm_dict[key] = float(val)
                    except ValueError:
                        fm_dict[key] = val

    return fm_dict, body


def loads_with_frontmatter(value: str, config: Optional[Config] = None) -> tuple[Optional[dict], SerializableTypes]:
    """Parse a markdown document with optional YAML front matter.

    Returns (frontmatter_dict, body_object). frontmatter_dict is None if no front matter found.
    """
    if not config:
        config = Config()
    frontmatter, body = _strip_yaml_frontmatter(value)
    body_obj = loads(body, config)
    return frontmatter, body_obj


def dumps_with_frontmatter(
    body: SerializableTypes,
    frontmatter: dict,
    config: Optional[Config] = None,
) -> str:
    """Serialize a Python object to markdown with YAML front matter."""
    from markpickle.serialize import dumps as _dumps

    if not config:
        config = Config()

    parts = ["---\n"]
    for key, val in frontmatter.items():
        if isinstance(val, list):
            parts.append(f"{key}: [{', '.join(str(v) for v in val)}]\n")
        elif isinstance(val, bool):
            parts.append(f"{key}: {'true' if val else 'false'}\n")
        else:
            parts.append(f"{key}: {val}\n")
    parts.append("---\n\n")

    body_md = _dumps(body, config)
    parts.append(body_md)

    return "".join(parts)


def load(value: io.StringIO, config: Optional[Config] = None, object_hook=None) -> SerializableTypes:
    """
    Convert certain markdown streams into simple Python types

    >>> import io
    >>> load(io.StringIO("- a\\n- b\\n - c\\n"))
    ['a', 'b', 'c']
    """
    if not config:
        config = Config()

    string_value = value.read()
    # TODO: maybe only do this if top level is block_code
    string_value = textwrap.dedent(string_value)

    # Handle YAML front matter if enabled
    frontmatter = None
    if config.parse_yaml_frontmatter:
        frontmatter, string_value = _strip_yaml_frontmatter(string_value)

    # Empty document
    if not string_value or not string_value.strip():
        # Exists to improve round-tripping for unit tests
        return cast(SerializableTypes, config.empty_string_is)

    # Enable def_list by default for another dictionary format.
    parser = mistune.create_markdown(renderer="ast", plugins=["def_list"])
    result = parser.parse(string_value)

    # Process a list
    if len(result) == 1 and result[0]["type"] == "list":
        if _is_ordered_list(result[0]) and config.ordered_list_as_tuple:
            return cast(SerializableTypes, tuple(process_list(result[0], config)))
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
            if list_or_dict_of_tokens is None:
                continue
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
