"""
Shared config state — holds the live Config and notifies panels when it changes.

Analogous to DocumentState but for markpickle.Config objects.
"""

from __future__ import annotations

from typing import Callable

from markpickle.config_class import Config


class ConfigState:
    """Observable Config object."""

    def __init__(self, config: Config = None) -> None:
        self._config: Config = config if config is not None else Config()
        self._listeners: list[Callable[[Config], None]] = []

    def register(self, callback: Callable[[Config], None]) -> None:
        self._listeners.append(callback)

    def set(self, config: Config) -> None:
        self._config = config
        for fn in self._listeners:
            try:
                fn(config)
            except Exception:
                pass

    @property
    def config(self) -> Config:
        return self._config
