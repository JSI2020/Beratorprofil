"""LLM-first Beraterprofil generation from raw CV text."""

from __future__ import annotations

from pathlib import Path

from src.llm.client import call_llm_json
from src.models.schemas import BeraterprofilContent
from src.transformer.content_normalizer import normalize_content
from src.transformer.content_transformer import content_from_dict
from src.transformer.template_profiles import build_profile_content

_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def generate_profile_from_cv_text(
    cv_text: str,
    *,
    domain: str | None = None,
    extra_certificates: list[str] | None = None,
    parsed_cv=None,
    extraction_hints: dict | None = None,
    cv_only: bool = False,
) -> BeraterprofilContent:
    """LLM reads uploaded CV text and returns template content."""
    system_prompt = (_PROMPTS_DIR / "beraterprofil_from_cv.md").read_text(encoding="utf-8")
    domain_hint = domain or "auto"

    data = call_llm_json(
        system_prompt,
        {
            "cv_text": cv_text,
            "extraction_hints": extraction_hints or {},
            "domain": domain_hint,
            "extra_certificates": extra_certificates or [],
            "cv_only": cv_only,
        },
    )
    content = content_from_dict(data)

    if parsed_cv is not None and not cv_only:
        content = normalize_content(
            content,
            parsed_cv,
            content.domain or domain or "IT-Beratung",
            extra_certificates,
            extraction_hints=extraction_hints,
        )
    elif cv_only:
        from src.transformer.content_normalizer import normalize_cv_only

        content = normalize_cv_only(
            content,
            content.domain or domain or "IT-Beratung",
            extra_certificates,
            extraction_hints=extraction_hints,
        )

    return content


def revise_profile_with_manager_comment(
    current: BeraterprofilContent,
    manager_comment: str,
    *,
    cv_text: str | None = None,
    parsed_cv=None,
    extra_certificates: list[str] | None = None,
    cv_only: bool = False,
) -> BeraterprofilContent:
    """Apply manager feedback to an existing profile via LLM."""
    comment = manager_comment.strip()
    if not comment:
        return current

    system_prompt = (_PROMPTS_DIR / "manager_revision.md").read_text(encoding="utf-8")
    data = call_llm_json(
        system_prompt,
        {
            "cv_text": cv_text or "",
            "current_profile": current.to_dict(),
            "manager_comment": comment,
            "revision_mode": "cv_backed" if cv_text else "profile_only",
            "cv_only": cv_only,
        },
    )
    revised = content_from_dict(data)
    revised.audit_warnings = list(
        dict.fromkeys(revised.audit_warnings + [f"Manager-Feedback angewendet: {comment[:120]}"])
    )

    if parsed_cv is not None and not cv_only:
        revised = normalize_content(revised, parsed_cv, revised.domain, extra_certificates)

    return revised
