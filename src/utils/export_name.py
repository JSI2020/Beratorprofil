"""Fixed export naming — Beraterprofil files never include a person's name."""

from __future__ import annotations

DEFAULT_EXPORT_STEM = "Beraterprofil"


def default_export_filename(*, suffix: str = ".pptx") -> str:
    return f"{DEFAULT_EXPORT_STEM}{suffix}"
