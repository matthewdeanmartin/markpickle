# Configuration

All serialization and deserialization options are controlled through the `Config` dataclass. Pass a config to `dumps`, `loads`, `dump`, or `load`.

```python
from markpickle import Config

config = Config()
config.infer_scalar_types = False
result = markpickle.loads("42", config=config)  # "42" (string, not int)
```

## Type Inference

### `infer_scalar_types: bool = True`

When `True`, markpickle attempts to convert strings to richer Python types during deserialization: integers, floats, booleans, None, and dates. When `False`, everything comes back as a string.

```python
config = Config(infer_scalar_types=True)
markpickle.loads("42", config=config)          # 42 (int)
markpickle.loads("True", config=config)        # True (bool)
markpickle.loads("2024-01-15", config=config)  # datetime.date(2024, 1, 15)

config = Config(infer_scalar_types=False)
markpickle.loads("42", config=config)          # "42" (str)
markpickle.loads("True", config=config)        # "True" (str)
markpickle.loads("2024-01-15", config=config)  # "2024-01-15" (str)
```

### `true_values: list[str] = ["True", "true"]`

Strings recognized as boolean `True` during deserialization.

### `false_values: list[str] = ["False", "false"]`

Strings recognized as boolean `False` during deserialization.

### `none_values: list[str] = ["None", "nil", "nil"]`

Strings recognized as `None` during deserialization. Used alongside `none_string`.

### `none_string: str = "None"`

The string written when serializing `None`, and also recognized as `None` during deserialization.

### `infer_complex_types: bool = False`

When `True`, detect complex number patterns (e.g. `(3+4j)`) during deserialization.

```python
config = Config(infer_complex_types=True)
markpickle.loads("(3+4j)", config=config)  # (3+4j)
```

### `infer_decimal_types: bool = False`

When `True`, parse numeric strings as `decimal.Decimal` instead of `float`. Mutually exclusive with float inference.

```python
config = Config(infer_decimal_types=True)
markpickle.loads("3.14", config=config)  # Decimal('3.14')
```

### `infer_uuid_types: bool = False`

When `True`, detect UUID patterns (8-4-4-4-12 hex) during deserialization.

```python
config = Config(infer_uuid_types=True)
markpickle.loads("550e8400-e29b-41d4-a716-446655440000", config=config)
# uuid.UUID('550e8400-e29b-41d4-a716-446655440000')
```

## Serialization Options

### `serialize_headers_are_dict_keys: bool = True`

When `True`, top-level dict keys become ATX headers (`# key`). When `False`, keys use bullet-style (`- key : value`).

```python
config = Config(serialize_headers_are_dict_keys=False)
markpickle.dumps({"a": "1", "b": "2"}, config=config)
# "- a : 1\n- b : 2\n"
```

### `serialize_child_dict_as_table: bool = True`

When `True`, flat child dictionaries (all scalar values) become Markdown tables. Non-flat child dicts always use ATX header recursion regardless of this setting.

```python
config = Config(serialize_child_dict_as_table=True)
markpickle.dumps({"cat": {"name": "Ringo", "age": 5}}, config=config)
# # cat
#
# | name  | age |
# | ----- | --- |
# | Ringo | 5   |

config = Config(serialize_child_dict_as_table=False)
markpickle.dumps({"cat": {"name": "Ringo", "age": 5}}, config=config)
# # cat
#
# ## name
#
# Ringo
#
# ## age
#
# 5
```

### `serialize_tables_tabulate_style: bool = False`

When `True`, use the `tabulate` library for table rendering instead of the built-in renderer.

### `serialize_force_final_newline: bool = False`

When `True`, ensure all serialized output ends with a newline.

### `serialize_date_format: str = "%Y-%m-%d"`

strftime format string for `datetime.date` serialization.

### `serialized_datetime_format: str = "%Y-%m-%d %H:%M:%S"`

strftime format string for `datetime.datetime` serialization.

### `list_bullet_style: str = "-"`

The bullet character for unordered lists. Common values: `-`, `*`, `+`.

### `serialize_tuples_as_ordered_lists: bool = True`

When `True`, tuples serialize as ordered (numbered) lists.

```python
markpickle.dumps((1, 2, 3))
# 1. 1
# 2. 2
# 3. 3
```

### `serialize_bytes_mime_type: str = "image/png"`

MIME type used when serializing bytes as base64 data URLs.

### `serialize_include_python_type: bool = False`

When `True` and serializing an object with `__getstate__`, include a `python_type` key in the output dict.

## Deserialization Options

### `tables_become_list_of_lists: bool = False`

When `True`, Markdown tables deserialize as `list[list[str]]`. When `False` (default), tables become `list[dict[str, str]]`.

### `ordered_list_as_tuple: bool = True`

When `True`, ordered Markdown lists (`1. item`) deserialize as tuples. When `False`, they become regular lists.

### `empty_string_is: str = ""`

What to return when deserializing an empty document. Default is empty string.

### `deserialized_add_missing_key: bool = True`

When `True`, if a document has ATX headers but no initial header, a synthetic `Missing Key` header is added.

### `deserialized_missing_key_name: str = "Missing Key"`

The key name used when `deserialized_add_missing_key` inserts a synthetic header.

### `preserve_formatting_as_unicode: bool = False`

When `True`, inline markdown formatting (`**bold**`, `*italic*`, `` `code` ``) is converted to Unicode Mathematical Alphanumeric Symbols instead of being stripped. This preserves formatting information in plain Python strings.

### `parse_yaml_frontmatter: bool = False`

When `True`, detect and parse YAML front matter (`---...---`) at the start of a document. The front matter is stripped before normal parsing; use `loads_with_frontmatter()` to access it.

## Default Callback

### `default: Optional[Callable[[object], str]] = None`

A fallback function called when an object can't be serialized by the built-in logic. The function receives the object and should return a string.

```python
config = Config()
config.default = str  # Fall back to str() for unknown types
markpickle.dumps(frozenset([1, 2, 3]), config=config)
# "frozenset({1, 2, 3})"
```
