# Examples

## Scalars

### Strings

```python
markpickle.dumps("hello world")  # "hello world"
markpickle.loads("hello world")  # "hello world"
```

### Integers

```python
markpickle.dumps(42)    # "42"
markpickle.dumps(-7)    # "-7"
markpickle.loads("42")  # 42
markpickle.loads("-7")  # -7
```

### Floats

```python
markpickle.dumps(3.14)    # "3.14"
markpickle.loads("3.14")  # 3.14
markpickle.loads("-2.5")  # -2.5
```

### Booleans

```python
markpickle.dumps(True)     # "True"
markpickle.dumps(False)    # "False"
markpickle.loads("True")   # True
markpickle.loads("false")  # False  (case-insensitive by default)
```

### None

```python
markpickle.dumps(None)     # ""
markpickle.loads("None")   # None
markpickle.loads("nil")    # None  (in default none_values)
```

### Dates

```python
import datetime

markpickle.dumps(datetime.date(2024, 1, 15))  # "2024-01-15"
markpickle.loads("2024-01-15")                 # datetime.date(2024, 1, 15)
```

### Datetimes

```python
import datetime

markpickle.dumps(datetime.datetime(2024, 1, 15, 10, 30, 45))
# "2024-01-15 10:30:45"
```

### Bytes (as base64 data URLs)

```python
markpickle.dumps(b"hello bytes")
# "![bytes](data:image/png;base64,aGVsbG8gYnl0ZXM=)"
```

### Complex Numbers (opt-in)

```python
from markpickle import Config

config = Config(infer_complex_types=True)
markpickle.dumps(3+4j)                      # "(3+4j)"
markpickle.loads("(3+4j)", config=config)   # (3+4j)
```

### Decimal (opt-in)

```python
from decimal import Decimal
from markpickle import Config

config = Config(infer_decimal_types=True)
markpickle.dumps(Decimal("123.456"))                # "123.456"
markpickle.loads("123.456", config=config)           # Decimal('123.456')
```

### UUID (opt-in)

```python
import uuid
from markpickle import Config

config = Config(infer_uuid_types=True)
u = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
markpickle.dumps(u)
# "550e8400-e29b-41d4-a716-446655440000"

markpickle.loads("550e8400-e29b-41d4-a716-446655440000", config=config)
# uuid.UUID('550e8400-e29b-41d4-a716-446655440000')
```

## Lists

### Flat List

```python
markpickle.dumps([1, 2, 3])
# - 1
# - 2
# - 3

markpickle.loads("- a\n- b\n- c\n")  # ["a", "b", "c"]
```

### Nested Lists

```python
markpickle.dumps([1, 2, ["a", "b"]])
# - 1
# - 2
#   - a
#   - b
```

### List of Dictionaries (becomes a table)

```python
data = [{"animal": "cat", "name": "Frisky"}, {"animal": "dog", "name": "Fido"}]
markpickle.dumps(data)
# | animal | name   |
# | ------ | ------ |
# | cat    | Frisky |
# | dog    | Fido   |
```

## Tuples (as ordered lists)

Tuples serialize as numbered markdown lists and ordered lists deserialize as tuples.

```python
markpickle.dumps((1, 2, 3))
# 1. 1
# 2. 2
# 3. 3

markpickle.loads("1. Alice\n2. Bob\n3. Carol\n")
# ("Alice", "Bob", "Carol")
```

Disable with `Config(serialize_tuples_as_ordered_lists=False, ordered_list_as_tuple=False)`.

## Dictionaries

### Flat Dict (ATX headers)

```python
markpickle.dumps({"name": "Alice", "city": "NYC"})
# # name
#
# Alice
#
# # city
#
# NYC
```

### Nested Dict (deeper ATX headers)

```python
markpickle.dumps({"person": {"name": "Alice", "age": 30}})
# # person
#
# | name  | age |
# | ----- | --- |
# | Alice | 30  |
```

With `serialize_child_dict_as_table=False`:

```python
config = Config(serialize_child_dict_as_table=False)
markpickle.dumps({"person": {"name": "Alice", "age": 30}}, config=config)
# # person
#
# ## name
#
# Alice
#
# ## age
#
# 30
```

### Deeply Nested Dicts (3+ levels)

```python
markpickle.loads("# a\n\n## b\n\n### c\n\ndeep\n")
# {"a": {"b": {"c": "deep"}}}
```

### Dict with Non-Flat Values (smart table heuristic)

