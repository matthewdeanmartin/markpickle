"""
Random markdown generator — produces markpickle-compatible markdown snippets.

Only generates constructs that markpickle can round-trip:
  scalars, lists (unordered/ordered), nested lists, dicts (ATX headers),
  tables, definition lists, code blocks, nested dicts.
"""

from __future__ import annotations

import random
import string
from typing import Any

# ---------------------------------------------------------------------------
# Low-level value generators
# ---------------------------------------------------------------------------


def _rand_word() -> str:
    length = random.randint(3, 10)
    return "".join(random.choices(string.ascii_lowercase, k=length))


def _rand_words(n: int = 3) -> str:
    return " ".join(_rand_word() for _ in range(n))


def _rand_int() -> int:
    return random.randint(-999, 9999)


def _rand_float() -> float:
    return round(random.uniform(-100, 100), 2)


def _rand_bool() -> bool:
    return random.choice([True, False])


def _rand_scalar_str() -> str:
    """Return a scalar that survives round-trip as its type."""
    kind = random.choice(["word", "int", "float", "bool", "none"])
    if kind == "word":
        return _rand_words(random.randint(1, 4))
    if kind == "int":
        return str(_rand_int())
    if kind == "float":
        return str(_rand_float())
    if kind == "bool":
        return random.choice(["True", "False"])
    return "None"


def _rand_identifier() -> str:
    """A word suitable for a dict key / heading."""
    return _rand_word().capitalize()


# ---------------------------------------------------------------------------
# Block generators  (each returns a markdown string)
# ---------------------------------------------------------------------------


def _scalar_block() -> str:
    """A lone paragraph — deserialises to a scalar."""
    return _rand_scalar_str() + "\n"


def _unordered_list_block(depth: int = 0) -> str:
    n = random.randint(2, 5)
    indent = "  " * depth
    lines = []
    for _ in range(n):
        if depth < 2 and random.random() < 0.2:
            # nested list
            lines.append(f"{indent}- {_rand_word()}")
            nested = _unordered_list_block(depth + 1)
            for sub in nested.splitlines():
                lines.append("  " + sub)
        else:
            lines.append(f"{indent}- {_rand_scalar_str()}")
    return "\n".join(lines) + "\n"


def _ordered_list_block() -> str:
    n = random.randint(2, 5)
    lines = [f"{i + 1}. {_rand_scalar_str()}" for i in range(n)]
    return "\n".join(lines) + "\n"


def _code_block() -> str:
    lang = random.choice(["python", "bash", "json", ""])
    body_lines = [
        f"{'    ' if random.random() < 0.3 else ''}{_rand_word()} = {_rand_int()}" for _ in range(random.randint(1, 4))
    ]
    body = "\n".join(body_lines)
    return f"```{lang}\n{body}\n```\n"


def _table_block() -> str:
    n_cols = random.randint(2, 4)
    n_rows = random.randint(1, 4)
    headers = [_rand_identifier() for _ in range(n_cols)]
    sep = ["---"] * n_cols
    rows = [[str(_rand_int()) for _ in range(n_cols)] for _ in range(n_rows)]

    def row_str(cells):
        return "| " + " | ".join(cells) + " |"

    lines = [row_str(headers), row_str(sep)] + [row_str(r) for r in rows]
    return "\n".join(lines) + "\n"


def _def_list_block() -> str:
    n = random.randint(1, 3)
    lines = []
    for _ in range(n):
        lines.append(_rand_identifier())
        lines.append(f":   {_rand_words(2)}")
        lines.append("")
    return "\n".join(lines)


def _dict_block(depth: int = 1, max_depth: int = 2) -> str:
    """ATX-header dict with random values under each key."""
    n_keys = random.randint(2, 4)
    hashes = "#" * depth
    parts = []
    for _ in range(n_keys):
        key = _rand_identifier()
        parts.append(f"{hashes} {key}\n")
        if depth < max_depth and random.random() < 0.3:
            parts.append(_dict_block(depth + 1, max_depth))
        else:
            value_kind = random.choice(["scalar", "list", "ordered"])
            if value_kind == "scalar":
                parts.append(_scalar_block() + "\n")
            elif value_kind == "list":
                parts.append(_unordered_list_block() + "\n")
            else:
                parts.append(_ordered_list_block() + "\n")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Top-level scenarios
# ---------------------------------------------------------------------------

_SCENARIOS: list[tuple[str, Any]] = [
    ("scalar", _scalar_block),
    ("unordered list", _unordered_list_block),
    ("ordered list", _ordered_list_block),
    ("code block", _code_block),
    ("table", _table_block),
    ("definition list", _def_list_block),
    ("dict (ATX headers)", _dict_block),
]


def random_markdown() -> tuple[str, str]:
    """
    Return ``(label, markdown_text)`` for a randomly chosen supported scenario.

    The label names the scenario (e.g. ``"table"``).
    """
    label, fn = random.choice(_SCENARIOS)
    return label, fn()
