# markpickle Proposals

## Current State Summary

### What works
- **Scalars**: str, int, float, bool, None, datetime.date, datetime.datetime, bytes (as base64 data URL)
- **Lists**: flat scalar lists, nested lists
- **Dicts**: ATX headers (`# key` / `## key`) for nested dicts, definition lists (partial)
- **Tables**: list-of-dicts to/from markdown tables, list-of-lists mode
- **Multi-doc**: `---` separator for multiple documents in one file
- **Classes**: `__getstate__`, dataclasses, `__dict__` objects via dict conversion
- **Custom**: `default` callback for arbitrary type handling

### What's broken with tables

Tables are currently used too aggressively. The `serialize_child_dict_as_table` flag (default `True`) causes any dict nested inside another dict to become a table. This makes sense for **one** level:

```python
# GOOD: h1 key with a flat dict value -> table under header
{"people": {"Alice": 30, "Bob": 25}}
```

```markdown
# people

| Alice | Bob |
| ----- | --- |
| 30    | 25  |
```

But it falls apart for **dict-in-dict-in-dict** because markdown has no nested table construct. The code in `render_dict` (serialize.py:259-278) hits a dict value, writes an ATX header, then forcibly renders the child dict as a table even when it should recurse into deeper ATX headers. Result: a flat table where you expected `## subkey` / `### subsubkey` nesting.

**The rule should be:** Tables are for *leaf-level* flat dicts (all scalar values) or list-of-flat-dicts. If a dict has dict/list values, it should use ATX header nesting, not tables.

---

## Proposal 1: Fix Table Heuristics

### Problem
`serialize_child_dict_as_table=True` blindly converts child dicts to tables even when they contain non-scalar values (nested dicts, lists). This produces mangled output.

### Solution
Add a check before table rendering: only use tables when all values in the dict are scalars. Otherwise, fall through to ATX header recursion.

```python
def is_flat_dict(d: dict) -> bool:
    """True if all values are scalars (no nested dicts/lists/sets)."""
    return all(not isinstance(v, (dict, list, set, tuple)) for v in d.values())
```

In `render_dict`, change the `isinstance(item, dict)` branch (line 259):

- If `is_flat_dict(item)` and `serialize_child_dict_as_table`: render as table
- Else: recurse with `render_dict` using deeper header level (`header_level + 1`)

Similarly for `list-of-dicts` in `render_list` (line 316): only table-ify if all dicts in the list are flat.

### Config changes
- Keep `serialize_child_dict_as_table` but document it as "prefer tables for flat child dicts"
- Add `serialize_table_max_depth: int = 1` to limit how many nesting levels can become tables (default 1 = only immediate children)

### Backwards compatibility
Default behavior changes slightly: deep nested dicts that previously produced garbled tables will now produce ATX header nesting. This is a bug fix, not a breaking change.

---

## Proposal 2: YAML Front Matter Support

### Problem
The "YAML on top, markdown party on the bottom" pattern is a de facto standard (Jekyll, Hugo, Obsidian, Astro, MDX, Docusaurus, etc.) and markpickle doesn't support it.

```markdown
---
title: My Document
date: 2024-01-15
tags: [python, markdown]
---

# Actual Content

Some text here.
```

### Solution
Support reading and writing YAML front matter as metadata separate from the body.

#### Deserialization
```python
def loads(value, config=None) -> SerializableTypes:
    ...

def loads_with_frontmatter(value, config=None) -> tuple[dict, SerializableTypes]:
    """Returns (frontmatter_dict, body_object)"""
```

If `config.parse_yaml_frontmatter = True` (default False for backwards compat), detect `---` at the start of the document, parse everything before the closing `---` as YAML, and process the rest as normal markdown.

#### Serialization
```python
def dumps_with_frontmatter(
    body: SerializableTypes,
    frontmatter: dict,
    config=None
) -> str:
    """Emit YAML front matter + markdown body."""
```

