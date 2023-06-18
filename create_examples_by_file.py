import markpickle
import mdformat
import difflib


def compare_files(file1_path, file2_path):
    # Created by ChatGPT
    with open(file1_path) as file1, open(file2_path) as file2:
        lines1 = file1.readlines()
        lines2 = file2.readlines()

    diff = difflib.unified_diff(lines1, lines2, fromfile=file1_path, tofile=file2_path)

    for line in diff:
        print(line, end="")


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

config = markpickle.Config()
config.serialize_force_final_newline = True

for key, value in EXAMPLES.items():
    name = f"docs/individual/{key}.md"

    with open(name, "w", encoding="utf-8") as file:
        string = markpickle.dumps(value, config)
        if string == "None":
            raise TypeError(f"Lost a serialization for {value}")
        file.write(string)
    name_formatted = f"docs/individual/{key}_formatted.md"
    with open(name_formatted, "w", encoding="utf-8") as file:
        file.write(mdformat.text(string).replace("_" * 70, "---"))
    compare_files(name, name_formatted)


for key, value in MULTI.items():
    name = f"docs/individual/{key}_multi.md"
    with open(name, "w", encoding="utf-8") as file:
        string = markpickle.dumps_all(value, config)
        if string == "None":
            raise TypeError(f"Lost a serialization for {value}")
        file.write(string)
    name_formatted = f"docs/individual/{key}_multi_formated.md"
    with open(name_formatted, "w", encoding="utf-8") as file:
        file.write(mdformat.text(string).replace("_" * 70, "---"))
    compare_files(name, name_formatted)


# formatting fails on square brackets for data urls
# # is always followed by line break & paragraph always has linebreak following
# No leading space on table
