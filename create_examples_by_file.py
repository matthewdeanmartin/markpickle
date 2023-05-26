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

for key, value in EXAMPLES.items():
    with open(f"docs/individual/{key}.md", "w", encoding="utf-8") as file:
        string = markpickle.dumps(value)
        if string == "None":
            raise TypeError(f"Lost a serialization for {value}")
        file.write(string)


for key, value in MULTI.items():
    with open(f"docs/individual/{key}_multi.md", "w", encoding="utf-8") as file:
        string = markpickle.dumps_all(value)
        if string == "None":
            raise TypeError(f"Lost a serialization for {value}")
        file.write(string)
