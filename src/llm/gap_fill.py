"""LLM fallback to fill fields missing after rules-based CV extraction."""

from __future__ import annotations

from src.llm.client import call_llm_json, llm_available
from src.llm.prompts_loader import load_prompt
from src.models.schemas import BeraterprofilContent, CategorizedBullet, ToolCategory
from src.parser.cv_hints import extract_cv_hints


def missing_profile_fields(content: BeraterprofilContent) -> list[str]:
    missing: list[str] = []
    if not content.education_certificates:
        missing.append("education_certificates")
    if not content.schwerpunkte.strip():
        missing.append("schwerpunkte")
    if not content.summary.strip():
        missing.append("summary")
    if len(content.kompetenzen) < 3:
        missing.append("kompetenzen")
    if not content.relevante_erfahrungen:
        missing.append("relevante_erfahrungen")
    if not content.international_experience:
        missing.append("international_experience")
    if not content.tool_categories:
        missing.append("tool_categories")
    return missing


def fill_missing_from_cv_with_llm(
    content: BeraterprofilContent,
    cv_text: str,
) -> BeraterprofilContent:
    """Use LLM only for fields the rules engine did not find."""
    if not llm_available():
        return content

    missing = missing_profile_fields(content)
    if not missing or not cv_text.strip():
        return content

    system_prompt = load_prompt("cv_gap_fill.md")
    data = call_llm_json(
        system_prompt,
        {
            "cv_text": cv_text,
            "missing_fields": missing,
            "extraction_hints": extract_cv_hints(cv_text),
            "cv_only": True,
            "strict_cv_only": True,
        },
    )

    warnings = list(content.audit_warnings)
    warnings.append(f"LLM gap-fill für: {', '.join(missing)}")
    warnings.append("Strikte CV-Regel: nur Fakten aus hochgeladenem Lebenslauf")

    return BeraterprofilContent(
        domain=content.domain,
        title=content.title,
        position_level=content.position_level,
        schwerpunkte=data.get("schwerpunkte") or content.schwerpunkte,
        summary=data.get("summary") or content.summary,
        kompetenzen=data.get("kompetenzen") or content.kompetenzen,
        relevante_erfahrungen=_merge_categorized(
            content.relevante_erfahrungen,
            data.get("relevante_erfahrungen", []),
        ),
        international_experience=data.get("international_experience") or content.international_experience,
        tool_categories=_merge_tools(content.tool_categories, data.get("tool_categories", [])),
        education_certificates=data.get("education_certificates") or content.education_certificates,
        audit_warnings=warnings,
    )


def _merge_categorized(
    existing: list[CategorizedBullet],
    incoming: list,
) -> list[CategorizedBullet]:
    if existing:
        return existing
    return [
        CategorizedBullet(category=item["category"], details=item["details"])
        for item in incoming
        if item.get("category")
    ]


def _merge_tools(existing: list[ToolCategory], incoming: list) -> list[ToolCategory]:
    if existing:
        return existing
    return [
        ToolCategory(category=item["category"], tools=item.get("tools", []))
        for item in incoming
        if item.get("category")
    ]
