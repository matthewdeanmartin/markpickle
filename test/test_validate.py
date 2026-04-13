"""
Tests for markpickle.validate.validate_markdown.
"""

from __future__ import annotations

from markpickle.validate import validate_markdown

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_issue_containing(issues: list[str], keyword: str) -> bool:
    return any(keyword in issue for issue in issues)


# ---------------------------------------------------------------------------
# Empty / trivially valid documents
# ---------------------------------------------------------------------------


def test_empty_document_returns_no_issues() -> None:
    assert validate_markdown("") == []


def test_whitespace_only_document_returns_no_issues() -> None:
    assert validate_markdown("   \n\n  ") == []


# ---------------------------------------------------------------------------
# Supported constructs — should return no issues
# ---------------------------------------------------------------------------


def test_simple_supported_document_returns_no_issues() -> None:
    md = "# Title\n\nSome plain text.\n"
    assert validate_markdown(md) == []


def test_supported_heading_returns_no_issues() -> None:
    md = "# Top heading\n\n## Second level\n"
    assert validate_markdown(md) == []


def test_supported_unordered_list_returns_no_issues() -> None:
    md = "# Things\n\n- apple\n- banana\n- cherry\n"
    assert validate_markdown(md) == []


def test_supported_ordered_list_returns_no_issues() -> None:
    md = "# Steps\n\n1. First\n2. Second\n3. Third\n"
    assert validate_markdown(md) == []


def test_supported_code_block_returns_no_issues() -> None:
    md = "# Code\n\n```python\nprint('hello')\n```\n"
    assert validate_markdown(md) == []


def test_supported_definition_list_returns_no_issues() -> None:
    md = "# Glossary\n\nterm\n:   definition\n"
    assert validate_markdown(md) == []


# ---------------------------------------------------------------------------
# Unsupported constructs — should flag issues
# ---------------------------------------------------------------------------


def test_blockquote_returns_issue() -> None:
    md = "# Title\n\n> This is a blockquote.\n"
    issues = validate_markdown(md)
    assert issues, "Expected at least one issue for blockquote"
    assert _has_issue_containing(issues, "blockquote")


def test_thematic_break_returns_issue() -> None:
    md = "# Title\n\nSome text.\n\n---\n\nMore text.\n"
    issues = validate_markdown(md)
    assert issues, "Expected at least one issue for thematic break"
    assert _has_issue_containing(issues, "thematic_break")


def test_link_in_paragraph_returns_issue() -> None:
    md = "# Title\n\nCheck out [this link](https://example.com) for details.\n"
    issues = validate_markdown(md)
    assert issues, "Expected at least one issue for link"
    assert _has_issue_containing(issues, "link")


def test_inline_image_returns_issue() -> None:
    md = "# Title\n\nHere is an ![alt text](image.png) inline.\n"
    issues = validate_markdown(md)
    assert issues, "Expected at least one issue for image"
    assert _has_issue_containing(issues, "image")


def test_block_html_returns_issue() -> None:
    md = "# Title\n\n<div>raw html block</div>\n"
    issues = validate_markdown(md)
    assert issues, "Expected at least one issue for block_html"
    assert _has_issue_containing(issues, "block_html")


def test_strong_formatting_returns_issue() -> None:
    md = "# Title\n\nThis is **bold** text.\n"
    issues = validate_markdown(md)
    assert issues, "Expected at least one issue for strong formatting"
    assert _has_issue_containing(issues, "strong")


def test_emphasis_formatting_returns_issue() -> None:
    md = "# Title\n\nThis is *italic* text.\n"
    issues = validate_markdown(md)
    assert issues, "Expected at least one issue for emphasis formatting"
    assert _has_issue_containing(issues, "emphasis")


def test_codespan_formatting_returns_issue() -> None:
    md = "# Title\n\nUse `some_function()` here.\n"
    issues = validate_markdown(md)
    assert issues, "Expected at least one issue for codespan formatting"
    assert _has_issue_containing(issues, "codespan")


def test_missing_top_heading_with_buried_headings_returns_issue() -> None:
    # Document starts with a paragraph, then has a heading further down.
    md = "Some intro text.\n\n# Heading buried below\n\nMore text.\n"
    issues = validate_markdown(md)
    assert issues, "Expected an issue for missing top-level heading"
    assert _has_issue_containing(issues, "top-level heading")


# ---------------------------------------------------------------------------
# Config argument is accepted without error
# ---------------------------------------------------------------------------


def test_accepts_config_kwarg() -> None:
    """validate_markdown should accept a config= argument without raising."""
    from markpickle.config_class import Config

    md = "# Title\n\nHello.\n"
    issues = validate_markdown(md, config=Config())
    assert issues == []
