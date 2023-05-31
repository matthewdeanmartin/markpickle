import markpickle

EXAMPLES = {
    "scalar": 6,
    "binary": b"hello world",
    "list of scalars": [1, 2, 3],
    "list of scalars and lists": [1, 2, 3, ["a", "b", "c"]],
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
    }
    # Markdown to python is fine, but python to markdown isn't sensible!
    # "complex nested": {'Description': 'This is an example file',
    #                    'Authors': ['Nate Vack', 'Vendor Packages', ['docopt', 'CommonMark-py']],
    #                    'Versions': {'Version 1': 'Here\'s something about Version 1; I said "Hooray!"',
    #                                 'Version 2': "Here's something about Version 2"}}
}

MULTI = {"two scalar documents": ["abc", 123], "two dictionary documents": [{"cat": "Frisky"}, {"dog": "Fido"}]}

with open("docs/examples.md", "w", encoding="utf-8") as file:
    file.write("# Examples\n\n")
    file.write("## Single Documents\n\n")
    for key, value in EXAMPLES.items():
        string = markpickle.dumps(value)
        try:
            roundtrip = markpickle.loads(string)
            roundtripable = value == roundtrip
        except NotImplementedError:
            roundtripable = False

        if string == "None":
            raise TypeError(f"Lost a serialization for {value}")
        file.write(f"### {key}\n")
        file.write("```python\n")
        file.write(repr(value))
        file.write("\n```\n\n")

        file.write("```markdown\n")
        file.write(string)
        file.write("\n```\n\n")
        file.write(f"Roundtripable? {'Yes' if roundtripable else 'No'}\n\n")

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
