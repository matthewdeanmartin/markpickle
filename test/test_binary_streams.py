from __future__ import annotations

import base64
import io

from unittest.mock import patch

import pytest

from markpickle.binary_streams import bytes_to_markdown, extract_bytes
from markpickle.config_class import Config


def test_bytes_to_markdown_uses_default_alt_text_and_configured_mime_type():
    config = Config(serialize_bytes_mime_type="application/octet-stream")

    assert bytes_to_markdown(None, b"hello", config) == (
        "![bytes](data:application/octet-stream;base64,aGVsbG8=)"
    )


def test_bytes_to_markdown_preserves_explicit_alt_text():
    assert bytes_to_markdown("cover", b"", Config()) == "![cover](data:image/png;base64,)"


@pytest.mark.parametrize("src", ["", "not a data URL", "prefix:abc"])
def test_extract_bytes_without_data_separator_returns_none(src):
    assert extract_bytes(src, Config()) is None


def test_extract_bytes_returns_decoded_payload_without_pillow_conversion():
    payload = b"image payload"
    src = "data:image/png;base64," + base64.b64encode(payload).decode("ascii")

    assert extract_bytes(src, Config()) == payload


def test_extract_bytes_falls_back_to_octet_stream_when_header_is_malformed():
    payload = b"raw"
    src = "malformed," + base64.b64encode(payload).decode("ascii")

    assert extract_bytes(src, Config()) == payload


def test_extract_bytes_opens_png_as_pillow_image_when_requested():
    image_module = pytest.importorskip("PIL.Image")
    image = image_module.new("RGB", (2, 3), color="red")
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    src = "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode("ascii")

    result = extract_bytes(src, Config(serialize_images_to_pillow=True))

    assert isinstance(result, image_module.Image)
    assert result.size == (2, 3)
    assert result.getpixel((0, 0)) == (255, 0, 0)


def test_extract_bytes_does_not_open_non_png_as_pillow_image():
    payload = b"not an image"
    src = "data:image/jpeg;base64," + base64.b64encode(payload).decode("ascii")

    assert extract_bytes(src, Config(serialize_images_to_pillow=True)) == payload


def test_extract_bytes_explains_optional_pillow_dependency():
    payload = b"png bytes"
    src = "data:image/png;base64," + base64.b64encode(payload).decode("ascii")

    with patch.dict("sys.modules", {"PIL": None}):
        with pytest.raises(ImportError, match=r"pip install markpickle\[images\]"):
            extract_bytes(src, Config(serialize_images_to_pillow=True))
