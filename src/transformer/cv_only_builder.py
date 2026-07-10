"""Build Beraterprofil content strictly from parsed CV fields — no ORBIT template filler."""

from __future__ import annotations

import re

from src.models.schemas import BeraterprofilContent, CategorizedBullet, ParsedCV, ToolCategory
from src.parser.cv_hints import extract_cv_hints


def build_profile_from_cv_only(
    cv: ParsedCV,
    domain: str,
    extra_certificates: list[str] | None = None,
) -> BeraterprofilContent:
    """Extract only what the rules parser found in the uploaded CV."""
    warnings: list[str] = []

    schwerpunkte = ", ".join(cv.expertise_areas[:4]) if cv.expertise_areas else ""
    summary = cv.summary.strip()
    kompetenzen = [item.strip() for item in cv.expertise_areas[:8] if item.strip()]

    relevante: list[CategorizedBullet] = []
    for job in cv.work_history[:6]:
        if job.bullets:
            relevante.append(
                CategorizedBullet(
                    category=job.title or "Projekterfahrung",
                    details=", ".join(job.bullets[:6]),
                )
            )
        elif job.title:
            details = ", ".join(filter(None, [job.company, job.project, job.country]))
            relevante.append(CategorizedBullet(category=job.title, details=details or job.title))

    international: list[str] = []
    for job in cv.work_history[:4]:
        parts = [p for p in [job.title, job.country or job.project, job.company] if p]
        if parts:
            international.append(" — ".join(parts))
    if cv.vendors:
        international.append(f"Vendor-Erfahrung: {', '.join(cv.vendors[:6])}")

    tool_categories: list[ToolCategory] = []
    if cv.tools:
        grouped: dict[str, list[str]] = {}
        for line in cv.tools:
            if ":" in line:
                category, tools_str = line.split(":", 1)
                tools = [t.strip() for t in re.split(r",|;", tools_str) if t.strip()]
                grouped.setdefault(category.strip(), []).extend(tools)
            else:
                grouped.setdefault("Tools", []).append(line.strip())
        tool_categories = [
            ToolCategory(category=cat, tools=tools[:12]) for cat, tools in grouped.items() if tools
        ]

    education = _education_lines_from_cv(cv, extra_certificates)
    if not education and cv.raw_text.strip():
        hints = extract_cv_hints(cv.raw_text)
        for line in hints.get("education_candidates", []) + hints.get("certification_candidates", []):
            if line not in education:
                education.append(line)
        if education:
            warnings.append("Abschluss/Zertifikate aus CV-Text-Hinweisen übernommen")

    if not education:
        warnings.append("Kein Abschluss/Zertifikat im CV gefunden — LLM gap-fill wird versucht")
    if not summary:
        warnings.append("Keine Summary im CV gefunden")
    if len(kompetenzen) < 3:
        warnings.append("Weniger als 3 Kompetenzen im CV gefunden")

    return BeraterprofilContent(
        domain=domain,
        title=f"Beraterprofil – {domain}",
        position_level=_infer_position(cv),
        schwerpunkte=schwerpunkte,
        summary=summary,
        kompetenzen=kompetenzen,
        relevante_erfahrungen=relevante,
        international_experience=international[:4],
        tool_categories=tool_categories,
        education_certificates=education[:8],
        audit_warnings=warnings,
    )


def _education_lines_from_cv(
    cv: ParsedCV,
    extra_certificates: list[str] | None,
) -> list[str]:
    lines: list[str] = []
    for edu in cv.education:
        parts = [p.strip() for p in [edu.year, edu.degree, edu.institution] if p and p.strip()]
        if parts:
            lines.append(", ".join(parts))
    if extra_certificates:
        for cert in extra_certificates:
            if cert not in lines:
                lines.append(cert)
    return lines


def _infer_position(cv: ParsedCV) -> str:
    for job in cv.work_history:
        if re.search(r"senior|lead|architect", job.title, re.I):
            return "Senior Consultant"
    return "Consultant"
