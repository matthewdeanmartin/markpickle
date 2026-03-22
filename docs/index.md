# markpickle

Lossy serialization of Python types to Markdown and back.

markpickle treats Markdown as a data serialization format. Markdown headers become dictionary keys, lists become Python lists, and tables represent lists of dictionaries. It creates predictable Markdown from Python objects and can parse structured Markdown back into Python types.

## Quick Example

```python
import markpickle

# Python dict -> Markdown
md = markpickle.dumps({"name": "Alice", "age": 30})
print(md)
# # name
#
# Alice
#
# # age
#
# 30

# Markdown -> Python dict
data = markpickle.loads("# name\n\nAlice\n\n# age\n\n30\n")
print(data)
# {'name': 'Alice', 'age': 30}
```

## What's New in 2.0.0

- Fixed datetime serialization (time component no longer lost)
- Fixed negative integer deserialization (no longer becomes float)
- Fixed 3-level nested dict support (no longer crashes)
- Smarter table heuristics (non-flat dicts use ATX headers instead of broken tables)
- Tuples serialize as ordered lists (`1. item`)
- YAML front matter support
- Unicode text formatting (bold/italic/monospace preserved as Unicode math symbols)
- New scalar types: `complex`, `Decimal`, `UUID`

## Installation

```shell
pip install markpickle
```

## Documentation

- [Getting Started](getting_started.md) - Installation and basic usage
- [Examples](examples.md) - All supported type conversions with code
- [Configuration](configuration.md) - Every config option explained
- [Things That Will Not Work](limitations.md) - Known limitations and edge cases
- [Choosing a Library](choosing_a_library.md) - When to use markpickle vs alternatives
