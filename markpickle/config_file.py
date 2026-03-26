"""
File-based configuration for markpickle.

Looks for a ``[tool.markpickle]`` section in ``pyproject.toml`` in the
current directory, or in a path supplied via ``--config``.

Usage
-----
    from markpickle.config_file import load_config
    config = load_config()                        # auto-discover pyproject.toml
    config = load_config("path/to/config.toml")  # explicit file
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path
from typing import Any, Optional

from markpickle.config_class import Config


def _read_toml(path: Path) -> dict[str, Any]:
    """Read a TOML file using tomllib (3.11+) or tomli fallback."""
    if sys.version_info >= (3, 11):
        import tomllib  # pylint: disable=import-outside-toplevel

        with path.open("rb") as fh:
            return tomllib.load(fh)
    else:
        try:
            import tomli  # pylint: disable=import-outside-toplevel

            with path.open("rb") as fh:
                return tomli.load(fh)
        except ImportError:
            try:
                import tomllib  # pylint: disable=import-outside-toplevel

                with path.open("rb") as fh:
                    return tomllib.load(fh)
            except ImportError as exc:
                raise ImportError(
                    "TOML support requires Python 3.11+ or the 'tomli' package. Install it with: pip install tomli"
                ) from exc


def _extract_markpickle_section(data: dict[str, Any], path: Path) -> dict[str, Any]:
    """Pull [tool.markpickle] from a pyproject.toml or the root of a standalone config.toml."""
    # pyproject.toml style: [tool.markpickle]
    if "tool" in data and "markpickle" in data["tool"]:
        return data["tool"]["markpickle"]
    # Standalone config.toml: keys are at root level, or nested under [markpickle]
    if "markpickle" in data:
        return data["markpickle"]
    # Keys directly at root (standalone file with no section header)
    # Only use root keys if the file is NOT named pyproject.toml
    if path.name != "pyproject.toml":
        return {k: v for k, v in data.items() if k != "tool"}
    return {}


def _apply_section(config: Config, section: dict[str, Any]) -> list[str]:
    """
    Apply key/value pairs from a TOML section onto a Config instance.

    Returns a list of warning strings for unrecognised keys.
    """
    fields = {f.name for f in dataclasses.fields(config)}
    # exclude non-serialisable fields
    skip = {"default"}
    warnings: list[str] = []

    for key, value in section.items():
        if key in skip:
            continue
        if key not in fields:
            warnings.append(f"Unknown config key '{key}' — ignored")
            continue
        field_type = type(getattr(config, key))
        # Coerce type if needed (TOML gives us native types for bool/int/str/list)
        if field_type is bool and not isinstance(value, bool):
            value = str(value).lower() in ("true", "1", "yes")
        elif field_type is list and not isinstance(value, list):
            value = [value]
        setattr(config, key, value)

    return warnings


def load_config(
    config_path: Optional[str] = None,
    base: Optional[Config] = None,
) -> Config:
    """
    Load a Config from a TOML file.

    Search order:
    1. ``config_path`` if provided
    2. ``pyproject.toml`` in the current working directory

    If no file is found, returns the default ``Config()``.

    Args:
        config_path: Explicit path to a TOML config file.
        base: Starting Config to layer settings on top of (defaults to Config()).

    Returns:
        A populated Config instance.
    """
    config = base if base is not None else Config()

    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
    else:
        path = Path.cwd() / "pyproject.toml"
        if not path.exists():
            return config  # no config file found — use defaults

    data = _read_toml(path)
    section = _extract_markpickle_section(data, path)

    if not section:
        return config  # file exists but has no [tool.markpickle] section

    _apply_section(config, section)
    return config
