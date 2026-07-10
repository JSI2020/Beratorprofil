"""Light-touch normalization: keep LLM content, fix structure and ORBIT tool headers."""

from __future__ import annotations

import re

from src.models.schemas import (
    BeraterprofilContent,
    CategorizedBullet,
    ParsedCV,
    ToolCategory,
)
from src.transformer.template_profiles import (
    FUNKNETZ_TOOL_CATEGORIES,
    _build_education_lines,
    _build_international_bullets,
    _clean_vendors,
    build_profile_content,
)


def normalize_content(
    content: BeraterprofilContent,
    cv: ParsedCV,
    domain: str,
    extra_certificates: list[str] | None = None,
    extraction_hints: dict | None = None,
) -> BeraterprofilContent:
    """Preserve LLM-authored text; only fix counts, headers, and CV-derived gaps."""
    fallback = build_profile_content(cv, domain, extra_certificates)

    title = content.title or fallback.title
    if not title.startswith("Beraterprofil"):
        title = f"Beraterprofil – {content.domain or domain}"

    kompetenzen = (_trim(content.kompetenzen, 1, 8) or fallback.kompetenzen)[:6]
    relevante = _trim_categorized(content.relevante_erfahrungen, 4, 6) or fallback.relevante_erfahrungen
    international = _enhance_international(content.international_experience, cv, fallback)
    if len(international) < 3:
        international = fallback.international_experience[:4]
    tools = _normalize_tool_categories(content.tool_categories, cv, fallback)
    education = _normalize_education(
        content.education_certificates,
        cv,
        extra_certificates,
        fallback,
        extraction_hints=extraction_hints,
    )
    if not education:
        education = fallback.education_certificates

    warnings = list(dict.fromkeys(content.audit_warnings + fallback.audit_warnings))

    return BeraterprofilContent(
        domain=content.domain or domain,
        title=title,
        position_level=content.position_level or fallback.position_level,
        schwerpunkte=_fit_schwerpunkte(content.schwerpunkte or fallback.schwerpunkte),
        summary=content.summary or fallback.summary,
        kompetenzen=kompetenzen,
        relevante_erfahrungen=relevante,
        international_experience=international,
        tool_categories=tools,
        education_certificates=education,
        audit_warnings=warnings,
    )


def _trim(items: list[str], min_count: int, max_count: int) -> list[str]:
    cleaned = [item.strip() for item in items if item and item.strip()]
    return cleaned[:max_count] if len(cleaned) >= min_count else cleaned


def _trim_categorized(
    items: list[CategorizedBullet], min_count: int, max_count: int
) -> list[CategorizedBullet]:
    cleaned = [i for i in items if i.category.strip() and i.details.strip()]
    return cleaned[:max_count] if len(cleaned) >= min_count else cleaned


def _enhance_international(
    llm_bullets: list[str],
    cv: ParsedCV,
    fallback: BeraterprofilContent,
) -> list[str]:
    bullets = [b.strip() for b in llm_bullets if b.strip()]
    cv_bullets = fallback.international_experience

    # Ensure role + clients/OSS lines from CV when LLM output is generic
    if not any("internationale" in b.lower() or "regional" in b.lower() for b in bullets):
        if cv_bullets:
            bullets.insert(0, cv_bullets[0])

    if not any("kunden" in b.lower() or "zusammenarbeit" in b.lower() for b in bullets):
        client_line = next((b for b in cv_bullets if "Kunden" in b), None)
        if client_line:
            bullets.append(client_line)

    if not any("oss" in b.lower() or "huawei" in b.lower() for b in bullets):
        oss_line = next((b for b in cv_bullets if "OSS" in b), None)
        if oss_line and oss_line not in bullets:
            bullets.append(oss_line)

    return bullets[:4] if bullets else cv_bullets[:4]


