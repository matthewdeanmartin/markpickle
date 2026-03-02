from markpickle import loads


def test_empty_header():
    """Test that a header with no content doesn't raise an exception."""
    result = loads("# Hello World")
    assert result == {"Hello World": None}


def test_empty_header_with_content_after():
    """Test that a header followed by content works normally."""
    result = loads("# Hello World\n\nSome content here")
    assert result == {"Hello World": "Some content here"}


def test_multiple_empty_headers():
    """Test multiple headers with no content."""
    result = loads("# Header1\n# Header2\n# Header3")
    assert result == {"Header1": None, "Header2": None, "Header3": None}


def test_mixed_empty_and_populated_headers():
    """Test mix of empty and populated headers."""
    result = loads("# Empty\n# With Content\nvalue\n")
    assert result == {"Empty": None, "With Content": "value"}
