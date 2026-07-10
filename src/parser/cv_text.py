"""Extract raw CV text from uploaded files (no rules-based content generation)."""

from __future__ import annotations

from pathlib import Path

from src.parser.cv_parser import _read_text
from src.parser.cv_parser import parse_cv as parse_cv_structured


def extract_cv_text(path: str | Path) -> str:
    """Return full CV text for LLM — first step in the pipeline."""
    text = _read_text(Path(path)).strip()
    if not text:
        raise ValueError("CV file is empty or text could not be extracted")
    return text


def parse_cv_for_audit(path: str | Path):
    """Light structured parse for audit JSON only — not used for content generation."""
    return parse_cv_structured(path)
