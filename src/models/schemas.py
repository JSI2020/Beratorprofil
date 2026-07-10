"""Data models for CV parsing and Beraterprofil generation."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class WorkEntry:
    title: str = ""
    company: str = ""
    project: str = ""
    country: str = ""
    date_from: str = ""
    date_to: str = ""
    bullets: list[str] = field(default_factory=list)


@dataclass
class EducationEntry:
    year: str = ""
    degree: str = ""
    institution: str = ""


@dataclass
class CertificationEntry:
    year: str = ""
    name: str = ""
    issuer: str = ""


@dataclass
class ParsedCV:
    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    expertise_areas: list[str] = field(default_factory=list)
    vendors: list[str] = field(default_factory=list)
    work_history: list[WorkEntry] = field(default_factory=list)
    education: list[EducationEntry] = field(default_factory=list)
    certifications: list[CertificationEntry] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    raw_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CategorizedBullet:
    category: str
    details: str


@dataclass
class ToolCategory:
    category: str
    tools: list[str]


@dataclass
class BeraterprofilContent:
    domain: str
    title: str
    position_level: str
    schwerpunkte: str
    summary: str
    kompetenzen: list[str]
    relevante_erfahrungen: list[CategorizedBullet]
    international_experience: list[str]
    tool_categories: list[ToolCategory]
    education_certificates: list[str]
    audit_warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "title": self.title,
            "position_level": self.position_level,
            "schwerpunkte": self.schwerpunkte,
            "summary": self.summary,
            "kompetenzen": self.kompetenzen,
            "relevante_erfahrungen": [
                {"category": e.category, "details": e.details}
                for e in self.relevante_erfahrungen
            ],
            "international_experience": self.international_experience,
            "tool_categories": [
                {"category": t.category, "tools": t.tools} for t in self.tool_categories
            ],
            "education_certificates": self.education_certificates,
            "audit_warnings": self.audit_warnings,
        }
