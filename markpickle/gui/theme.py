"""
Catppuccin Mocha dark palette + shared widget helpers.
"""

# ---------------------------------------------------------------------------
# Catppuccin Mocha palette
# ---------------------------------------------------------------------------

BASE = "#1e1e2e"  # window / panel background
MANTLE = "#181825"  # slightly darker — sidebar bg
CRUST = "#11111b"  # deepest — borders / separators
SURFACE0 = "#313244"  # raised surface (inactive tab, text bg)
SURFACE1 = "#45475a"  # slightly lighter surface
SURFACE2 = "#585b70"  # muted borders
OVERLAY0 = "#6c7086"  # disabled / placeholder text
OVERLAY2 = "#9399b2"  # secondary text
TEXT = "#cdd6f4"  # primary text
SUBTEXT1 = "#bac2de"  # secondary readable text
BLUE = "#89b4fa"  # accent / active tab highlight
LAVENDER = "#b4befe"  # secondary accent
GREEN = "#a6e3a1"  # success
RED = "#f38ba8"  # error / warning
YELLOW = "#f9e2af"  # warning
PEACH = "#fab387"  # info / highlight
MAUVE = "#cba6f7"  # heading colour


# ---------------------------------------------------------------------------
# Font names — caller can override
# ---------------------------------------------------------------------------

FONT_MONO = ("Consolas", 11)
FONT_UI = ("Segoe UI", 10)
FONT_UI_BOLD = ("Segoe UI", 10, "bold")
FONT_HEADING = ("Segoe UI", 12, "bold")
FONT_SMALL = ("Segoe UI", 9)


# ---------------------------------------------------------------------------
# Shared style dict helpers
# ---------------------------------------------------------------------------


def text_area_kw() -> dict:
    """Keyword args for a plain Text widget (editor/output)."""
    return {
        "bg": SURFACE0,
        "fg": TEXT,
        "insertbackground": TEXT,
        "selectbackground": BLUE,
        "selectforeground": BASE,
        "relief": "flat",
        "font": FONT_MONO,
        "padx": 6,
        "pady": 4,
    }


def label_kw() -> dict:
    """Keyword args for a standard Label."""
    return {"bg": BASE, "fg": TEXT, "font": FONT_UI}


def heading_kw() -> dict:
    """Keyword args for a heading Label."""
    return {"bg": BASE, "fg": MAUVE, "font": FONT_HEADING}


def button_kw(active: bool = False) -> dict:
    """Keyword args for a standard Button."""
    return {
        "bg": BLUE if active else SURFACE1,
        "fg": BASE if active else TEXT,
        "activebackground": LAVENDER,
        "activeforeground": BASE,
        "relief": "flat",
        "font": FONT_UI,
        "padx": 10,
        "pady": 6,
        "cursor": "hand2",
        "bd": 0,
    }


def small_button_kw() -> dict:
    """Keyword args for a small Button."""
    return {
        "bg": SURFACE1,
        "fg": TEXT,
        "activebackground": BLUE,
        "activeforeground": BASE,
        "relief": "flat",
        "font": FONT_SMALL,
        "padx": 8,
        "pady": 3,
        "cursor": "hand2",
        "bd": 0,
    }


def frame_kw() -> dict:
    """Keyword args for a standard Frame."""
    return {"bg": BASE}


def sidebar_frame_kw() -> dict:
    """Keyword args for a sidebar Frame."""
    return {"bg": MANTLE}
