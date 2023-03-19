import markpickle

EXAMPLES = {
    "scalar": 6,
    "list of scalars": [1, 2, 3],
    "list of dictionaries": [{"animal": "cat", "name": "Frisky"}, {"animal": "dog", "name": "Fido"}],
    "dictionaries of strings": {"animal": "cat", "name": "Frisky"},
    "dictionary of lists": {
        "ages": [24, 59, 45],
        "countires": ["US", "Canada", "Iceland"],
    },
    "dictionary of dictionaries": {
        "Best Cat": {"animal": "cat", "name": "Frisky"},
        "Best Dog": {"animal": "dog", "name": "Fido"},
    },
}

with open("docs/examples.md", "w", encoding="utf-8") as file:
    file.write("# Examples\n\n")
    for key, value in EXAMPLES.items():
        string = markpickle.dumps(value)
        file.write(f"## {key}\n")
        file.write("```python\n")
        file.write(repr(value))
        file.write("\n```\n\n")

        file.write("```markdown\n")
        file.write(string)
        file.write("\n```\n\n")
