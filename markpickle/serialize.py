"""
Serialize many python types to Markdown.
"""
import datetime
import io
import logging
from typing import Optional

import mdformat

import markpickle.python_to_tables as python_to_tables
from markpickle.config_class import Config, unsafe_falsy_type, unsafe_scalar_type
from markpickle.mypy_types import SerializableTypes


def dumps(value: SerializableTypes, config: Optional[Config] = None) -> str:
    """
    Serialize basic python types to string of markdown

    >>> dumps([1,2])
    '- 1\\n- 2\\n'
    """
    if unsafe_falsy_type(value):
        logging.warning("Unsafe falsy types, round tripping won't be possible")
    if unsafe_scalar_type(value):
        logging.warning("Unsafe non-string types, round tripping won't be possible")

    if not config:
        config = Config()
    builder = io.StringIO()
    dump(value, builder, config)
    builder.seek(0)
    result = builder.read()
    if config.serialize_run_formatter:
        result = mdformat.text(result)
    return result


def dump(
    value: SerializableTypes,
    stream: io.IOBase,
    config: Optional[Config] = None,
) -> None:
    """
    Serialize basic python types to markdown in a file-like object.

    >>> import io
    >>> stream = io.StringIO()
    >>> dump([1,2], stream=stream)
    >>> _ = stream.seek(0)
    >>> stream.read()
    '- 1\\n- 2\\n'
    """
    if not config:
        config = Config()
    # TODO: support formatting when stream can't go backwards- seek(0)
    builder = stream
    header_level = 1
    if isinstance(value, list):
        render_list(builder, value, config, indent=0, header_level=header_level)
    elif isinstance(value, dict):
        render_dict(builder, value, config, indent=0, header_level=header_level)
    elif isinstance(value, (str, int, float, bool)):
        builder.write(str(value))
    elif isinstance(value, (datetime.date,)):
        builder.write(value.strftime(config.serialize_date_format))
    elif isinstance(value, (datetime.datetime,)):
        builder.write(value.strftime(config.serialized_datetime_format))
    elif value is None:
        builder.write(config.none_string)
    else:
        raise NotImplementedError()


def render_dict(
    builder: io.IOBase, value: SerializableTypes, config: Config, indent: int = 0, header_level: int = 1
) -> int:
    """Convert python dictionary to markdown"""
    for key, item in value.items():
        if not isinstance(item, (list, dict, set)):
            # `- key : value` is not markdown
            if config.serialize_headers_are_dict_keys and indent == 0:
                # headers dict keys. Can't nest.
                builder.write(f"{header_level * '#'} {key}\n" f"{item}\n")
            else:
                builder.write(f"{indent * ' '}- {key} : {item}\n")
        elif isinstance(item, list):
            if item and isinstance(item[0], dict):
                if config.serialize_headers_are_dict_keys and indent == 0:
                    # headers dict keys. Can't nest.
                    header = f"{header_level * '#'} {key}\n"
                    builder.write(header)
                else:
                    header = f"{indent * ' '}- {key}\n"
                    builder.write(header)
                python_to_tables.list_of_dict_to_markdown(builder, item, indent)
            else:
                builder.write(f"{indent * ' '}- {key}\n")
                render_list(builder, item, config, indent + 1)
        elif isinstance(item, dict):
            if config.serialize_child_dict_as_table:
                table = python_to_tables.dict_to_markdown(item, include_header=True, indent=indent + 1)
                builder.write(table)
            else:
                render_dict(builder, item, config, indent + 1)
        else:
            raise NotImplementedError()
    return indent


def render_list(
    builder: io.IOBase, value: SerializableTypes, config: Config, indent: int = 0, header_level: int = 1
) -> int:
    """Convert python list to markdown"""
    # This list is a list of dictionaries and we want a big table.
    if value and isinstance(value[0], dict):
        python_to_tables.list_of_dict_to_markdown(builder, value, indent)
        return indent

    # The list is not of dictionaries or we don't want tables.
    for item in value:
        if not isinstance(item, (list, dict, set)):
            builder.write(f"{indent * ' '}- {item}\n")
        elif isinstance(item, list):
            if item and isinstance(item[0], dict):
                python_to_tables.list_of_dict_to_markdown(builder, item, indent)
            else:
                render_list(builder, item, config, indent + 1, header_level)
        elif isinstance(item, dict):
            # We don't want tables or we'd have handled it above.
            render_dict(builder, item, config, indent + 1, header_level)
        else:
            raise NotImplementedError()
    return indent
