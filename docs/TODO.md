# TODO

## Features

- json to markdown utility function
- support multiple 3rd party table makers
- support  `__getstate__()`
  - Easy! Just check if well behaved python type would rather serialize a proxy.
- and `__setstate__()`
  - Difficult! Most likely custom types implemente `__setstate__()`
  - Don't have meta data extensions.

## Bugs

- dictionary of dictionaries loses key of outer dictionary
- date format fails on certain dates
- 2nd paragraph in a series of paragraphs blows up instead of showing up as simple text.
- Need some sort of fallback behavior for styled text (code block/quote/bold/italic)

## Build

- devcontainer
- github actions script
- get hypothesis slow/flaky to pass
- get passing mypyc for some modules?

## Config ideas from ChatGPT

- `newline_character: str = "\n"`
  Specifies the newline character to use in the serialized markdown (e.g., "\\n", "\\r\\n").

- -`indentation_spaces: int = 2`
  Specifies the number of spaces to use for indentation in nested structures (e.g., lists within lists or nested dicts).

- `quote_string_values: bool = False`
  If true, quote string values in the serialized markdown. Useful to distinguish strings from other scalar types.

- `escape_special_characters: bool = True`
  If true, escape special characters like "\*", "\_", and "\`" in the serialized markdown to avoid unintentional formatting.

- `deserialize_custom_types: Dict[str, Callable] = dataclasses.field(default_factory=dict)`
  A dictionary mapping custom type identifiers to deserialization callables. This allows users to extend the deserialization to custom types.

- `serialize_custom_types: Dict[Type, Callable] = dataclasses.field(default_factory=dict)`
  A dictionary mapping custom types to serialization callables. This allows users to extend the serialization to custom types.

- `key_value_separator: str = ": "`
  Specifies the separator to use between keys and values in serialized dictionaries (e.g., ": ", " = ", " -> ").

- `error_handling: str = "strict"`
  Specifies how to handle errors during serialization/deserialization (e.g., "strict", "ignore", "replace"). In "strict" mode, errors raise exceptions; in "ignore" mode, errors are silently ignored; in "replace" mode, errors are replaced with a specified replacement value.

- `error_replacement_value: Optional[SerializableTypes] = None`
  Specifies the value to use as a replacement when error_handling is set to "replace".

## Data format to support

```python
{
    'data': {
        'Name': ['Alice', 'Bob', 'Carol'],
        'Age': [30, 25, 35],
        'City': ['New York', 'San Francisco', 'Los Angeles'],
    }
}
```

```markdown
| Name  | Age | City         |
| ----- | --- | ------------ |
| Alice | 30  | New York     |
| Bob   | 25  | San Francisco|
| Carol | 35  | Los Angeles  |
```

## Deserialing real world english

- deerialize bold/italic to f string-like thing (possible? not possible?)
- treat code block as eval
- treat 2nd unexpected data structure as generator stream? (essentially another variation on handing `---`
