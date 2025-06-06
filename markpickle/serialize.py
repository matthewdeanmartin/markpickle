"""
serialize.py

This module provides functions to serialize many Python types to Markdown.
"""

import datetime
import io
import logging
import textwrap
from typing import Any, Callable, Optional, TextIO, Union, cast

from markpickle import python_to_tables, simplify_types, third_party_tables
from markpickle.binary_streams import bytes_to_markdown
from markpickle.config_class import Config
from markpickle.mypy_types import DictTypes, SerializableTypes


def dumps_all(
    value: list[SerializableTypes],
    config: Optional[Config] = None,
    default: Optional[Callable[[object], str]] = None,
) -> str:
    """Iterate value and serialize documents with horizontal lines between documents"""
    if default and config:
        config.default = default
    if default and not config:
        config = Config()
        config.default = default

    builder = io.StringIO()
    for docs, document in enumerate(value):
        if docs > 0:
            builder.write("\n---\n\n")
        builder.write(dumps(document, config, default))

    builder.seek(0)
    return builder.read()


def dumps(
    value: SerializableTypes,
    config: Optional[Config] = None,
    default: Optional[Callable[[object], str]] = None,
) -> str:
    """
    Serialize basic Python types to a string of Markdown.

    Args:
        value: The value to be serialized.
        default: A function to handle otherwise unserializable types.
        config: Optional configuration object.

    Returns:
        A string containing the serialized Markdown.

    >>> dumps([1,2])
    '- 1\\n- 2\\n'
    """
    if default and config:
        config.default = default
    if default and not config:
        config = Config()
        config.default = default

    if unsafe_falsy_type(value):
        logging.warning("Unsafe falsy types, round tripping won't be possible")
    if unsafe_scalar_type(value):
        logging.warning("Unsafe non-string types, round tripping won't be possible")

    if not config:
        config = Config()
    builder = io.StringIO()
    dump(value, builder, config=config, default=default)

    builder.seek(0)
    result = builder.read()

    # results in a copy! ugh!
    if config.serialize_force_final_newline and not result.endswith("\n"):
        # add missing single final new line
        result += "\n"
    while result.endswith("\n\n"):
        # remove extras down to one
        if result.endswith("\n"):
            result = result[0:-1]

    return result


def dump_all(
    value: list[SerializableTypes],
    stream: Union[io.IOBase, TextIO],
    config: Optional[Config] = None,
    default: Optional[Callable[[object], str]] = None,
) -> None:
    """Iterate value and serialize documents with horizontal lines between documents"""
    if default and config:
        config.default = default
    if default and not config:
        config = Config()
        config.default = default
    docs = 0
    for document in value:
        if docs > 0:
            stream.write("---\n\n")
        dump(document, stream, config, default)


def render_scalar(
    builder: Union[io.IOBase, TextIO],
    value: SerializableTypes,
    config: Config,
    _indent: int = 0,
    _header_level: int = 1,
) -> None:
    """Render a scalar value to Markdown"""
    if isinstance(value, (str, int, float, bool)):
        builder.write(str(value))
    elif isinstance(value, (datetime.date,)):
        try:
            builder.write(value.strftime(config.serialize_date_format))
        except UnicodeEncodeError:
            builder.write(str(config.serialize_date_format))
    elif isinstance(value, (datetime.datetime,)):
        try:
            builder.write(value.strftime(config.serialized_datetime_format))
        except UnicodeEncodeError:
            builder.write(str(config.serialize_date_format))
    elif value is None:
        builder.write(config.none_string)
    elif isinstance(value, bytes):
        builder.write(bytes_to_markdown(None, value, config))
    elif config.default:
        # fall back to user preferred, e.g. str()
        builder.write(config.default(value))
    else:
        raise NotImplementedError(f"Unknown scalar type: {type(value)}")