#### Dependency
- Use `pyyaml` (or `tomli`/`tomllib` for TOML front matter as alt)
- Make it an optional dependency: `pip install markpickle[frontmatter]`

#### What goes in front matter vs body
Front matter is for metadata (type hints, schema info, authorship, dates). Body is the actual data. This naturally solves the `__setstate__` problem from TODO.md: put the class name in front matter, data in body.

```markdown
---
python_type: mymodule.Person
---

# name
Alice

# age
30
```

---

## Proposal 3: More Scalar Types

### Currently supported scalars
str, int, float, bool, None, datetime.date, datetime.datetime, bytes

### Proposed new scalars

#### 3a. `complex` numbers
Python's `complex` type has no direct markdown analog, but we can use a convention:

- Serialize: `3+4j` (Python repr)
- Deserialize: detect pattern `\d+[+-]\d+j` and parse with `complex()`
- Config: `infer_complex_types: bool = False`

#### 3b. `Decimal`
Financial/precise numbers:

- Serialize: `"123.456"` (just str)
- Deserialize: when `infer_decimal_types=True`, parse numeric strings as `Decimal` instead of `float`
- Mutual exclusion with float inference needed

#### 3c. `UUID`
- Serialize: `"550e8400-e29b-41d4-a716-446655440000"` (standard form)
- Deserialize: detect UUID pattern (8-4-4-4-12 hex) and parse with `uuid.UUID()`
- Config: `infer_uuid_types: bool = False`

#### 3d. `pathlib.Path`
- Serialize: str(path)
- Deserialize: can't reliably distinguish from regular strings without front matter / type hints
- Best handled via front matter metadata or a convention like backtick-wrapped paths

#### 3e. `enum.Enum`
- Serialize: `EnumClass.MEMBER_NAME` or just `"MEMBER_NAME"`
- Deserialize: requires knowing the enum class (front matter or `object_hook`)
- Proposal: support via `object_hook` or `deserialize_custom_types` config dict

#### 3f. `re.Pattern` (compiled regex)
- Serialize: the pattern string, wrapped in `/pattern/flags` convention
- Deserialize: detect `/pattern/` and compile
- Niche but fun

### Summary table

| Type | Serialize | Deserialize | Needs config | Risk |
| --- | --- | --- | --- | --- |
| complex | repr() | regex detect | yes | low |
| Decimal | str() | pattern detect | yes | medium (float conflict) |
| UUID | str() | regex detect | yes | low |
| Path | str() | ambiguous | front matter | high |
| Enum | name | needs class ref | object_hook | medium |
| Pattern | /pattern/ | convention | yes | low |

---

## Proposal 4: Unicode Text Formatting as Python String Metadata

### The idea
Python strings don't have bold... **or do they?**

Unicode has Mathematical Alphanumeric Symbols that provide bold, italic, bold-italic, monospace, script, and other variants for Latin letters and digits. These are real characters that render in terminals, editors, and markdown:

| Style | Example | Unicode Block |
| --- | --- | --- |
| Bold | **hello** -> `????????????????????` | U+1D400-1D419 |
| Italic | *hello* -> `????????????????????` | U+1D434-1D44D |
| Bold Italic | `????????????????????????????` | U+1D468-1D481 |
| Monospace | `` `hello` `` -> `????????????????????` | U+1D670-1D689 |
| Script | `????????????????????????` | U+1D49C-1D4B5 |
| Double-struck | `????????????????????` | U+1D538-1D551 |
| Fraktur | `????????????????????` | U+1D504-1D51D |

### How it works

#### Serialization direction (Python -> Markdown)
Detect Unicode math-styled characters in Python strings and convert them to markdown formatting:

- `????????????????????` -> `**hello**` (bold)
- `????????????????????` -> `*hello*` (italic)
- `????????????????????` -> `` `hello` `` (code)

#### Deserialization direction (Markdown -> Python)
When `config.preserve_formatting_as_unicode = True`:

