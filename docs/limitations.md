# Things That Will Not Work

markpickle is a **lossy** serializer. Markdown lacks many concepts that Python has, so not everything round-trips cleanly. This page documents what won't work and why.

## Empty and Falsy Values

Empty collections and None all serialize to the same empty string:

```python
markpickle.dumps(None)   # ""
markpickle.dumps({})     # ""
markpickle.dumps([])     # ""
```

There is no way to distinguish these after serialization. They all deserialize back to `""`.

## Scalar Type Ambiguity

Once serialized, a number and its string representation are identical:

```python
markpickle.dumps(42)    # "42"
markpickle.dumps("42")  # "42"
```

When deserializing, `"42"` becomes `int(42)` if `infer_scalar_types=True`. The original type is lost. The same applies to floats, booleans, dates, and None.

If you need to preserve the distinction between `42` and `"42"`, either:

- Use `infer_scalar_types=False` (everything stays as strings)
- Use YAML front matter to store type hints

## Strings With Markdown Syntax

Strings containing markdown control characters will be interpreted as structure:

```python
markpickle.dumps("# Not a header")  # "# Not a header"
markpickle.loads("# Not a header")  # {"Not a header": None}  -- oops!
```

Problematic characters: `#`, `-`, `*`, `|`, `>`, `[`, `]`, `` ` ``, `_`, `~`, `\n`

There is no escaping mechanism. If your string data contains markdown syntax, it will not round-trip correctly.

## Nested Lists Flatten

Nested lists beyond one level may not round-trip with the correct nesting depth:

```python
original = [[1, 2], [3, 4]]
md = markpickle.dumps(original)    # "  - 1\n  - 2\n  - 3\n  - 4\n"
markpickle.loads(md)               # [1, 2, 3, 4]  -- flattened!
```

A single level of nesting works:

```python
original = [1, 2, [3, 4]]
md = markpickle.dumps(original)    # "- 1\n- 2\n  - 3\n  - 4\n"
markpickle.loads(md)               # [1, 2, [3, 4]]  -- correct
```

## Dict with List Values Lose Structure

When a dict has list values and uses headers:

```python
original = {"items": ["x", "y"]}
md = markpickle.dumps(original)
markpickle.loads(md)  # different structure
```

The header-section format doesn't clearly delimit where the list ends and the next key begins.

## Nested Dict Round-Trip Shape Change

When `serialize_child_dict_as_table=True` (default) and the child dict is flat:

```python
original = {"k": {"a": "1", "b": "2"}}
md = markpickle.dumps(original)  # table under # k
markpickle.loads(md)             # {"k": [{"a": "1", "b": "2"}]}
```

The dict becomes a table, and tables deserialize as a **list** of dicts (since tables represent tabular data with potentially multiple rows).

## Sets and Frozensets

Not directly supported. Sets have no Markdown equivalent. Use the `default` callback:

```python
config = Config()
config.default = lambda x: str(sorted(x)) if isinstance(x, (set, frozenset)) else str(x)
```

## Complex Nested Structures

Markdown is fundamentally flat. While markpickle supports nesting through ATX header levels (`#`, `##`, `###`, etc.) and indented lists, there's a practical depth limit. ATX headers go to level 6 (`######`), so dict nesting beyond 6 levels cannot be represented.

## Tuple vs List Ambiguity

By default, tuples serialize as ordered lists and lists as unordered lists. But not all markdown parsers distinguish between ordered and unordered lists. If you need to be safe, disable ordered list handling:

```python
config = Config(serialize_tuples_as_ordered_lists=False, ordered_list_as_tuple=False)
```

## Keys Must Be Strings

Dict keys are rendered as ATX headers or table headers, both of which are text. Non-string keys are converted via `str()`:

```python
markpickle.dumps({1: "one"})  # "# 1\n\none\n"
markpickle.loads("# 1\n\none\n")  # {"1": "one"}  -- key is now a string
```

## Whitespace Sensitivity

Leading/trailing whitespace in strings is not preserved. Markdown collapses whitespace.

```python
markpickle.dumps("  hello  ")   # "  hello  "
markpickle.loads("  hello  ")   # "hello"  -- stripped
```

## Bytes May Not Round-Trip in Lists

While standalone bytes round-trip via base64 data URLs, bytes inside lists may lose their type:

```python
markpickle.dumps([b"hello", b"world"])  # data URLs in list items
# Deserialization of data URLs in list items may not reconstruct bytes
```

## Unicode Math Symbols Limitations

The Unicode text formatting feature (`preserve_formatting_as_unicode`) has limitations:

- Only covers ASCII letters (a-z, A-Z) and digits (0-9)
- Punctuation, spaces, and non-Latin characters are not converted
- Some fonts render mathematical symbols poorly
- Screen readers may not interpret them correctly
- String comparison breaks: `"hello" != to_bold("hello")`
- Search won't find Unicode-formatted text with plain text queries

## Arbitrary Markdown Won't Deserialize

markpickle is designed to round-trip **its own output**. Feeding it arbitrary README.md files or hand-written markdown will often produce unexpected results or raise errors. For parsing arbitrary markdown, use `mistune` or another markdown AST library directly.

## What DOES Round-Trip Cleanly

For reference, these types survive `dumps()` -> `loads()` intact:

- Non-empty strings (without markdown syntax characters)
- Positive integers
- Floats
- Booleans
- Dates (as `datetime.date`)
- Flat lists of the above
- Flat dicts with string keys and scalar values
- Lists of flat dicts (tables)
- Tuples of scalars (via ordered lists)
- Bytes (standalone, via base64 data URLs)
