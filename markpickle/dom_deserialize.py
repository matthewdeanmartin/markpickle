"""
DOM-style Markdown deserializer.

Produces a Python structure where every key is an HTML tag name, mirroring
the document's logical structure rather than extracting data values.

Example
-------
    >>> loads_as_dom("# Title\\n\\nHello world.\\n")
    [{'tag': 'h1', 'text': 'Title'}, {'tag': 'p', 'text': 'Hello world.'}]

The result is a list of DOM nodes. Each node is a dict with at least a
``'tag'`` key. Additional keys depend on the tag type.

Supported tags
--------------
    h1 … h6   {'tag': 'h1', 'text': '...'}
    p         {'tag': 'p', 'text': '...'}
    ul        {'tag': 'ul', 'items': ['...', ...]}
    ol        {'tag': 'ol', 'items': ['...', ...]}
    code      {'tag': 'code', 'text': '...', 'language': 'python' | None}
    table     {'tag': 'table', 'headers': [...], 'rows': [[...], ...]}
    dl        {'tag': 'dl', 'items': [{'term': '...', 'definition': '...'}, ...]}
    hr        {'tag': 'hr'}
    blockquote {'tag': 'blockquote', 'text': '...'}
"""
from __future__ import annotations

import io
from typing import Any, Optional

import mistune

# ---------------------------------------------------------------------------
# Internal text extraction
# ---------------------------------------------------------------------------


def _text_from_children(children: list[dict[str, Any]]) -> str:
    """Recursively flatten inline token children to plain text."""
    parts: list[str] = []
    for child in children:
        if "text" in child:
            parts.append(child["text"])
        elif "children" in child:
            parts.append(_text_from_children(child["children"]))
    return "".join(parts)


def _inline_text(token: dict[str, Any]) -> str:
    if "text" in token:
        return token["text"]
    if "children" in token:
        return _text_from_children(token["children"])
    return ""


# ---------------------------------------------------------------------------
# List item extraction
# ---------------------------------------------------------------------------


def _list_items(list_token: dict[str, Any]) -> list[Any]:
    """Extract items from a list token, recursing into nested lists."""
    items: list[Any] = []
    for item in list_token.get("children", []):
        if item["type"] != "list_item":
            continue
        item_parts: list[Any] = []
        for child in item.get("children", []):
            if child["type"] in ("block_text", "paragraph"):
                item_parts.append(_inline_text(child))
            elif child["type"] == "list":
                nested_tag = "ol" if child.get("ordered") else "ul"
                item_parts.append(
                    {
                        "tag": nested_tag,
                        "items": _list_items(child),
                    }
                )
        if len(item_parts) == 1:
            items.append(item_parts[0])
        else:
            items.extend(item_parts)
    return items


# ---------------------------------------------------------------------------
# Table extraction
# ---------------------------------------------------------------------------


def _parse_table_text(text: str) -> Optional[dict[str, Any]]:
    """Parse a pipe-delimited table from a paragraph text node."""
    lines = [ln.strip() for ln in text.strip().splitlines()]
    lines = [ln for ln in lines if set(ln) - set("| :-")]
    if len(lines) < 1:
        return None
    rows = []
    for line in lines:
        # Strip leading/trailing | then split
        stripped = line.strip().strip("|")
        cells = [c.strip() for c in stripped.split("|")]
        rows.append(cells)
    if not rows:
        return None
    headers = rows[0]
    data_rows = rows[1:]
    return {"tag": "table", "headers": headers, "rows": data_rows}


# ---------------------------------------------------------------------------
# Token → DOM node
# ---------------------------------------------------------------------------


def _token_to_node(token: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Convert a single top-level mistune token to a DOM node dict."""
    t = token["type"]

    if t == "heading":
        level = token.get("level", 1)
        return {"tag": f"h{level}", "text": _inline_text(token)}

    if t == "paragraph":
        children = token.get("children", [])
        # Single text child that looks like a table
        if len(children) == 1 and children[0]["type"] == "text":
            raw = children[0]["text"]
            if raw.count("|") >= 2:
                table = _parse_table_text(raw)
                if table:
                    return table
        return {"tag": "p", "text": _inline_text(token)}

    if t == "list":
        tag = "ol" if token.get("ordered") else "ul"
        return {"tag": tag, "items": _list_items(token)}

    if t == "block_code":
        return {
            "tag": "code",
            "text": token.get("text", "").rstrip("\n"),
            "language": token.get("info") or None,
        }

    if t == "def_list":
        pairs: list[dict[str, str]] = []
        children = token.get("children", [])
        i = 0
        while i < len(children):
            if (
                children[i]["type"] == "def_list_header"
                and i + 1 < len(children)
                and children[i + 1]["type"] == "def_list_item"
            ):
                pairs.append(
                    {
                        "term": children[i].get("text", ""),
                        "definition": children[i + 1].get("text", ""),
                    }
                )
                i += 2
            else:
                i += 1
        return {"tag": "dl", "items": pairs}

    if t == "thematic_break":
        return {"tag": "hr"}

    if t == "block_quote":
        inner = [_token_to_node(c) for c in token.get("children", [])]
        inner_filtered = [n for n in inner if n is not None]
        return {"tag": "blockquote", "children": inner_filtered}

    if t == "newline":
        return None  # skip whitespace nodes

    # Fallback: return a generic node with the raw token type
    return {"tag": t, "raw": token}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def loads_as_dom(text: str) -> list[dict[str, Any]]:
    """
    Parse a Markdown string into a list of DOM-style node dicts.

    Each node has at minimum a ``'tag'`` key (e.g. ``'h1'``, ``'p'``,
    ``'ul'``, ``'table'``, ``'code'``).

    >>> loads_as_dom("# Hello\\n\\nWorld.\\n")
    [{'tag': 'h1', 'text': 'Hello'}, {'tag': 'p', 'text': 'World.'}]
    """
    parser = mistune.create_markdown(renderer="ast", plugins=["def_list"])
    tokens: list[dict[str, Any]] = parser.parse(text)
    nodes: list[dict[str, Any]] = []
    for token in tokens:
        node = _token_to_node(token)
        if node is not None:
            nodes.append(node)
    return nodes


def load_as_dom(stream: io.TextIOBase) -> list[dict[str, Any]]:
    """
    Parse a Markdown stream into a list of DOM-style node dicts.

    >>> import io
    >>> load_as_dom(io.StringIO("# Hi\\n\\nThere.\\n"))
    [{'tag': 'h1', 'text': 'Hi'}, {'tag': 'p', 'text': 'There.'}]
    """
    return loads_as_dom(stream.read())
