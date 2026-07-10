"""One-time project bootstrap: clear stale bytecode before importing app modules."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

_FLAG = "BERATORPROFIL_BOOTSTRAPPED"
_PROJECT_ROOT = Path(__file__).resolve().parents[1]


def clear_project_pycache(root: Path | None = None) -> int:
    """Remove __pycache__ folders under the project. Returns folders removed."""
    base = root or _PROJECT_ROOT
    removed = 0
    for cache_dir in base.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
            removed += 1
    return removed


def bootstrap() -> None:
    if os.environ.get(_FLAG):
        return
    clear_project_pycache()
    os.environ[_FLAG] = "1"


bootstrap()
