# markpickle

Markpickle treats markdown as a data serialization format.

Markpickle is a Python library for lossy serialization of markdown to simple python data types and back. Imagine if
markdown headers were used to define nested dictionaries and Markdown lists were python lists.

It will create predictable markdown from a python object, but can't turn all markdown files into sensible python
objects (for that use a markdown library that creates an AST). I created this because I wanted a way to turn json into
Markdown. It is an accidental successor to [markdown-to-json](https://github.com/njvack/markdown-to-json).

```markdown
- 1
- 2
```

becomes the python list `[1, 2]`

```markdown
# Cat

## Name

Ringo

## Species

Felix
```

becomes the python dict `{"Cat": {"Name": "Ringo", "Species": "Felix"}}`

See [examples](docs/examples.md) for representable types.

Almost all markdown libraries use it as a way to generate HTML fragments from untrusted sources for insertion into some
other HTML template. We are using it to represent data. See [guidance](docs/choosing_a_library.md) for which library
make sense for you.

![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/markpickle) [![Downloads](https://pepy.tech/badge/markpickle/month)](https://pepy.tech/project/markpickle/month)

## Installation

```shell
pip install markpickle
```

To install with a formatter, image-as-link format,

```shell
pip install markpickle[all]
```

Discover capabilities with gui.

```shell
markpickle gui
```

## Capabilities

This is a lossy serialization. Markdown is missing too many concepts to make a high fidelity representation of a python
data structure. If you want an object model that faithfully represents each object in a Markdown document, use the AST
of mistune or one of the other markdown parsers.

### Supported Types

- Scalar values: strings, integers, floats, booleans, `None`
- Dates (`datetime.date`) and datetimes (`datetime.datetime`)
- Complex numbers, `decimal.Decimal`, and `uuid.UUID` (opt-in via `Config`)
- Bytes serialized as base64 data URLs
- Lists of scalar values, including nested lists
- Tuples (as numbered ordered lists)
- Dictionaries with scalar, list, or nested dict values
- Lists of dictionaries (as Markdown tables)
- YAML front matter (opt-in via `Config`)
- Unicode text formatting preservation (bold/italic/monospace)
- Objects with `__getstate__` or `__dict__`, and dataclasses
- Partial support for blanks/string with leading/trailing whitespace

See [examples](https://github.com/matthewdeanmartin/markpickle/blob/main/docs/examples.md).

### Not Supported

- Things not ordinarily serializable
- Markdown that uses more than headers, lists, tables
- Blanks, falsy values, empty iterables don't round trip
- Scalar type inference doesn't round trip. After a scalar is converted to a markdown string, there is no indication if
  the original was a string or not.

## Serializing and Deserializing

### Serializing

Results can be formatted at the cost of speed. Dictionaries can be represented as tables or header-text pairs.

### Deserializing

Markdown is deserialized by parsing the document to an abstract syntax tree (AST). This is done by `mistune`. If the
markdown file has the same structure that markpickle uses, then it will create a sensible object. Deserializing a random
README.md file is not expected to always work. For that, you should use mistune's AST.

### Round Tripping

Some but not all data structures will be round-trippable. The goal is that the sort of dicts you get from loading JSON
will be round-trippable, provided everything is a string.

### Splitting Files

If typical serialization scenarios, many json files might be written to a single file, or in the case of yaml, you can
put multiple documents into one file separated by `---`. markpickle can treat the horizontal rule as a document spliter
if you use `split_file`. It works like [splitstream](https://github.com/rickardp/splitstream), but less efficiently.

## CLI

markpickle ships with a command-line interface. The `markpickle` entry point is installed
automatically; you can also invoke it as `python -m markpickle`.

```bash
# Convert a Markdown file to JSON (stdout)
markpickle convert data.md

# Convert and write to a file
markpickle convert data.md out.json

# Read Markdown from stdin
markpickle convert -

# Check whether a file round-trips safely
markpickle validate data.md

# Show installed optional libraries and their status
markpickle doctor

# Launch the interactive tkinter GUI
markpickle gui
```

Use `markpickle --help` or `markpickle <command> --help` for full usage.

## Prior Art

Imagine you have json and want to the same data as markdown. Json looks like python dict, so any python library that can
convert json to markdown, probably can convert a python dict to markdown.

Many tools turn tabular data into a markdown table.

### Serializing to Markdown

[json2md](https://github.com/IonicaBizau/json2md), a node package, will turn json that looks like the HTML document
object model into markdown, e.g.

```python
{"h1": "Some Header",
 "p": "Some Text"}
```

[tomark](https://pypi.org/project/tomark/) will turn dict into a markdown table. Unmaintained.

[pytablewriter](https://pytablewriter.readthedocs.io/en/latest/pages/reference/writers/text/markup/md.html) also, dict
to table, but supports many tabular formats.

### Deserializing to Python

Most libraries turn markdown into document object model. Markdown-to-json is the most similar to markpickle's goal of
turning a markdown document into a python data types, in this case nested dicts.

[markdown-to-json](https://github.com/njvack/markdown-to-json) is the library most similar to markpickle and is now
maintained. It handles only deserialization and conversion to json.

[mistune](https://pypi.org/project/mistune/) will turn markdown into an Abstract Syntax Tree. The AST is faithful
representation of the Markdown, including concepts that have no semantic equivalent to python datatypes.

[beautifulsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) will let you navigate the HTML DOM. So you can
turn the markdown into HTML, then parse with Beautiful Soup.

[keepachangelog](https://pypi.org/project/keepachangelog/) is a single-schema Markdown to python dict tool.

## Representable Types

There is one optional root dictionary representable with ATX headers, e.g. `#`, `##`, etc. Lists are nestable lists or
dicts. For the most part, this looks like the types that JSON can represent.

```python
SerializableTypes: TypeAlias = Union[
    ColumnsValuesTableType,
    dict[str, "SerializableTypes"],
    list["SerializableTypes"],
    tuple["SerializableTypes"],
    str,
    int,
    float,
    bool,
    datetime.date,
    datetime.datetime,
    None,
]
```

The deserialized types is the same except all Scalars are strings.

## Schema Validation for Markdown

In the case of a serialization library, you'd want something that would indicate if your markdown file will successfully
deserialize back into python.

I haven't really found anything that says, for example, "This markdown document shall have one # Header and a 3 column
table and nothing else."

- [schema-markdown-js](https://craigahobbs.github.io/schema-markdown-js/language/) A json schema that happens to be
  using markdown as its syntax.

## Credits

I copied the ATX-dictionary-like header parsing from [markdown-to-json](https://github.com/njvack/markdown-to-json).

## Documentation

Full documentation is available at [markpickle.readthedocs.io](https://markpickle.readthedocs.io/).

- [Getting Started](docs/getting_started.md)
- [Examples](docs/examples.md)
- [Configuration](docs/configuration.md)
- [Things That Will Not Work](docs/limitations.md)
- [Choosing a Library](docs/choosing_a_library.md)
- [How It Works](docs/how_it_works.md)
- [Credits](docs/credits.md)
- [Changelog](CHANGELOG.md)
