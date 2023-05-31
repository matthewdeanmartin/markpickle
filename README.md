# markpickle

Markpickle is a Python library for lossy serialization of markdown to simple python data types and back. It will create predictable markdown from a python object, but can't turn all markdown files into sensible python objects (for that use a markdown library that creates an AST). I created this because I wanted a way to turn json into Markdown. It is an accidental successor to [markdown-to-json](https://github.com/njvack/markdown-to-json).

For example this

```markdown
- 1
- 2
```

becomes the python list `[1, 2]`

Almost all markdown libraries use it as intended, as a way to generate HTML fragments from untrusted sources for insertion into some other HTML template. We are using it to represent data.

![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/markpickle) [![Downloads](https://pepy.tech/badge/markpickle/month)](https://pepy.tech/project/markpickle/month)

______________________________________________________________________

## Installation

```shell
pip install markpickle
```

## Capabilities

This is a lossy serialization. Markdown is missing too many concepts to make a high fidelity representation of a python data structure. If you want an object model that faithfully represents each object in a Markdown document, use the AST of mistune or one of the other markdown parsers.

______________________________________________________________________

### Supported Types

- Scalar values
- Lists of scalar values
- Dictionaries with scalar values
- Lists of dictionaries of scalar values
- Dictionaries with list values
- Partial support for blanks/string with leading/trailing whitespace

See [examples](https://github.com/matthewdeanmartin/markpickle/blob/main/docs/examples.md).

### Not Supported

- Things not ordinarily serializable
- Markdown that uses more than headers, lists, tables
- Blanks, falsy values, empty iterables don't round trip
- Scalar type inference doesn't round trip. After a scalar is converted to a markdown string, there is no indication if the original was a string or not.

______________________________________________________________________

## Serializing and Deserializing

______________________________________________________________________

### Serializing

Results can be formatted at the cost of speed. Dictionaries can be represented as tables or header-text pairs.

### Deserializing

Markdown is deserialized by parsing the document to an abstract syntax tree (AST). This is done by `mistune`. If the markdown file has the same structure that markpickle uses, then it will create a sensible object. Deserializing a random README.md file is not expected to always work. For that, you should use mistune's AST.

### Round Tripping

Some but not all data structures will be round-trippable. The goal is that the sort of dicts you get from loading JSON will be round-trippable, provided everything is a string.

### Splitting Files

If typical serialization scenarios, many json files might be written to a single file, or in the case of yaml, you can put multiple documents into one file separated by `---`. markpickle can treat the horizontal rule as a document spliter if you use `split_file`. It works like [splitstream](https://github.com/rickardp/splitstream), but less efficiently.

## CLI

This command will take a deserializable markdown file and output json.

```bash
python -m markpickle "docs/individual/list of scalars.md"
```

## Prior Art

People normally want to convert json to markdown. Json looks like python dict, so if you can do that you can probably do both.

### Serializing to Markdown

[json2md](https://github.com/IonicaBizau/json2md), a node package, will turn json that looks like the HTML document object model into markdown, e.g.

```python
{"h1": "Some Header",
 "p": "Some Text"}
```

[tomark](https://pypi.org/project/tomark/) will turn dict into a markdown table. Unmaintained.

[pytablewriter](https://pytablewriter.readthedocs.io/en/latest/pages/reference/writers/text/markup/md.html) also, dict to table, but supports many tabular formats.

### Deserializing to Python

Most libraries turn markdown into document object model. Markdown-to-json is the most similar to markpickle's goal of turning a markdown document into a python data types, in this case nested dicts.

[markdown-to-json](https://github.com/njvack/markdown-to-json) is the library most similar to markpickle, but is somewhat broken, unmaintained and depends on the unmaintained commonmark library.

[mistune](https://pypi.org/project/mistune/) will turn markdown into an Abstract Syntax Tree. The AST is faithful representation of the Markdown, including concepts that have no semantic equivalent to python datatypes.

[beautifulsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) will let you navigate the HTML DOM. So you can turn the markdown into HTML, then parse with Beautiful Soup.

## Schema Validation for Markdown

In the case of a serialization library, you'd want something that would indicate if your markdown file will successfully deserialize back into python.

I haven't really found anything that says, for example, "This markdown document shall have one # Header and a 3 column table and nothing else."

- [schema-markdown-js](https://craigahobbs.github.io/schema-markdown-js/language/) A json schema that happens to be using markdown as its syntax.

## Credits

I copied the ATX-dictionary-like header parsing from [markdown-to-json](https://github.com/njvack/markdown-to-json).

## Documentation

- [Examples](https://github.com/matthewdeanmartin/markpickle/blob/main/docs/examples.md)
- [TODO](https://github.com/matthewdeanmartin/markpickle/blob/main/docs/TODO.md)
- [People solving similar problems on StackOverflow](https://github.com/matthewdeanmartin/markpickle/blob/main/docs/stackoverflow.md)

## Change Log

- 1.1.0 - Basic functionality. See [examples](https://github.com/matthewdeanmartin/markpickle/blob/main/docs/examples.md) for what is supported.
- 1.2.0 - Add support for binary data, which is serialized as images with data URLs.
