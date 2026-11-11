from __future__ import annotations

import base64
import io

import markpickle
from markpickle.deserialize import extract_scalar, missing_top_key
from markpickle._mistune_compat import parse_markdown


def test_empty_document_uses_configured_empty_value():
    assert markpickle.loads("", markpickle.Config(empty_string_is="empty")) == "empty"


def test_object_hook_receives_wrapper_mapping_for_root_scalar():
    seen = []

    result = markpickle.loads("42", object_hook=lambda value: seen.append(value) or value)

    assert result == {None: 42}
    assert seen == [{None: 42}]


def test_object_hook_receives_header_mapping():
    result = markpickle.loads("# answer\n\n42\n", object_hook=lambda value: value)

    assert result == {"answer": 42}


def test_disabling_scalar_inference_preserves_numeric_text():
    assert extract_scalar("-12.5", markpickle.Config(infer_scalar_types=False)) == "-12.5"


def test_ordered_list_can_become_tuple():
    assert markpickle.loads("1. alpha\n2. beta\n", markpickle.Config(ordered_list_as_tuple=True)) == (
        "alpha",
        "beta",
    )


def test_root_image_data_url_decodes_to_bytes():
    encoded = base64.b64encode(b"payload").decode("ascii")

    assert markpickle.loads(f"![alt](data:application/octet-stream;base64,{encoded})") == b"payload"


def test_load_all_skips_empty_documents_between_separators():
    documents = list(markpickle.loads_all("1\n---\n---\n2\n---\n"))

    assert documents == [1, 2]


def test_missing_top_key_ignores_blank_lines_and_whitespace_paragraphs():
    tokens = parse_markdown("\n   \n# Heading\n")

    assert missing_top_key(tokens) is False


def test_load_stream_dedents_indented_markdown():
    result = markpickle.load(io.StringIO("    # title\n\n    value\n"))

    assert result == {"title": "value"}
