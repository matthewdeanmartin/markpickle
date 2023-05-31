import markpickle

EXAMPLE = """# Description

This is an example file

# Authors

* Nate Vack
* Vendor Packages
    * docopt
    * CommonMark-py

# Versions

## Version 1

Here's something about Version 1; I said "Hooray!"

## Version 2

Here's something about Version 2"""


def test_dictionary_of_lists():
    marks = EXAMPLE
    config = markpickle.Config()
    # config.root = "Top level heading"
    result = markpickle.loads(marks, config)
    assert "Description" in result
    assert "Authors" in result
    assert "Versions" in result
    assert result["Description"] == "This is an example file"
    assert result["Authors"] == ["Nate Vack", "Vendor Packages", ["docopt", "CommonMark-py"]]
    assert result["Versions"] == {
        "Version 1": 'Here\'s something about Version 1; I said "Hooray!"',
        "Version 2": "Here's something about Version 2",
    }
