"""Dedicated LLM calls for Schwerpunkte and Kompetenzen from the full CV."""

from __future__ import annotations

from pathlib import Path

from src.llm.client import call_llm_json
from src.models.schemas import ParsedCV

_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def generate_schwerpunkte(cv: ParsedCV) -> str:
    system_prompt = (_PROMPTS_DIR / "schwerpunkte.md").read_text(encoding="utf-8")
    data = call_llm_json(system_prompt, {"cv_text": cv.raw_text, "name": cv.name})
    text = str(data.get("schwerpunkte", "")).strip()
    return text.replace("\n", ", ").strip(" ,")


def generate_kompetenzen(cv: ParsedCV) -> list[str]:
    system_prompt = (_PROMPTS_DIR / "kompetenzen.md").read_text(encoding="utf-8")
    data = call_llm_json(system_prompt, {"cv_text": cv.raw_text, "name": cv.name})
    items = data.get("kompetenzen", [])
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    return cleaned[:8]
