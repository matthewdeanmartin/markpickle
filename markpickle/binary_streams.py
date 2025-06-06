"""
Add support for binary streams via images and data URLs
"""

import base64
import io
from typing import Any, Optional

from PIL import Image

from markpickle.config_class import Config


def bytes_to_markdown(key: Optional[str], value: bytes, config: Config) -> str:
    """
    Convert bytes to markdown image
    """
    base64_data = base64.b64encode(value).decode("utf-8")
    key = key or "bytes"
    mime_type = config.serialize_bytes_mime_type
    return f"![{key}](data:{mime_type};base64,{base64_data})"


# Can't correctly type the return value because Pillow's Image module acts like module and class.
def extract_bytes(src: str, config: Config) -> Any:
    """
    Extract bytes from a markdown image or pillow Image
    """
    if "," not in src:
        return None

    # Extract the mime type and data portion from the src
    try:
        mime_type = src.split(",")[0].split(":")[1].split(";")[0]
    except IndexError:
        mime_type = "application/octet-stream"

    # Extract the Base64-encoded data portion from the data URL
    try:
        base64_data = src.split(",")[1]
    except IndexError:
        return None

    # Decode the Base64 string into bytes
    image_bytes = base64.b64decode(base64_data)

    if config.serialize_images_to_pillow and mime_type == "image/png":
        # Create an in-memory stream from the image bytes
        stream = io.BytesIO(image_bytes)

        # Open the image using PIL/Pillow
        image = Image.open(stream)
        return image
    return image_bytes
