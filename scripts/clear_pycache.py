"""Clear Python bytecode cache for this project."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bootstrap import clear_project_pycache  # noqa: E402


def main() -> int:
    count = clear_project_pycache(ROOT)
    print(f"Cleared {count} __pycache__ folder(s) under {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
