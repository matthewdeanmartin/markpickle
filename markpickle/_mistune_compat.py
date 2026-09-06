"""Parse markdown to a stable AST shape regardless of the installed mistune.

Why this exists
---------------
Python 3.15 made :func:`re.Scanner` reject patterns containing capturing groups, which
breaks **all** of mistune 2.x::

    ValueError: Cannot use capturing groups in re.Scanner

So markpickle has to work with mistune 3.x on 3.15. But mistune 3 changed both the call
contract and the AST node shape:

============================  ==============================  ==============================
                              mistune 2.x                     mistune 3.x
============================  ==============================  ==============================
``parser.parse(text)``        returns ``list``                returns ``(list, state)``
text content                  ``{"type":"text","text":...}``  ``{"type":"text","raw":...}``
node attributes               ``{"type":"heading","level":1}``  ``{...,"attrs":{"level":1}}``
blank lines                   not emitted                     emits ``{"type":"blank_line"}``
============================  ==============================  ==============================

Rather than rewrite every AST consumer (18 call sites across four modules), this module
normalises mistune 3 output *back* to the mistune 2 shape at the single parse boundary.
That keeps the existing deserialisation logic — and its tests — untouched.

When the 2.x pin is finally dropped everywhere, this module can be deleted and the
consumers switched to the v3 shape directly.
"""

from __future__ import annotations

from typing import Any

import mistune

__all__ = ["parse_markdown"]

_NEWLINE = "\n"

_MISTUNE_MAJOR = int(mistune.__version__.split(".", maxsplit=1)[0])


def _inline_text(nodes: list[Any]) -> str:
    """Flatten an inline subtree to plain text, the way mistune 2 pre-flattened it."""
    parts: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        if "raw" in node:
            parts.append(str(node["raw"]))
        elif node.get("type") == "softbreak":
            # v3 splits hard/soft line breaks into their own nodes; v2 kept the newline
            # inside the surrounding text run.
            parts.append(_NEWLINE)
        elif isinstance(node.get("children"), list):
            parts.append(_inline_text(node["children"]))
    return "".join(parts)


def _normalize_node(node: dict[str, Any]) -> dict[str, Any] | None:
    """Rewrite one mistune 3 node into the mistune 2 shape.

    Returns ``None`` for nodes that mistune 2 never emitted, so the caller drops them.
    """
    node_type = node.get("type")
    if node_type == "blank_line":
        # mistune 2 simply did not produce these; downstream code counts on that.
        return None

    # mistune 2 emitted definition lists as FLAT nodes carrying inline text; mistune 3
    # nests the text under children and renamed def_list_header -> def_list_head.
    if node_type in ("def_list_head", "def_list_header"):
        return {"type": "def_list_header", "text": _inline_text(node.get("children") or [])}
    if node_type == "def_list_item":
        return {"type": "def_list_item", "text": _inline_text(node.get("children") or [])}

    attrs = node.get("attrs") or {}

    # v3 moved the target URL into attrs["url"] for both links and images, and pushed
    # an image's alt text down into children. v2 exposed link/src/alt/title flat.
    if node_type == "image":
        return {
            "type": "image",
            "src": attrs.get("url"),
            "alt": _inline_text(node.get("children") or []),
            "title": attrs.get("title"),
        }
    if node_type == "link":
        return {
            "type": "link",
            "link": attrs.get("url"),
            "children": _normalize(node.get("children") or []),
            "title": attrs.get("title"),
        }

    out: dict[str, Any] = {}
    for key, value in node.items():
        if key == "raw":
            # v3 renamed the text payload; v2 consumers read ["text"].
            out["text"] = value
        elif key == "attrs":
            # v3 nests level/url/etc under "attrs"; v2 had them at the top level.
            if isinstance(value, dict):
                out.update(value)
        elif key == "style":
            # v3-only metadata (e.g. atx vs setext headings); v2 had no equivalent.
            continue
        elif key == "children":
            if isinstance(value, list):
                out["children"] = _normalize(value)
            else:
                out["children"] = value
        else:
            out[key] = value
    return out


def _merge_text_runs(nodes: list[Any]) -> list[Any]:
    """Rejoin the text runs that mistune 3 splits on soft/hard line breaks.

    mistune 2 kept a multi-line paragraph as a single ``text`` node with embedded
    newlines. mistune 3 splits it into ``text`` / ``softbreak`` / ``text`` ... . Code
    that reads ``children[0]["text"]`` to get a paragraph's contents — as markpickle's
    table detection does — otherwise sees only the first line.
    """
    merged: list[Any] = []
    for node in nodes:
        is_text = isinstance(node, dict) and node.get("type") == "text" and "text" in node
        # Only softbreaks get folded back into the text run. mistune 2 emitted a
        # `linebreak` node for a markdown hard break (two trailing spaces) and left it
        # for downstream code to render as a space, so it must survive normalisation.
        is_break = isinstance(node, dict) and node.get("type") == "softbreak"
        if is_break:
            if merged and isinstance(merged[-1], dict) and merged[-1].get("type") == "text":
                merged[-1] = {**merged[-1], "text": merged[-1]["text"] + _NEWLINE}
            continue
        if is_text and merged and isinstance(merged[-1], dict) and merged[-1].get("type") == "text":
            merged[-1] = {**merged[-1], "text": merged[-1]["text"] + node["text"]}
            continue
        merged.append(node)
    return merged


def _normalize(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalise a list of nodes, dropping the ones mistune 2 never emitted."""
    result = []
    for node in nodes:
        if not isinstance(node, dict):
            result.append(node)
            continue
        normalized = _normalize_node(node)
        if normalized is not None:
            result.append(normalized)
    return _merge_text_runs(result)


def parse_markdown(string_value: str, plugins: list[str] | None = None) -> list[dict[str, Any]]:
    """Parse markdown into a mistune-2-shaped AST.

    Args:
        string_value: The markdown source.
        plugins: mistune plugin names; defaults to ``["def_list"]``.

    Returns:
        The AST as a list of nodes, in the mistune 2 shape, on any supported mistune.
    """
    if plugins is None:
        plugins = ["def_list"]
    parser = mistune.create_markdown(renderer="ast", plugins=plugins)
    result = parser.parse(string_value)

    # mistune 3's parse() returns (tokens, state); mistune 2's returned just the tokens.
    if isinstance(result, tuple):
        result = result[0]

    if _MISTUNE_MAJOR >= 3:
        return _normalize(result)
    return result
