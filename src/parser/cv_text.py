"""Extract raw CV text from uploaded files (no rules-based content generation)."""

from __future__ import annotations

from pathlib import Path

from src.parser.cv_reader import read_cv_document
from src.parser.cv_hints import extract_cv_hints, prepare_cv_for_llm
from src.parser.cv_parser import parse_cv as parse_cv_structured


def extract_cv_text(path: str | Path) -> str:
    """Return full CV text for LLM — first step in the pipeline."""
    raw = read_cv_document(Path(path))
    prepared = prepare_cv_for_llm(raw)
    if not prepared.strip():
        raise ValueError("CV file is empty or text could not be extracted")
    return prepared


def extract_cv_text_with_hints(path: str | Path) -> tuple[str, dict]:
    """Return prepared CV text plus bilingual section hints for the LLM."""
    raw = read_cv_document(Path(path))
    prepared = prepare_cv_for_llm(raw)
    if not prepared.strip():
        raise ValueError("CV file is empty or text could not be extracted")
    hints = extract_cv_hints(prepared)
    return prepared, hints


def parse_cv_for_audit(path: str | Path):
    """Light structured parse for audit JSON only — not used for content generation."""
    return parse_cv_structured(path)