- `**hello**` -> `????????????????????` (Unicode bold)
- `*hello*` -> `????????????????????` (Unicode italic)
- `` `hello` `` -> `????????????????????` (Unicode monospace)

Instead of stripping formatting (current behavior in `strip_formatting()`), convert it to Unicode equivalents so the information survives round-tripping.

### Config
```python
preserve_formatting_as_unicode: bool = False  # default off for backwards compat
unicode_bold: bool = True      # convert **text** to Unicode bold
unicode_italic: bool = True    # convert *text* to Unicode italic
unicode_monospace: bool = True  # convert `text` to Unicode monospace
```

### Pros
- Strings actually DO carry formatting now
- Round-trips through markdown without loss
- Works in terminals, filenames, anywhere strings go
- No dependency on any rendering engine

### Cons
- Unicode math symbols don't cover all characters (no punctuation, limited non-Latin)
- Some fonts render these poorly
- Accessibility concerns (screen readers may not handle these well)
- Search/comparison breaks (`"hello" != "????????????????????"`)

### Implementation
Build a translation table (dict mapping `ord('a')` -> `ord('\U0001D41A')` etc.) and use `str.translate()`. The existing `unicode_formatting.py` module already has terminal escape code logic; this would be the "pure Unicode" alternative.

---

## Proposal 5: More Complex Types via Markdown Constructs

### 5a. Sets via unordered lists
Markdown bullet lists are inherently unordered. Use a convention:

- Serialize `{1, 2, 3}` as a list with a front matter hint or a special marker
- Or: sets serialize identically to lists, but deserialize as sets when `config.prefer_sets = True`
- Or: use a comment convention `<!-- type: set -->` before the list

### 5b. Tuples via ordered lists
Markdown supports ordered lists (`1. item`). Currently unused by markpickle.

```markdown
1. Alice
2. 30
3. New York
```

-> `("Alice", 30, "New York")`

Config: `serialize_tuples_as_ordered_lists: bool = True`

This gives tuples a distinct representation from lists (unordered bullet lists).

### 5c. NamedTuples / dataclasses via definition lists
Definition lists (already partially supported) are a natural fit:

```markdown
Person
:   name: Alice
:   age: 30
```

Or with the YAML front matter approach:
```markdown
---
python_type: Person
---

# name
Alice

# age
30
```

### 5d. Nested dicts via deeper ATX headers (fix existing)
Currently broken (TODO.md: "Doesn't deserialize python nested dict to ATX headers, except 1st level"). Fix the recursion in `render_dict` to properly increment `header_level` when serializing nested dicts as ATX sections rather than tables.

### 5e. OrderedDict
Markdown headers and lists have inherent ordering. `OrderedDict` could be the default deserialization target for ATX-header dicts (Python 3.7+ dicts are ordered anyway, so this is mostly symbolic).

### 5f. `frozenset`
Same as set but immutable. Serialize identically; config flag to choose set vs frozenset on deserialize.

---

## Proposal 6: Blockquotes as Strings with Attribution

Markdown blockquotes are unused by markpickle:

```markdown
> To be or not to be, that is the question.
>
> -- William Shakespeare
```

### Options
- **As plain string**: Strip `>` and return the text. Simple.
- **As attributed quote tuple**: `("To be or not to be...", "William Shakespeare")`
- **As dict**: `{"quote": "To be or not to be...", "author": "William Shakespeare"}`

Blockquotes could also represent "escaped" or "literal" string values where we want to preserve whitespace and newlines.

---

## Proposal 7: Code Blocks as Typed Values

Code blocks are partially handled (as strings) but could carry more meaning:

````markdown
```python
def hello():
    print("world")
```
````

### Options
- **Current**: treated as plain string (formatting stripped)
- **Proposed**: return a typed wrapper or tuple `("python", "def hello():\n    print(\"world\")\n")`
- **With front matter**: could specify that code blocks should be `exec()`'d or `eval()`'d (dangerous but opt-in)
- **As bytes**: code blocks with language `base64` could be an alternative to data URLs for binary data

