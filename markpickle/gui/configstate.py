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
        """Initialize with an optional Config object."""
        self._config: Config = config if config is not None else Config()
        self._listeners: list[Callable[[Config], None]] = []

    def register(self, callback: Callable[[Config], None]) -> None:
        """Register a callback to be notified of Config changes."""
        self._listeners.append(callback)

    def set(self, config: Config) -> None:
        """Set the Config and notify listeners."""
        self._config = config
        for fn in self._listeners:
            try:
                fn(config)
            except Exception:  # pylint: disable=broad-exception-caught
                pass

    @property
    def config(self) -> Config:
        """Return the current Config."""
        return self._config
