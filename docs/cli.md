# CLI Reference

markpickle ships with a `markpickle` command installed by `pip install markpickle`.
You can also invoke it as `python -m markpickle`.

```
markpickle [--version] <command> [options]
```

## Global flags

| Flag | Description |
| ----------- | -------------------------------- |
| `--version` | Print the installed version and exit |
| `--help` | Show help text |

---

## `markpickle convert`

Convert a Markdown file to JSON.

```bash
markpickle convert <infile> [outfile] [--config FILE]
```

| Argument | Description |
| ------------- | ------------------------------------------------------- |
| `infile` | Path to the Markdown file, or `-` to read from stdin |
| `outfile` | Optional output path. Defaults to stdout if omitted |
| `--config` | TOML config file (default: `pyproject.toml` in cwd) |

### Examples

```bash
# Print JSON to stdout
markpickle convert data.md

# Write to file
markpickle convert data.md out.json

# Read from stdin, write to stdout
cat data.md | markpickle convert -

# Use a custom config
markpickle convert data.md --config settings.toml
```

### Output format

The output is pretty-printed JSON. Non-JSON-native types (dates, complex numbers, etc.)
are serialized using their string representation via `json.dumps(obj, default=str)`.

---

## `markpickle validate`

Check whether a Markdown file can be safely round-tripped (parsed and re-serialized without
data loss).

```bash
markpickle validate <infile> [--no-roundtrip] [--no-ast] [--config FILE]
```

| Argument | Description |
| ---------------- | ---------------------------------------------- |
| `infile` | Path to the Markdown file to validate |
| `--no-roundtrip` | Skip the round-trip equality check |
| `--no-ast` | Skip AST structural analysis |
| `--config` | TOML config file (default: `pyproject.toml` in cwd) |

### Exit codes

| Code | Meaning |
| ---- | ---------------------------------- |
| 0 | File passed all checks |
| 1 | One or more issues found |

### Examples

```bash
# Full validation (AST analysis + round-trip check)
markpickle validate data.md

# Only run round-trip check, skip AST
markpickle validate data.md --no-ast

# Only run AST analysis, skip round-trip
markpickle validate data.md --no-roundtrip
```

---

## `markpickle doctor`

Print a diagnostic table of optional dependencies and their installed versions.

```bash
markpickle doctor
```

### Example output

```
-----------------------------------------------
Package                  Status
-----------------------------------------------
[ok] Python              3.11.9
[ok] mistune             3.0.2
[!!] tabulate [tables]   NOT INSTALLED
[!!] Pillow [images]     NOT INSTALLED
[!!] mdformat [format]   NOT INSTALLED
[ok] tkinter             available (stdlib)
-----------------------------------------------

To install all optional extras:
  pip install markpickle[all]
```

Items marked `[!!]` are optional but unlock additional features:

| Extra | Package | Feature |
| -------- | ----------- | -------------------------------------- |
| `tables` | `tabulate` | Prettier Markdown table output |
| `images` | `Pillow` | Bytes ↔ data-URL image conversion |
| `format` | `mdformat` | Formatted Markdown output (GUI Format panel) |
| `all` | all above | Install everything |

---

## `markpickle gui`

Launch the interactive tkinter GUI.

```bash
markpickle gui
# or via the dedicated entry point:
markpickle-gui
```

Requires tkinter (part of the Python standard library, but excluded from some
minimal Python distributions). On Linux you may need to install it separately:

```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

### GUI panels

| Panel | Description |
| -------- | -------------------------------------------- |
| Convert | Paste Markdown or Python; convert either way |
| Format | Format Markdown with mdformat |
| Validate | Run round-trip and AST checks on Markdown |
| Config | Inspect and edit the active Config settings |
| Doctor | Same output as `markpickle doctor` |
| Help | Syntax cheat sheet |

---

## Configuration file

All subcommands accept `--config FILE` pointing to a TOML file. Without `--config`,
markpickle looks for a `[tool.markpickle]` section in `pyproject.toml` in the current
working directory.

Example `pyproject.toml` section:

```toml
[tool.markpickle]
list_bullet_style = "*"
infer_scalar_types = true
serialize_child_dict_as_table = false
```

See [Configuration](configuration.md) for all available keys.
