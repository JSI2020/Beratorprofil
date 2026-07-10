"""Prepare CV text and extract bilingual section hints for the LLM."""

from __future__ import annotations

import re
from typing import Any

# Section headers in English and German — used for hint extraction and LLM guidance.
SECTION_HEADERS: dict[str, list[str]] = {
    "education": [
        "education",
        "qualification",
        "qualifications",
        "academic background",
        "academic qualifications",
        "degrees",
        "studies",
        "ausbildung",
        "studium",
        "hochschulbildung",
        "bildung",
        "abschluss",
        "akademisch",
    ],
    "certifications": [
        "certification",
        "certifications",
        "certificates",
        "licenses",
        "licences",
        "professional certifications",
        "zertifikat",
        "zertifikate",
        "weiterbildung",
    ],
    "experience": [
        "work experience",
        "professional experience",
        "employment history",
        "career history",
        "berufserfahrung",
        "projekterfahrung",
        "experience",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "competencies",
        "kompetenzen",
        "fachkenntnisse",
        "expertise",
        "areas of expertise",
    ],
    "tools": [
        "tools",
        "technologies",
        "software",
        "tool-kentnisse",
        "technologien",
    ],
    "languages": [
        "languages",
        "sprachen",
        "language skills",
    ],
}

DEGREE_PATTERN = re.compile(
    r"\b("
    r"B\.?\s*E\.?|B\.?\s*Eng\.?|B\.?\s*Sc\.?|B\.?\s*A\.?|Bachelor|"
    r"M\.?\s*E\.?|M\.?\s*Eng\.?|M\.?\s*Sc\.?|M\.?\s*A\.?|Master|MBA|"
    r"Diplom|Ph\.?\s*D\.?|Dr\.|Hochschulabschluss|Staatsexamen"
    r")\b",
    re.IGNORECASE,
)
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
INSTITUTION_PATTERN = re.compile(
    r"\b(University|Universität|Hochschule|Institute|College|School|FH|TU|RWTH)\b",
    re.IGNORECASE,
)
CERT_PATTERN = re.compile(
    r"\b(PSM|ITIL|PMP|PRINCE2|Scrum|AWS|Azure|CCNA|CCNP|HCIA|HCIP|TOGAF|"
    r"ISTQB|SAFe|Six Sigma|Cisco|Huawei|Microsoft|Oracle)\b",
    re.IGNORECASE,
)


def prepare_cv_for_llm(text: str) -> str:
    """Normalize whitespace and annotate table-like blocks for the LLM."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        header = _match_section_header(stripped)
        if header:
            lines.append(f"## SECTION: {header.upper()} ##")
            remainder = _strip_header_line(stripped, header)
            if remainder:
                lines.append(remainder)
            continue
        if stripped.count("|") >= 2 or "\t" in stripped:
            cells = [c.strip() for c in re.split(r"\||\t", stripped) if c.strip()]
            if len(cells) >= 2:
                lines.append(" | ".join(cells))
                continue
        lines.append(stripped)

    return "\n".join(lines).strip()


def extract_cv_hints(text: str) -> dict[str, Any]:
    """Lightweight bilingual scan — helps the LLM not miss education/certs in tables."""
    prepared = prepare_cv_for_llm(text)
    sections = _split_by_markers(prepared)

    education_lines = _unique_lines(
        sections.get("education", [])
        + sections.get("certifications", [])
        + _scan_degree_lines(prepared)
    )
    cert_lines = _unique_lines(
        _scan_certification_lines(prepared)
        + [line for line in education_lines if CERT_PATTERN.search(line)]
    )
    tool_lines = _unique_lines(sections.get("tools", []) + _scan_tool_like_lines(prepared))

    return {
        "detected_sections": sorted(sections.keys()),
        "education_candidates": education_lines[:12],
        "certification_candidates": cert_lines[:12],
        "tool_candidates": tool_lines[:20],
        "extraction_notes": _build_notes(sections, education_lines, cert_lines),
    }


def _match_section_header(line: str) -> str | None:
    normalized = re.sub(r"[:#\-–—|]+$", "", line.strip()).strip().lower()
    normalized = re.sub(r"^\W+|\W+$", "", normalized)
    for section, headers in SECTION_HEADERS.items():
        for header in headers:
            if normalized == header or normalized.startswith(header + " "):
                return section
    return None


def _strip_header_line(line: str, section: str) -> str:
    for header in SECTION_HEADERS[section]:
        pattern = re.compile(rf"^{re.escape(header)}\s*[:#\-–—]?\s*", re.IGNORECASE)
        match = pattern.match(line.strip())
        if match:
            return line.strip()[match.end() :].strip()
    return ""


def _split_by_markers(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        marker = re.match(r"^## SECTION: (\w+) ##$", line.strip())
        if marker:
            current = marker.group(1).lower()
            sections.setdefault(current, [])
            continue
        if current and line.strip():
            sections.setdefault(current, []).append(line.strip())
    return sections


def _scan_degree_lines(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("##"):
            continue
        if DEGREE_PATTERN.search(stripped) or (
            YEAR_PATTERN.search(stripped) and INSTITUTION_PATTERN.search(stripped)
        ):
            lines.append(stripped.replace("[TABLE]", "").strip())
    return lines


def _scan_certification_lines(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("##"):
            continue
        lower = stripped.lower()
        if CERT_PATTERN.search(stripped) or any(
            kw in lower for kw in ("certified", "zertifikat", "certificate", "license")
        ):
            lines.append(stripped.replace("[TABLE]", "").strip())
    return lines


def _scan_tool_like_lines(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("##"):
            continue
        if ":" in stripped and any(
            kw in stripped.lower()
            for kw in ("oss", "ran", "drive test", "planung", "tool", "software", "system")
        ):
            lines.append(stripped)
    return lines


def _unique_lines(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        key = line.lower()
        if key not in seen and len(line) > 3:
            seen.add(key)
            result.append(line)
    return result


def _build_notes(
    sections: dict[str, list[str]],
    education: list[str],
    certs: list[str],
) -> list[str]:
    notes: list[str] = []
    if not sections.get("education") and education:
        notes.append("Education content may appear outside a labeled section — check degree/year lines and [TABLE] blocks.")
    if not sections.get("certifications") and certs:
        notes.append("Certifications may be embedded in Education or Skills sections.")
    if not education and not certs:
        notes.append("No education/certification lines auto-detected — perform exhaustive manual scan of full cv_text.")
    return notes
