"""
Convert bold and italic to terminal formatting.

One solution for handling text with formatting markup in strings.
"""

import re


def convert_markup_to_terminal(markdown: str):
    """Convert bold and italic to terminal formatting."""
    # Convert bold markup
    text = re.sub(r"__(.*?)__", r"\033[1m\g<1>\033[0m", markdown)

    # Convert italic markup
    text = re.sub(r"\*(.*?)\*", r"\033[3m\g<1>\033[0m", text)

    # not a real thing?
    # Convert underline markup
    # text = re.sub(r'--(.*?)--', r'\033[4m\g<1>\033[0m', text)

    return text


if __name__ == "__main__":

    def run() -> None:
        text = "Some text in __bold__, *italic*, and --underline--"
        converted_text = convert_markup_to_terminal(text)
        print(converted_text)

    run()