def dump(
    value: SerializableTypes,
    stream: Union[io.IOBase, TextIO],
    config: Optional[Config] = None,
    default: Optional[Callable[[object], str]] = None,
) -> None:
    """
    Serialize basic Python types to Markdown in a file-like object.

    Args:
        value: The value to be serialized.
        stream: The file-like object to write the serialized Markdown to.
        config: Optional configuration object.

    >>> import io
    >>> string_builder = io.StringIO()
    >>> dump([1,2], stream=string_builder)
    >>> _ = string_builder.seek(0)
    >>> string_builder.read()
    '- 1\\n- 2\\n'
    """
    if not config:
        config = Config()
    # TODO: support formatting when stream can't go backwards- seek(0)
    builder = stream
    header_level = 1

    outtermost_type = type(value).__qualname__

    # mypy doesn't use info from the hadattr check.
    if hasattr(value, "__getstate__") and cast(Any, value).__getstate__():
        value = cast(Any, value).__getstate__()
        if isinstance(value, dict) and config.serialize_include_python_type:
            value["python_type"] = outtermost_type

    if isinstance(value, list):
        render_list(builder, cast(list[SerializableTypes], value), config, indent=0, header_level=header_level)
    # elif isinstance(value, dict) and all(isinstance(_, dict) for _ in value.values()):
    #     for key, item in value.items():
    #         builder.write(f"{ '#' * header_level} {key}")
    #         render_dict(builder, item, config, indent=1, header_level=header_level)
    elif isinstance(value, dict):
        render_dict(builder, value, config, indent=0, header_level=header_level)
    elif isinstance(value, bool | datetime.date | datetime.datetime | float | int | str):
        render_scalar(builder, value, config)
    elif simplify_types.can_class_to_dict(value):
        candidate_dict = cast(Any, simplify_types.class_to_dict(value))
        render_dict(builder, candidate_dict, config, indent=0, header_level=header_level)
    elif default:
        attempt = default(value)
        builder.write(attempt)
    elif isinstance(value, (bytes,)):
        image_text = bytes_to_markdown("bytes", value, config)
        builder.write(image_text)
    elif value is None:
        builder.write("")
    else:
        raise NotImplementedError(f"Can't dump type of {type(value)} with value of {value}")


def python_to_atx_header(_builder: Union[io.IOBase, TextIO], _data: list[DictTypes], _header_level: int, _indent: int):
    """Write a nested dictionary as a series of ATX header sections"""
    print("Not implemented yet")


def render_dict(
    builder: Union[io.IOBase, TextIO], value: DictTypes, config: Config, indent: int = 0, header_level: int = 1
) -> int:
    """Convert a Python dictionary to Markdown.

    Args:
        builder: The file-like object to write the Markdown to.
        value: The dictionary to be converted.
        config: Configuration object.
        indent: The current indentation level.
        header_level: The current header level.

    Returns:
        The current indentation level.
    """
    if value is None:
        # Nothing to write.
        return indent

    for key, item in value.items():
        if not isinstance(item, (list, dict, set)):
            # `- key : value` is not markdown
            if config.serialize_headers_are_dict_keys and indent == 0:
                # headers dict keys. Can't nest.
                minibuilder = io.StringIO()
                render_scalar(minibuilder, item, config)
                seralialized_scalar = minibuilder.getvalue()
                builder.write(f"{header_level * '#'} {key}\n\n" f"{seralialized_scalar}\n\n")
            else:
                # This is ad hoc and not a markdown standard.
                minibuilder = io.StringIO()
                render_scalar(minibuilder, item, config)
                seralialized_scalar = minibuilder.getvalue()
                builder.write(f"{indent * '  '}{config.list_bullet_style} {key} : {seralialized_scalar}\n")
        elif isinstance(item, list):
            if item and isinstance(item[0], dict):
                if config.serialize_headers_are_dict_keys and indent == 0:
                    # headers dict keys. Can't nest.
                    header = f"{header_level * '#'} {key}\n"
                    builder.write(header)
                else:
                    # Some markdown parsers treat 1 space indents as 0!
                    header = f"{indent * '  '}{config.list_bullet_style} {key}\n"
                    builder.write(header)
                # assume if first is dict, they all are
                if config.serialize_child_dict_as_table:
                    python_to_tables.list_of_dict_to_markdown(builder, cast(list[DictTypes], item), indent)
                else:
                    python_to_atx_header(builder, cast(list[DictTypes], item), header_level, indent)
            else:
                # Some markdown parsers treat 1 space indents as 0!
                builder.write(f"{indent * '  '}{config.list_bullet_style} {key}\n")
                render_list(builder, cast(list[SerializableTypes], item), config, indent + 1)
        elif isinstance(item, dict):
            builder.write(f"{'#' * header_level} {key}\n\n")
            if config.serialize_child_dict_as_table:
                success = False
                if config.serialize_tables_tabulate_style:
                    # pylint: disable=broad-exception-caught
                    try:
                        table = third_party_tables.to_table_tablulate_style(item)
                        table = textwrap.indent(table, prefix=" " * (indent + 1))
                        builder.write(table)
                        success = True
                    except Exception:
                        success = False
                if not success:
                    # Try again
                    table = python_to_tables.dict_to_markdown(item, include_header=True, indent=indent + 1)
                    builder.write(table)
            else:
                render_dict(builder, item, config, indent + 1)
            builder.write("\n")
        elif config.serialize_child_dict_as_table:
            try:
                table = third_party_tables.to_table_tablulate_style(item)
                table = textwrap.indent(table, prefix=" " * (indent + 1))
                builder.write(table)
            except Exception as ex:
                logging.warning(f"Tabulate can't handle it either: {ex}")
                raise NotImplementedError() from ex
        else:
            raise NotImplementedError()

    return indent


