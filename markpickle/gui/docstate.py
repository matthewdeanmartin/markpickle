"""
Shared document state — holds the current markdown text and notifies panels.

All panels that display markdown input receive a reference to the same
DocumentState instance. When any panel calls ``set(text, source)``, every
registered listener is called with the new text so all inputs stay in sync.
"""

from __future__ import annotations

from typing import Callable


class DocumentState:
    """Observable string holding the current markdown document."""

    def __init__(self) -> None:
        self._text: str = ""
        self._listeners: list[Callable[[str], None]] = []

    # ------------------------------------------------------------------
    def register(self, callback: Callable[[str], None]) -> None:
        """Register a callback that is called whenever the document changes."""
        self._listeners.append(callback)

    def set(self, text: str) -> None:
        """Update the shared document and notify all listeners."""
        self._text = text
        for fn in self._listeners:
            try:
                fn(text)
            except Exception:
                pass

    @property
    def text(self) -> str:
        return self._text
