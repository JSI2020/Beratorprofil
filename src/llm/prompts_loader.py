"""Load LLM prompts with mandatory CV-only strict rules appended."""

from __future__ import annotations

from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def load_prompt(name: str) -> str:
    base = (_PROMPTS_DIR / name).read_text(encoding="utf-8")
    strict = (_PROMPTS_DIR / "cv_only_strict.md").read_text(encoding="utf-8")
    return f"{base.rstrip()}\n\n{strict}"