def render_list(
    builder: Union[io.IOBase, TextIO],
    value: list[SerializableTypes],
    config: Config,
    indent: int = 0,
    header_level: int = 1,
) -> int:
    """
    Convert a Python list to Markdown.

    Args:
        builder: The file-like object to write the Markdown to.
        value: The list to be converted.
        config: Configuration object.
        indent: The current indentation level.
        header_level: The current header level.

    Returns:
        The current indentation level.
    """
    if not value:
        return indent
    # This list is a list of dictionaries and we want a big table.
    if value and all(isinstance(_, dict) for _ in value) and config.serialize_child_dict_as_table:
        python_to_tables.list_of_dict_to_markdown(builder, cast(list[DictTypes], value), indent)
        return indent

    # The list is not of dictionaries or we don't want tables.
    for item in value:
        if not isinstance(item, (list, dict, set)):
            minibuilder = io.StringIO()
            render_scalar(minibuilder, item, config)
            seralialized_scalar = minibuilder.getvalue()
            builder.write(f"{indent * '  '}{config.list_bullet_style} {seralialized_scalar}\n")
        elif isinstance(item, list):
            if item and isinstance(item[0], dict) and config.serialize_child_dict_as_table:
                # assuming if the first is dict, they all are dict.
                python_to_tables.list_of_dict_to_markdown(builder, cast(list[DictTypes], item), indent)
            elif item and isinstance(item[0], dict):
                raise NotImplementedError()
            else:
                render_list(builder, cast(list[SerializableTypes], item), config, indent + 1, header_level)
        elif isinstance(item, dict):
            # We don't want tables or we'd have handled it above.
            render_dict(builder, item, config, indent + 1, header_level)
        else:
            raise NotImplementedError()
    return indent


def unsafe_falsy_type(value: SerializableTypes) -> bool:
    """
    Warn the user that blank structures don't have an equivalent in Markdown.

    Args:
        value: The value to be checked.

    Returns:
        True if the value is a blank structure, otherwise False.
    """
    if value in ([], {}, (), "", "0", None):
        # falsies will not roundtrip.
        return True
    if isinstance(value, dict):
        if any(key in ([], {}, (), "", "0", None) for key in value):
            return True
        if any(dict_value in ([], {}, (), "", "0", None) for dict_value in value.values()):
            return True
    if isinstance(value, list):
        if any(list_value in ([], {}, (), "", "0", None) for list_value in value):
            return True
        for inner in value:
            if isinstance(inner, dict):
                if any(key in ([], {}, (), "", "0", None) for key in inner):
                    return True
                if any(dict_value in ([], {}, (), "", "0", None) for dict_value in inner.values()):
                    return True
    return False


def unsafe_scalar_type(value: SerializableTypes) -> bool:
    """
      Warn the user that non-string types won't round trip.

    Args:
        value: The value to be checked.

    Returns:
        True if the value is a non-string type that may not round trip, otherwise False.
    """
    if isinstance(
        value,
        (
            int,
            float,
            datetime.date,
        ),
    ):
        # we either get 0->"0" and then "0" is inferred to 0
        # and we also get "0"->"0" and then "0" is inferred to 0
        # or vica versa, for everything except strings.
        return True
    if isinstance(value, dict):
        if any(
            isinstance(
                key,
                (
                    int,
                    float,
                    datetime.date,
                ),
            )
            for key in value
        ):
            return True
        if any(
            isinstance(
                dict_value,
                (
                    int,
                    float,
                    datetime.date,
                ),
            )
            for dict_value in value.values()
        ):
            return True
    if isinstance(value, list) and any(  # noqa: SIM103
        isinstance(
            list_value,
            (
                int,
                float,
                datetime.date,
            ),
        )
        for list_value in value
    ):
        return True
    return False
