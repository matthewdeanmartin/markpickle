# How It Works

## Architecture

markpickle converts between Python objects and Markdown using a two-phase approach:

1. **Serialization** (`dumps`/`dump`): Walk the Python object tree and emit Markdown constructs
1. **Deserialization** (`loads`/`load`): Parse Markdown into an AST (via mistune), then walk the AST to reconstruct Python objects

## Markdown Constructs as Python Types

| Markdown Construct | Python Type | Direction |
| --- | --- | --- |
| Plain text | `str` | Both |
| Numeric text | `int`, `float` | Inferred on load |
| `True`/`False` | `bool` | Inferred on load |
| `None`/`nil` | `None` | Inferred on load |
| `YYYY-MM-DD` | `datetime.date` | Inferred on load |
| `- item` (unordered list) | `list` | Both |
| `1. item` (ordered list) | `tuple` | Both |
| `# Header` | dict key (level 1) | Both |
| `## Header` | nested dict key (level 2) | Both |
| `### Header` ... `###### Header` | deeper nesting (levels 3-6) | Both |
| `\| table \|` | `list[dict]` or `list[list]` | Both |
| `![alt](data:...)` | `bytes` | Both |
| `---` | document separator | Both |
| `**bold**`, `*italic*`, `` `code` `` | stripped (or Unicode symbols) | Load |
| `term\n: definition` | `dict` (single pair) | Load |

## Documents

Multiple Python objects can be stored in a single file, separated by horizontal rules (`---`). The `dumps_all`/`loads_all` functions handle this.

## Scalars

Scalars are the leaf values. During serialization, Python types are converted to their string representation. During deserialization, type inference attempts to recover the original type.

Type inference order: None -> bool -> int -> float -> date -> string (fallback).

When `infer_scalar_types=False`, no inference runs and everything stays as a string.

## Dictionaries

Dictionaries use ATX headers (`#`, `##`, `###`, etc.) as keys. Each header starts a new key, and everything until the next same-level header is the value.

```
# key1          ->  {"key1": "value1", "key2": "value2"}

value1

# key2

value2
```

Nested dicts use deeper header levels:

```
# outer         ->  {"outer": {"inner": "value"}}

## inner

value
```

## Tables

Flat dictionaries (all scalar values) nested inside another dict can be rendered as Markdown tables. This is controlled by `serialize_child_dict_as_table`.

The **table heuristic** (new in 2.0.0): only flat dicts (no nested dicts/lists/sets as values) become tables. Non-flat dicts always use ATX header recursion.

## Lists

Unordered lists use bullet markers (`-`, `*`, or `+`). Nested lists are indented.

Ordered lists (`1.`, `2.`, etc.) represent tuples.

## The AST

markpickle uses `mistune` in AST mode with the `def_list` plugin. The parser produces a token list that markpickle walks to build Python objects. The key token types handled:

- `heading` -> dict keys
- `list` -> Python lists (or tuples if ordered)
- `paragraph` -> scalar values
- `block_code` -> string values
- `def_list` -> single-pair dicts
- Images with data URLs -> bytes

## Front Matter

When `parse_yaml_frontmatter=True`, markpickle detects YAML front matter (a block between `---` delimiters at the start of the document). This is parsed with a simple built-in key-value parser (no pyyaml dependency) and stripped before normal processing.

## Unicode Text Formatting

The `unicode_text` module provides a way to preserve inline formatting (`**bold**`, `*italic*`, `` `code` ``) through round-tripping by converting to Unicode Mathematical Alphanumeric Symbols. These are real Unicode characters that render in most contexts but don't require any markup.
