import markpickle


def test_simple_bytes():
    marks = "![data](data:image/png;base64,aGVsbG8gd29ybGQ=)"
    config = markpickle.Config()
    # config.root = "Top level heading"
    result = markpickle.loads(marks, config)
    assert result == b"hello world"


def test_bytes_lists():
    list_of_binary = [b"hello world", b"hello universe"]
    config = markpickle.Config()
    result = markpickle.dumps(list_of_binary, config)
    assert (
        result == "- ![bytes](data:application/octet-stream;base64,aGVsbG8gd29ybGQ=)\n"
        "- ![bytes](data:application/octet-stream;base64,aGVsbG8gdW5pdmVyc2U=)"
    )


def test_bytes_dict():
    dictionaries_of_binary = {"animal": b"hello world", "name": b"hello universe"}
    config = markpickle.Config()
    result = markpickle.dumps(dictionaries_of_binary, config)
    assert result == (
        "# animal\n"
        "![bytes](data:application/octet-stream;base64,aGVsbG8gd29ybGQ=)\n"
        "# name\n"
        "![bytes](data:application/octet-stream;base64,aGVsbG8gdW5pdmVyc2U=)"
    )
