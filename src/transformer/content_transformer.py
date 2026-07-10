"""Transform parsed CV data into German Beraterprofil content."""

from __future__ import annotations

from src.models.schemas import (
    BeraterprofilContent,
    CategorizedBullet,
    ParsedCV,
    ToolCategory,
)
from src.transformer.cv_only_builder import build_profile_from_cv_only
from src.transformer.template_profiles import build_profile_content

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "Funknetzplanung": [
        "telecom", "ran", "rf", "lte", "volte", "5g", "network", "funk", "mobilfunk",
    ],
    "Software-Entwicklung": [
        "software", "developer", "entwickler", "python", "java", "react", ".net", "api",
    ],
    "CRM-Beratung": ["crm", "sales", "vertrieb", "dynamics", "pipeline"],
    "BI & Data Analytics": ["bi", "power bi", "analytics", "data", "reporting"],
    "Cloud Solutions": ["cloud", "azure", "aws", "migration", "kubernetes"],
    "IT-Security": ["security", "zero trust", "nis2", "mdr", "cyber"],
    "ERP-Beratung": ["erp", "business central", "sap"],
    "Technische Dokumentation": ["documentation", "dokumentation", "technical writer"],
    "Projektmanagement": ["project manager", "scrum", "agile", "pmo"],
}


def transform_cv(
    cv: ParsedCV,
    domain_override: str | None = None,
    extra_certificates: list[str] | None = None,
    use_llm: bool | None = None,
    strict_template: bool = False,
    cv_only: bool = False,
) -> BeraterprofilContent:
    domain = domain_override or classify_domain_from_cv(cv)

    if use_llm is None:
        use_llm = False

    if strict_template:
        return build_profile_content(cv, domain, extra_certificates)
    if not use_llm:
        content = build_profile_from_cv_only(cv, domain, extra_certificates)
        return _fill_gaps_if_needed(content, cv)

    try:
        return _transform_with_llm(cv, domain, extra_certificates, cv_only=cv_only)
    except Exception as exc:
        content = build_profile_from_cv_only(cv, domain, extra_certificates)
        content.audit_warnings.append(f"LLM fallback used: {exc}")
        return _fill_gaps_if_needed(content, cv)


def _fill_gaps_if_needed(content: BeraterprofilContent, cv: ParsedCV) -> BeraterprofilContent:
    from src.llm.gap_fill import fill_missing_from_cv_with_llm

    cv_text = cv.raw_text.strip()
    if not cv_text:
        return content
    return fill_missing_from_cv_with_llm(content, cv_text)


def classify_domain_from_cv(cv: ParsedCV) -> str:
    return _classify_domain(cv)


def _classify_domain(cv: ParsedCV) -> str:
    haystack = " ".join(
        [
            cv.summary,
            " ".join(cv.expertise_areas),
            " ".join(w.title for w in cv.work_history[:2]),
            " ".join(cv.tools),
        ]
    ).lower()

    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for kw in keywords if kw in haystack)

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "IT-Beratung"
    return best


def _transform_with_llm(
    cv: ParsedCV,
    domain: str,
    extra_certificates: list[str] | None,
    *,
    cv_only: bool = False,
) -> BeraterprofilContent:
    from src.llm.profile_generator import generate_profile_from_cv_text
    from src.parser.cv_hints import extract_cv_hints

    if not cv.raw_text.strip():
        raise ValueError("CV has no raw text for LLM")

    return generate_profile_from_cv_text(
        cv.raw_text,
        domain=domain,
        extra_certificates=extra_certificates,
        parsed_cv=None if cv_only else cv,
        extraction_hints=extract_cv_hints(cv.raw_text),
        cv_only=cv_only,
    )


def content_from_dict(data: dict) -> BeraterprofilContent:
    return BeraterprofilContent(
        domain=data.get("domain", "IT-Beratung"),
        title=data.get("title", "Beraterprofil"),
        position_level=data.get("position_level", "Consultant"),
        schwerpunkte=data.get("schwerpunkte", ""),
        summary=data.get("summary", ""),
        kompetenzen=data.get("kompetenzen", []),
        relevante_erfahrungen=[
            CategorizedBullet(**item) for item in data.get("relevante_erfahrungen", [])
        ],
        international_experience=data.get("international_experience", []),
        tool_categories=[
            ToolCategory(category=item["category"], tools=item["tools"])
            for item in data.get("tool_categories", [])
        ],
        education_certificates=data.get("education_certificates", []),
        audit_warnings=data.get("audit_warnings", []),
    )
