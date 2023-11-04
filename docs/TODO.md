# TODO

## Bugs

- [ ] Doesn't deserialize python nexted dict to ATX headers, except 1st level
- [ ] loads_all is just broken
- [ ] test_dodgy failing (whitespace handling?)
- [ ] nested lists failing again
- [ ] Treat more mixed content as tuple?
- [ ] strict mode to reject mixed content? (areas where no data expected or only 1 value)
- [ ] treat multiple paragraphs with strong/bold/etc as one big string & strip formatting
- [ ] Doesn't handle when a scalar/list/etc is wrapped in bold 

## Features

- [ ] support  `__getstate__()`
  - [ ] Easy! Just check if well behaved python type would rather serialize a proxy.
- [ ] and `__setstate__()`
  - [ ] Difficult! Most likely custom types implemente `__setstate__()`
  - [ ] Don't have meta data extensions.
- [ ] schema? Markdown schema?

## Yaml-like metadata header 

Metadata for deserializing to something other that dict/list/scalar
- [ ] anti-tamper signature in header?

## use code block to put source code of class so you can deserialize to that at target.


```python
class Foobar():
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

```markdown
# x
123
# y
456
```

Would deserialize back to a Foobar

- Using serialization format as a database format, e.g. Shelve - key value store for serialized things? A persistent dictionary.

Dict-Key-Is-Tag-Name
- investigate json to markdown using mapping (key to md tag) e.g. https://github.com/snjyor/jsonvalue2markdown

Special Types- Links, Images
- using urlparse/yarl/furl serialize object representing url to a textual url. maybe doing same for links.

## Mixed Paragraphs as tuples/ Mixed Paragraphs as long string.
- e.g. para - list - para == tuple[str, list,  str]

## Strip Markdown/Preserve bold & italic as terminal codes
- Need some sort of fallback behavior for styled text (code block/quote/bold/italic)

## Build
- get hypothesis slow/flaky to pass
- get passing mypyc for some modules

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

## Deserializing real world english

- [ ] deserialize bold/italic to f string-like thing (possible? not possible?)