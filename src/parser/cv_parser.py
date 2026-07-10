"""Extract structured data from CV files (PDF, DOCX, TXT)."""

from __future__ import annotations

import re
from pathlib import Path

from src.models.schemas import CertificationEntry, EducationEntry, ParsedCV, WorkEntry


def parse_cv(path: str | Path) -> ParsedCV:
    path = Path(path)
    text = _read_text(path)
    return _parse_text(text)


def _read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix in {".docx", ".doc"}:
        return _read_docx(path)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported CV format: {suffix}")


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _read_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def _parse_text(text: str) -> ParsedCV:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    cv = ParsedCV(raw_text=text)

    if not lines:
        return cv

    cv.name = lines[0]
    cv.email = _first_match(text, r"[\w.+-]+@[\w.-]+\.\w+")
    cv.phone = _first_match(text, r"\+?\d[\d\s\-()]{7,}\d")

    cv.summary = _extract_section(
        text,
        start_patterns=[r"Senior Telecommunications Professional", r"Professional Summary", r"Summary"],
        end_patterns=[r"Areas of Expertise", r"Work Experience", r"Berufserfahrung"],
    )

    expertise_block = _extract_section(
        text,
        start_patterns=[r"Areas of Expertise", r"Expertise", r"Skills"],
        end_patterns=[r"Vendor Experience", r"Work Experience", r"TOOLS"],
    )
    cv.expertise_areas = _split_list_items(expertise_block)

    vendor_block = _extract_section(
        text,
        start_patterns=[r"Vendor Experience"],
        end_patterns=[r"Work Experience", r"Qualification"],
    )
    cv.vendors = _split_list_items(vendor_block.replace("Vendor Experience:", ""))

    tools_block = _extract_section(
        text,
        start_patterns=[r"TOOLS", r"Tools", r"Technologies"],
        end_patterns=[r"Qualification", r"Education", r"Ausbildung", r"$"],
    )
    cv.tools = _extract_tool_lines(tools_block)

    cv.education = _parse_education(text)
    cv.work_history = _parse_work_history(text)
    return cv


def _first_match(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(0).strip() if match else ""


def _extract_section(text: str, start_patterns: list[str], end_patterns: list[str]) -> str:
    start_idx = None
    for pattern in start_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            start_idx = match.end()
            break
    if start_idx is None:
        return ""

    remainder = text[start_idx:]
    end_idx = len(remainder)
    for pattern in end_patterns:
        match = re.search(pattern, remainder, flags=re.IGNORECASE)
        if match:
            end_idx = min(end_idx, match.start())
    return remainder[:end_idx].strip()


def _split_list_items(block: str) -> list[str]:
    if not block:
        return []
    items = re.split(r"[⎟|•\n]", block)
    cleaned = [re.sub(r"\s+", " ", item).strip(" -:;") for item in items]
    return [item for item in cleaned if item and len(item) > 2]


def _extract_tool_lines(block: str) -> list[str]:
    if not block:
        return []
    tools: list[str] = []
    for line in block.splitlines():
        line = re.sub(r"^[\s•\-]+", "", line).strip()
        if line:
            tools.append(line)
    return tools


def _parse_education(text: str) -> list[EducationEntry]:
    block = _extract_section(
        text,
        start_patterns=[r"Qualification", r"Education", r"Ausbildung"],
        end_patterns=[r"TOOLS", r"Tools", r"$"],
    )
    if not block:
        return []

    entries: list[EducationEntry] = []
    degree_match = re.search(
        r"(B\.?E\.?|Bachelor|Master|M\.?Sc|Diplom|Ph\.?D)[^\n]*",
        block,
        flags=re.IGNORECASE,
    )
    institution_match = re.search(
        r"(University|Universität|Hochschule|Institute)[^\n]*",
        block,
        flags=re.IGNORECASE,
    )
    year_match = re.search(r"(19|20)\d{2}", block)

    if degree_match or institution_match:
        entries.append(
            EducationEntry(
                year=year_match.group(0) if year_match else "",
                degree=degree_match.group(0).strip() if degree_match else block.splitlines()[0],
                institution=institution_match.group(0).strip() if institution_match else "",
            )
        )
    return entries


def _parse_work_history(text: str) -> list[WorkEntry]:
    block = _extract_section(
        text,
        start_patterns=[r"Work Experience", r"Berufserfahrung", r"Experience"],
        end_patterns=[r"Qualification", r"Education", r"TOOLS", r"$"],
    )
    if not block:
        return []

    entries: list[WorkEntry] = []
    chunks = re.split(r"_{5,}", block)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        header_line = chunk.splitlines()[0]
        header_match = re.match(
            r"(?P<title>.+?)\s*\|\s*(?P<dates>.+)$",
            header_line,
        )
        if not header_match:
            continue

        title = header_match.group("title").strip()
        dates = header_match.group("dates").strip()
        date_parts = re.split(r"\s*[–\-]\s*", dates, maxsplit=1)
        date_from = date_parts[0].strip() if date_parts else ""
        date_to = date_parts[1].strip() if len(date_parts) > 1 else ""

        company = ""
        project = ""
        country = ""
        if len(chunk.splitlines()) > 1:
            meta = chunk.splitlines()[1]
            company_match = re.match(r"(?P<company>.+?)\s*\|\s*Project:\s*(?P<project>.+)$", meta, re.I)
            if company_match:
                company = company_match.group("company").strip()
                project = company_match.group("project").strip()
                country_match = re.search(
                    r"(Germany|Pakistan|South Africa|UAE|Oman|Bahrain|Ghana|Deutschland)",
                    project,
                    re.I,
                )
                if country_match:
                    country = country_match.group(1)

        bullets = []
        for line in chunk.splitlines()[2:]:
            line = re.sub(r"^[\s•✓\-]+", "", line).strip()
            if line:
                bullets.append(line)

        entries.append(
            WorkEntry(
                title=title,
                company=company,
                project=project,
                country=country,
                date_from=date_from,
                date_to=date_to,
                bullets=bullets,
            )
        )
    return entries
