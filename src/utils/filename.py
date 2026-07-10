"""Safe filename helpers for Windows and cross-platform export paths."""

from __future__ import annotations

import re

_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WHITESPACE = re.compile(r"\s+")
_MULTI_UNDERSCORE = re.compile(r"_+")


def sanitize_filename(name: str, *, fallback: str = "Beraterprofil") -> str:
    """Strip control chars and produce a safe filename stem."""
    cleaned = _WHITESPACE.sub("_", name.strip())
    cleaned = _INVALID_CHARS.sub("_", cleaned)
    cleaned = _MULTI_UNDERSCORE.sub("_", cleaned)
    cleaned = cleaned.strip("._")
    return cleaned or fallback
