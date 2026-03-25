"""
Tkinter GUI for markpickle — Phase 3 placeholder.

Run with:
    markpickle gui
    markpickle-gui
"""


def launch_gui() -> None:
    """Launch the markpickle tkinter GUI."""
    try:
        import tkinter as tk  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "tkinter is not available in this Python installation. "
            "On Linux, install it with your package manager (e.g. python3-tk)."
        ) from exc

    # Phase 3 — GUI not yet implemented.
    import tkinter as tk
    import tkinter.messagebox as mb

    root = tk.Tk()
    root.title("markpickle")
    root.geometry("400x150")
    mb.showinfo(
        "Coming Soon",
        "The markpickle GUI is planned for Phase 3.\n\nUse the CLI for now:\n  markpickle --help",
        parent=root,
    )
    root.destroy()
