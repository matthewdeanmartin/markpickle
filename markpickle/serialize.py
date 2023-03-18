"""
Serialize many python types to Markdown.
"""
import dataclasses
import io
from typing import Optional, Union

import mdformat

import markpickle.python_to_tables as python_to_tables
from markpickle.mypy_types import SerializableTypes


@dataclasses.dataclass
class SerializationConfig:
    headers_are_dict_keys: bool = True
    dict_as_table: bool = False
    child_dict_as_table: bool = True
    none_is: str = "None"
    run_formatter: bool = False


def dumps(value: SerializableTypes, root: Optional[str] = None, config: Optional[SerializationConfig] = None) -> str:
    """
    Serialize basic python types to string of markdown

    >>> dumps([1,2])
    '- 1\\n- 2\\n'
    """
    if not config:
        config = SerializationConfig()
    builder = io.StringIO()
    dump(value, builder, root, config)
    builder.seek(0)
    result = builder.read()
    if config.run_formatter:
        result = mdformat.text(result)
    return result


def dump(
    value: SerializableTypes,
    stream: io.IOBase,
    root: Optional[str] = None,
    config: Optional[SerializationConfig] = None,
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
        config = SerializationConfig()
    # TODO: support formatting when stream can't go backwards- seek(0)
    builder = stream
    header_level = 1
    if root:
        builder.write(f"# {root}\n")
        header_level += 1
    if isinstance(value, list):
        render_list(builder, value, config, indent=0, header_level=header_level)
    elif isinstance(value, dict):
        render_dict(builder, value, config, indent=0, header_level=header_level)
    elif isinstance(value, (str, int, float, bool)):
        builder.write(str(value))
    elif value is None:
        builder.write(config.none_is)
    else:
        raise NotImplementedError()


def render_dict(
    builder: io.IOBase, value: SerializableTypes, config: SerializationConfig, indent: int = 0, header_level: int = 1
) -> int:
    """Convert python dictionary to markdown"""
    for key, item in value.items():
        if not isinstance(item, (list, dict, set)):
            # `- key : value` is not markdown
            if config.headers_are_dict_keys and indent == 0:
                # headers dict keys. Can't nest.
                builder.write(f"{header_level * '#'} {key}\n" f"{item}\n")
            else:
                builder.write(f"{indent * ' '}- {key} : {item}\n")
        elif isinstance(item, list):
            if item and isinstance(item[0], dict):
                if config.headers_are_dict_keys and indent == 0:
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
            if config.child_dict_as_table:
                table = python_to_tables.dict_to_markdown(item, include_header=True, indent=indent + 1)
                builder.write(table)
            else:
                render_dict(builder, item, config, indent + 1)
        else:
            raise NotImplementedError()
    return indent


def render_list(
    builder: io.IOBase, value: SerializableTypes, config: SerializationConfig, indent: int = 0, header_level: int = 1
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
