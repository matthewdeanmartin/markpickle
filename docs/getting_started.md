# Getting Started

## Installation

```shell
pip install markpickle
```

Or with uv:

```shell
uv add markpickle
```

## Basic Usage

markpickle follows the same API pattern as `json` and `pickle`:

- `dumps(value)` - serialize to string
- `loads(string)` - deserialize from string
- `dump(value, stream)` - serialize to file-like object
- `load(stream)` - deserialize from file-like object

### Serialize Python to Markdown

```python
import markpickle

# Scalars
markpickle.dumps("hello")          # "hello"
markpickle.dumps(42)               # "42"
markpickle.dumps(True)             # "True"
markpickle.dumps(3.14)             # "3.14"

# Lists
markpickle.dumps([1, 2, 3])        # "- 1\n- 2\n- 3\n"

# Dicts (become ATX headers)
markpickle.dumps({"key": "value"}) # "# key\n\nvalue\n"
```

### Deserialize Markdown to Python

```python
import markpickle

markpickle.loads("hello")           # "hello"
markpickle.loads("42")              # 42
markpickle.loads("- a\n- b\n")     # ["a", "b"]
markpickle.loads("# key\n\nval\n") # {"key": "val"}
```

### File I/O

```python
import markpickle

# Write to file
with open("data.md", "w") as f:
    markpickle.dump({"name": "Alice", "age": 30}, f)

# Read from file
with open("data.md") as f:
    data = markpickle.load(f)
```

### Multiple Documents

Separate multiple objects in one file with `---`:

```python
import markpickle

# Serialize multiple documents
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

# Deserialize multiple documents
import io
docs = list(markpickle.load_all(io.StringIO(md)))
# ["hello", [1, 2], {"key": "val"}]
```

### Configuration

Pass a `Config` object to customize behavior:

```python
import markpickle
from markpickle import Config

config = Config()
config.serialize_child_dict_as_table = False  # Use ATX headers instead of tables
config.list_bullet_style = "*"                # Use * instead of -

markpickle.dumps([1, 2, 3], config=config)
# "* 1\n* 2\n* 3\n"
```

See [Configuration](configuration.md) for all options.

### JSON to Markdown (and back)

```python
import markpickle

md = markpickle.convert_json_to_markdown('{"name": "Alice", "age": 30}')
json_str = markpickle.convert_markdown_to_json("# name\n\nAlice\n\n# age\n\n30\n")
```

### CLI

markpickle ships with a `markpickle` command (also available as `python -m markpickle`):

```bash
# Convert a Markdown file to JSON and print to stdout
markpickle convert data.md

# Convert and write output to a file
markpickle convert data.md out.json

# Read Markdown from stdin, write JSON to stdout
markpickle convert -

# Use a custom config file
markpickle convert data.md --config my_config.toml

# Validate that a file round-trips safely
markpickle validate data.md

# Show installed optional libraries
markpickle doctor

# Launch the interactive tkinter GUI
markpickle gui
```

Run `markpickle --help` or `markpickle <command> --help` for full usage.

See [CLI Reference](cli.md) for complete documentation of all subcommands and flags.