def _normalize_tool_categories(
    llm_categories: list[ToolCategory],
    cv: ParsedCV,
    fallback: BeraterprofilContent,
) -> list[ToolCategory]:
    """Re-bucket tools under ORBIT canonical category headers."""
    all_tools: list[str] = []
    for category in llm_categories:
        all_tools.extend(category.tools)

    if not all_tools and cv.tools:
        for line in cv.tools:
            all_tools.extend(_split_tools(line))

    if not all_tools:
        return fallback.tool_categories

    buckets: dict[str, list[str]] = {name: [] for name in FUNKNETZ_TOOL_CATEGORIES}
    rules: list[tuple[str, list[str]]] = [
        ("OSS / Command Management", ["m2000", "u2000", "netnumen", "u31", "mfiol", "winfiol", "cno", "command"]),
        ("Statistik und Analyse", ["bo", "optima", "netmax", "rno", "cna", "stat", "monitor"]),
        ("Planung und Optimierung", ["atoll", "planet", "aircom", "mcom", "nastar", "piano", "afp"]),
        ("Drive Test und Post-Processing", ["tems", "genex", "actix", "probe", "drive", "assistant"]),
        ("Mapping", ["mapinfo", "google earth", "map"]),
    ]

    for tool in _dedupe_tools(all_tools):
        lower = tool.lower()
        placed = False
        for bucket, keywords in rules:
            if any(kw in lower for kw in keywords):
                buckets[bucket].append(tool)
                placed = True
                break
        if not placed:
            buckets["Planung und Optimierung"].append(tool)

    result: list[ToolCategory] = []
    fallback_map = {c.category: c.tools for c in fallback.tool_categories}
    for name in FUNKNETZ_TOOL_CATEGORIES:
        tools = buckets[name] or fallback_map.get(name, [])
        result.append(ToolCategory(category=name, tools=tools))
    return result


def _normalize_education(
    llm_lines: list[str],
    cv: ParsedCV,
    extra_certificates: list[str] | None,
    fallback: BeraterprofilContent,
    *,
    extraction_hints: dict | None = None,
) -> list[str]:
    lines = [line.strip() for line in llm_lines if line.strip()]

    fixed: list[str] = []
    for line in lines:
        if re.search(r"b\.?e\.?", line, re.I) and not re.match(r"^\d{4}", line):
            fixed.extend(_build_education_lines(cv, extra_certificates))
            continue
        fixed.append(line)

    if not fixed and extraction_hints:
        for candidate in extraction_hints.get("education_candidates", []):
            if candidate not in fixed:
                fixed.append(candidate)
        for candidate in extraction_hints.get("certification_candidates", []):
            if candidate not in fixed:
                fixed.append(candidate)

    if not fixed:
        fixed = fallback.education_certificates
    elif extra_certificates:
        for cert in extra_certificates:
            if cert not in fixed:
                fixed.append(cert)

    return fixed[:8]


def normalize_cv_only(
    content: BeraterprofilContent,
    domain: str,
    extra_certificates: list[str] | None = None,
    extraction_hints: dict | None = None,
) -> BeraterprofilContent:
    """Trim LLM output without injecting template fallbacks — CV upload is the only source."""
    title = content.title
    if not title.startswith("Beraterprofil"):
        title = f"Beraterprofil – {content.domain or domain}"

    kompetenzen = _trim(content.kompetenzen, 1, 8)[:8]
    relevante = _trim_categorized(content.relevante_erfahrungen, 1, 6)
    international = [line.strip() for line in content.international_experience if line.strip()][:4]
    tools = content.tool_categories
    education = [line.strip() for line in content.education_certificates if line.strip()]

    if extraction_hints:
        for candidate in extraction_hints.get("education_candidates", []):
            if candidate not in education:
                education.append(candidate)
        for candidate in extraction_hints.get("certification_candidates", []):
            if candidate not in education:
                education.append(candidate)

    if extra_certificates:
        for cert in extra_certificates:
            if cert not in education:
                education.append(cert)

    return BeraterprofilContent(
        domain=content.domain or domain,
        title=title,
        position_level=content.position_level,
        schwerpunkte=_fit_schwerpunkte(content.schwerpunkte) if content.schwerpunkte else "",
        summary=content.summary,
        kompetenzen=kompetenzen,
        relevante_erfahrungen=relevante,
        international_experience=international,
        tool_categories=tools,
        education_certificates=education[:8],
        audit_warnings=list(content.audit_warnings),
    )


def _split_tools(line: str) -> list[str]:
    line = re.sub(r"^[^:]*:\s*", "", line)
    return [t.strip() for t in re.split(r",|;", line) if t.strip()]


def _dedupe_tools(tools: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for tool in tools:
        key = tool.lower()
        if key not in seen:
            seen.add(key)
            result.append(tool)
    return result


def _fit_schwerpunkte(text: str, max_len: int = 55) -> str:
    """Schwerpunkte box is tiny — keep to one short line like the ORBIT sample."""
    text = text.strip()
    if not text:
        return "Funknetzplanung, Optimierung und Deployment"
    if len(text) <= max_len:
        return text
    # Prefer clean cut at comma, no ellipsis character (can fail to render)
    cut = text[:max_len]
    if ", " in cut:
        return cut.rsplit(", ", 1)[0]
    return cut.rstrip()
