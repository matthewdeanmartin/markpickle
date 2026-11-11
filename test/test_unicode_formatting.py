from markpickle.unicode_formatting import convert_markup_to_terminal


def test_converts_bold_and_italic_markup_to_ansi_sequences():
    assert convert_markup_to_terminal("plain __bold__ and *italic*") == (
        "plain \033[1mbold\033[0m and \033[3mitalic\033[0m"
    )


def test_leaves_unmarked_text_and_underline_syntax_unchanged():
    text = "plain text --underline--"

    assert convert_markup_to_terminal(text) == text


def test_converts_multiple_markup_runs():
    assert convert_markup_to_terminal("*one* then *two*") == "\033[3mone\033[0m then \033[3mtwo\033[0m"


def test_unmatched_delimiters_remain_literal():
    assert convert_markup_to_terminal("__bold and *italic") == "__bold and *italic"