---

## Proposal 8: Links and Images as Rich Types

### Links
Currently URL objects via `urllib.parse.urlparse` are partially handled in list deserialization. Standardize:

- Serialize: `urllib.parse.ParseResult` or `yarl.URL` -> `[text](url)` or bare `https://...`
- Deserialize: detect links -> return `ParseResult` or a `Link(text, url)` namedtuple
- Config: `deserialize_links_as_urls: bool = False`

### Images
Already supported as bytes via base64 data URLs. Could also support:

- File path images: `![alt](path/to/image.png)` -> `Path("path/to/image.png")`
- Remote images: `![alt](https://...)` -> URL object
- Config: `serialize_images_to_pillow` already exists but is unused

---

## Proposal 9: Horizontal Rules as Sentinel Values

Currently `---` is a document separator. But within a document, `***` or `___` could represent:

- `None` (a "nothing here" marker)
- A section break in a long string (-> `\n\n---\n\n` becomes a delimiter)
- A sentinel/separator in lists

Low priority but worth noting as an unused markdown construct.

---

## Proposal 10: Markdown Comments as Type Hints

HTML comments are valid markdown:

```markdown
<!-- type: set -->
- 1
- 2
- 3

<!-- type: tuple -->
1. Alice
2. 30
```

This is lighter than YAML front matter for inline type hints. Could be used alongside or instead of front matter.

### Implementation
- Parse `<!-- type: X -->` before any markdown block
- Use it to guide deserialization (set vs list, tuple vs list, custom class, etc.)
- On serialization, emit comments when the Python type would otherwise be ambiguous

---

## Priority Ranking

| # | Proposal | Impact | Effort | Priority |
| --- | --- | --- | --- | --- |
| 1 | Fix table heuristics | High (bug fix) | Low | **P0** |
| 5d | Fix nested dict ATX recursion | High (bug fix) | Low | **P0** |
| 2 | YAML front matter | High (ecosystem compat) | Medium | **P1** |
| 4 | Unicode text formatting | Medium (unique feature) | Medium | **P1** |
| 5b | Tuples as ordered lists | Medium (new type) | Low | **P1** |
| 3 | More scalar types (UUID, complex, Decimal) | Medium (completeness) | Low | **P2** |
| 5a | Sets | Low-medium | Low | **P2** |
| 8 | Links/images as rich types | Medium | Medium | **P2** |
| 6 | Blockquotes | Low | Low | **P3** |
| 7 | Code blocks as typed values | Low | Low | **P3** |
| 10 | Markdown comments as type hints | Medium | Medium | **P3** |
| 9 | Horizontal rules as sentinels | Low | Low | **P3** |

---

## Appendix: Markdown Constructs vs Python Types (Full Grid)

| Markdown Construct | Current Python Mapping | Proposed Python Mapping |
| --- | --- | --- |
| `# Header` | dict key (level 1) | same |
| `## Header` | nested dict key (level 2) | same, fix deeper nesting |
| `- item` | list element | list element |
| `1. item` | (unused) | tuple element |
| `\| table \|` | list-of-dicts or list-of-lists | same, fix heuristics |
| `> blockquote` | (unused) | string or attributed tuple |
| `` `code` `` | stripped formatting | Unicode monospace char |
| `**bold**` | stripped formatting | Unicode bold chars |
| `*italic*` | stripped formatting | Unicode italic chars |
| ` ```code block``` ` | string | (language, string) tuple |
| `[text](url)` | partial (urlparse) | Link namedtuple / ParseResult |
| `![alt](src)` | bytes (base64 data URL) | bytes / Path / URL |
| `---` | document separator | same |
| `***` / `___` | (unused) | sentinel / None |
| `<!-- comment -->` | (unused) | type hint |
| `term\n: defn` | partial dict (single pair) | full dict support |
| YAML front matter | (unused) | metadata dict |
