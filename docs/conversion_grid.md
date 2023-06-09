# Conversions

## Useful Conversion Patterns
HTML <-> Markdown
- markdown -> HTML = Mistune, and many others
- HTML -> markdown = Reverse markdown tools

Markdown <-> Python dicts/etc
- JSON -> markdown = markpickle
- Markdown -> python dict/etc = markpickle

DOM
- markdown -> Markdown AST = Mistune, others
- markdown -> HTML -> DOM =  Mistune + Beautiful soup

DOM Simplifiers
- HTML -> Markdown -> python dict/ect = Reverse Markdown + markpickle 

Traditional serialization, API payloads
- python dict/etc -> json = json.dumps()
- json -> python dict/etc = json.loads()

Equivalent
----------
json <-> yaml <-> msgpack
