from markpickle.unicode_text import (
    from_bold,
    from_italic,
    from_monospace,
    has_unicode_formatting,
    markdown_inline_to_unicode,
    to_bold,
    to_italic,
    to_monospace,
    unicode_to_markdown,
)


def test_ascii_unicode_style_conversions_roundtrip():
    assert from_bold(to_bold("Az09!")) == "Az09!"
    assert from_italic(to_italic("Ahz!")) == "Ahz!"
    assert from_monospace(to_monospace("Az09!")) == "Az09!"


def test_markdown_inline_formatting_converts_bold_italic_and_code():
    converted = markdown_inline_to_unicode("**Bold 42** *italic* `code9`")

    assert converted == to_bold("Bold 42") + " " + to_italic("italic") + " " + to_monospace("code9")
    assert has_unicode_formatting(converted)
    assert not has_unicode_formatting("plain text")


def test_unicode_runs_convert_back_to_markdown_and_preserve_plain_text():
    text = "prefix " + to_bold("Bold") + " " + to_italic("italic") + " " + to_monospace("code") + " suffix"

    assert unicode_to_markdown(text) == "prefix **Bold** *italic* `code` suffix"
