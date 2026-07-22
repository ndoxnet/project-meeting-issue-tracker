# Concept by MrHan (08974747477)
"""CSV formula-injection mitigation.

Spreadsheet apps may execute a cell that begins with = + - @ (or tab/CR). We
prefix such values with a single quote so they are treated as text.
"""

from __future__ import annotations

_DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def sanitize_cell(value: object) -> str:
    """Return a CSV-safe string for one cell."""
    if value is None:
        return ""
    text = str(value)
    if text and text[0] in _DANGEROUS_PREFIXES:
        return "'" + text
    return text
