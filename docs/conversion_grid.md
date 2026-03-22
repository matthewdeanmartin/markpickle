# Conversion Grid

## Useful Conversion Patterns

| From | To | Tool |
| --- | --- | --- |
| Python dict/list | Markdown | `markpickle.dumps()` |
| Markdown | Python dict/list | `markpickle.loads()` |
| JSON string | Markdown | `markpickle.convert_json_to_markdown()` |
| Markdown | JSON string | `markpickle.convert_markdown_to_json()` |
| Markdown | HTML | mistune, commonmark, etc. |
| HTML | Markdown | reverse-markdown, html2text |
| Markdown | AST | mistune (AST mode) |
| HTML | DOM | BeautifulSoup |
| Python dict | JSON | `json.dumps()` |
| JSON | Python dict | `json.loads()` |

## Format Equivalences

These formats represent roughly the same data model (nested key-value + arrays):

- JSON
- YAML
- TOML
- MessagePack
- Markdown (via markpickle, lossy)

## When to Use What

| Goal | Tool |
| --- | --- |
| Python object to readable Markdown | markpickle |
| Structured Markdown to Python dict | markpickle |
| Arbitrary Markdown to HTML | mistune |
| Arbitrary Markdown to DOM tree | mistune AST mode |
| High-fidelity serialization | pickle, json |
| Human-editable config | TOML, YAML |
| Data exchange API | JSON |
| Tabular data to Markdown table | tabulate, pytablewriter |
| DOM-style dict to Markdown | json2md |
