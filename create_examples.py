import markpickle

EXAMPLES = {
    "scalar": 6,
    "binary": b"hello world",
    "list of scalars": [1, 2, 3],
    "list of binary": [b"hello world", b"hello universe"],
    "list of dictionaries": [{"animal": "cat", "name": "Frisky"}, {"animal": "dog", "name": "Fido"}],
    "dictionaries of strings": {"animal": "cat", "name": "Frisky"},
    "dictionaries of binary": {"animal": b"hello world", "name": b"hello universe"},
    "dictionary of lists": {
        "ages": [24, 59, 45],
        "countries": ["US", "Canada", "Iceland"],
    },
    "dictionary of dictionaries": {
        "Best Cat": {"animal": "cat", "name": "Frisky"},
        "Best Dog": {"animal": "dog", "name": "Fido"},
    },
}

MULTI = {"two scalar documents": ["abc", 123], "two dictionary documents": [{"cat": "Frisky"}, {"dog": "Fido"}]}

with open("docs/examples.md", "w", encoding="utf-8") as file:
    file.write("# Examples\n\n")
    file.write("## Single Documents\n\n")
    for key, value in EXAMPLES.items():
        string = markpickle.dumps(value)
        if string == "None":
            raise TypeError(f"Lost a serialization for {value}")
        file.write(f"### {key}\n")
        file.write("```python\n")
        file.write(repr(value))
        file.write("\n```\n\n")

        file.write("```markdown\n")
        file.write(string)
        file.write("\n```\n\n")

    file.write("## Examples of multiple document in one file\n\n")
    for key, value in MULTI.items():
        string = markpickle.dumps_all(value)
        if string == "None":
            raise TypeError(f"Lost a serialization for {value}")
        file.write(f"### {key}\n")
        file.write("```python\n")
        file.write(repr(value))
        file.write("\n```\n\n")

        file.write("```markdown\n")
        file.write(string)
        file.write("\n```\n\n")