When a child dict contains nested dicts or lists, markpickle automatically uses ATX header nesting instead of tables:

```python
data = {"config": {"db": {"host": "localhost", "port": 5432}}}
markpickle.dumps(data)
# # config
#
# ## db
#
# | host      | port |
# | --------- | ---- |
# | localhost | 5432  |
```

## Tables

### List of Dicts as Table

```python
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
markpickle.dumps(data)
# | name  | age |
# | ----- | --- |
# | Alice | 30  |
# | Bob   | 25  |
```

### Table as List of Lists

```python
config = Config(tables_become_list_of_lists=True)
md = """| name  | age |
| ----- | --- |
| Alice | 30  |"""
markpickle.loads(md, config=config)
# [["name", "age"], ["Alice", "30"]]
```

### Table as List of Dicts (default)

```python
md = """| name  | age |
| ----- | --- |
| Alice | 30  |"""
markpickle.loads(md)
# [{"name": "Alice", "age": "30"}]
```

## YAML Front Matter

### Reading Front Matter

```python
md = """---
title: My Document
date: 2024-01-15
tags: [python, markdown]
---

# name

Alice

# age

30
"""

frontmatter, body = markpickle.loads_with_frontmatter(md)
# frontmatter = {"title": "My Document", "date": "2024-01-15", "tags": ["python", "markdown"]}
# body = {"name": "Alice", "age": 30}
```

### Writing Front Matter

```python
body = {"name": "Alice", "age": 30}
frontmatter = {"title": "Person Record", "version": 2}

md = markpickle.dumps_with_frontmatter(body, frontmatter)
# ---
# title: Person Record
# version: 2
# ---
#
# # name
#
# Alice
#
# # age
#
# 30
```

## Unicode Text Formatting

Preserve markdown bold/italic/monospace through round-tripping using Unicode Mathematical Alphanumeric Symbols.

### Direct Usage

```python
from markpickle.unicode_text import to_bold, to_italic, to_monospace

to_bold("hello")      # bold Unicode characters
to_italic("hello")    # italic Unicode characters
to_monospace("hello")  # monospace Unicode characters
```

### Round-Trip Preservation

```python
from markpickle.unicode_text import markdown_inline_to_unicode, unicode_to_markdown

# Markdown -> Unicode (preserves formatting in plain strings)
markdown_inline_to_unicode("**hello** *world* `code`")
# Returns string with Unicode bold "hello", italic "world", monospace "code"

# Unicode -> Markdown (restore formatting)
unicode_to_markdown(formatted_string)
# "**hello** *world* `code`"
```

Enable during deserialization with `Config(preserve_formatting_as_unicode=True)`.

## Classes and Dataclasses

### Dataclass Serialization

```python
from dataclasses import dataclass
import markpickle

@dataclass
class Person:
    name: str
    age: int

markpickle.dumps(Person(name="Alice", age=30))
# # name
#
# Alice
#
# # age
#
# 30
```

### Objects with `__getstate__`

```python
class Pet:
    def __init__(self, name, species):
        self.name = name
        self.species = species

    def __getstate__(self):
        return {"name": self.name, "species": self.species}

markpickle.dumps(Pet("Ringo", "cat"))
# # name
#
# Ringo
#
# # species
#
# cat
```

### Objects with `__dict__`

Any object with a `__dict__` attribute can be serialized:

```python
class Config:
    def __init__(self):
        self.debug = True
        self.version = "1.0"

markpickle.dumps(Config())
# # debug
#
# True
#
# # version
#
# 1.0
```

## Multiple Documents

### String API

```python
md = markpickle.dumps_all(["hello", [1, 2], {"key": "val"}])
# hello
#
# ---
#
# - 1
# - 2
#
# ---
#
# # key
#
# val
```

### Stream API

```python
import io

# Write
s = io.StringIO()
markpickle.dump_all(["doc1", "doc2"], s)

# Read
s.seek(0)
docs = list(markpickle.load_all(s))
# ["doc1", "doc2"]
```

### File Splitting

For files with `---` or `***` or `___` separators:

```python
with open("multi.md", "rb") as f:
    for section in markpickle.split_file(f):
        data = markpickle.loads(section)
        print(data)
```

## JSON Conversion Helpers

```python
# JSON string -> Markdown string
markpickle.convert_json_to_markdown('{"name": "Alice"}')
# "# name\n\nAlice\n"

# Markdown string -> JSON string
markpickle.convert_markdown_to_json("# name\n\nAlice\n")
# '{"name": "Alice"}'
```
