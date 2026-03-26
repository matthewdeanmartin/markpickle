"""
Use 3rd party library to create tables
"""
from __future__ import annotations

from typing import Any


def to_table_tablulate_style(value: Any) -> str:
    """
    The following tabular data types are supported:

    list of lists or another iterable of iterables
    list or another iterable of dicts (keys as columns)
    dict of iterables (keys as columns)
    list of dataclasses (Python 3.7+ only, field names as columns)
    two-dimensional NumPy array
    NumPy record arrays (names as columns)
    pandas.DataFrame

    Requires the ``tabulate`` package: pip install markpickle[tables]
    """
    try:
        import tabulate as tabulate_mod  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        raise ImportError(
            "tabulate is required for tabulate-style tables. Install it with: pip install markpickle[tables]"
        ) from exc
    return tabulate_mod.tabulate(value, tablefmt="github")
