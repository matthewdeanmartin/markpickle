"""
AST-based markdown validation for round-trip safety.

Walks the mistune AST to identify constructs that are not preserved
during markpickle serialization/deserialization round-trips.
"""

from typing import Any, Optional

import mistune


def _check_inline_tokens(children: list[dict[str, Any]], context: str, issues: list[str]) -> None:
    """Walk inline tokens and flag unsupported constructs."""
    for child in children:
        typ = child.get("type", "")
        if typ == "image":
            issues.append(f"image found in {context}: inline images are not supported and will be lost")
        elif typ == "link":
            issues.append(f"link found in {context}: links lose their text label (only the URL is preserved)")
        elif typ in ("strong", "emphasis", "codespan"):
            issues.append(f"{typ} formatting found in {context}: inline formatting is stripped during round-trip")
        # Recurse into nested inline children (e.g. strong containing emphasis)
        if "children" in child:
            _check_inline_tokens(child["children"], context, issues)


def _check_paragraph(token: dict[str, Any], issues: list[str]) -> None:
    """Inspect a paragraph token for problematic inline content."""
    children = token.get("children", [])
    if not children:
        return

    non_text_types = [c.get("type", "") for c in children if c.get("type", "") != "text"]

    # Mixed paragraph: multiple children of different types
    if len(children) > 1 and non_text_types:
        issues.append(
            "mixed paragraph content found: paragraph contains multiple children of different "
            "types and will become a tuple rather than a string"
        )

    _check_inline_tokens(children, "paragraph", issues)


def _has_top_level_heading(tokens: list[dict[str, Any]]) -> bool:
    """Return True if the first non-empty token is a heading."""
    for token in tokens:
        if token.get("type") in ("heading", "blank_line"):
            if token.get("type") == "heading":
                return True
            # skip blank lines at top
            continue
        # First substantive non-heading token
        return False
    return False


def _has_any_heading(tokens: list[dict[str, Any]]) -> bool:
    """Return True if any token in the list is a heading."""
    for token in tokens:
        if token.get("type") == "heading":
            return True
    return False


def validate_markdown(text: str, _config: Optional[Any] = None) -> list[str]:
    """
    Walk a mistune AST and return a list of issue strings describing constructs
    that won't round-trip cleanly through markpickle.

    Parameters
    ----------
    text:
        Raw markdown text to analyse.
    _config:
        Unused; reserved for future use so callers can pass a Config object.

    Returns
    -------
    list[str]
        Human-readable issue descriptions. Empty list means no problems found.
    """
    if not text or not text.strip():
        return []

    parser = mistune.create_markdown(renderer="ast", plugins=["def_list"])
    tokens: list[dict[str, Any]] = parser(text)  # type: ignore[assignment]

    if not tokens:
        return []

    issues: list[str] = []

    # Check for headings buried inside a document that has no top-level heading
    if not _has_top_level_heading(tokens) and _has_any_heading(tokens):
        issues.append(
            "document has no top-level heading but contains headings further down: "
            "the top key used by markpickle will be missing"
        )

    for token in tokens:
        typ = token.get("type", "")

        if typ == "block_quote":
            issues.append("blockquote found: blockquotes have no serialization support and will be lost")

        elif typ == "thematic_break":
            issues.append(
                "thematic_break (horizontal rule) found: horizontal rules are not serialized "
                "as a value and will be lost"
            )

        elif typ == "block_html":
            issues.append("block_html found: raw HTML blocks are not handled and will be lost")

        elif typ == "table":
            issues.append(
                "table token found: native mistune tables may not round-trip correctly without tabulate support"
            )

        elif typ == "strikethrough":
            issues.append("strikethrough found: strikethrough formatting is not preserved during round-trip")

        elif typ == "paragraph":
            _check_paragraph(token, issues)

    return issues
