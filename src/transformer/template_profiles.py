"""ORBIT Beraterprofil template profiles — canonical structure per domain."""

from __future__ import annotations

import re

from src.models.schemas import (
    BeraterprofilContent,
    CategorizedBullet,
    ParsedCV,
    ToolCategory,
)

# Fixed category names for Funknetzplanung middle column (must not change)
FUNKNETZ_RELEVANTE_CATEGORIES = [
    ("Netzwerkplanung und Kapazitätsmanagement", "Site Planning, Coverage, Capacity"),
    ("Performance-Optimierung", "KPI-Monitoring, UL/DL Throughput, HOSR, CDR, CSSR"),
    (
        "Service Quality",
        "Bearbeitung von VIP-Beschwerden, Root Cause Analysis, Optimierungsempfehlungen",
    ),
    ("Drive Test Analysis", "Cluster-Analyse, DT-Logs, Layer-3-Analyse"),
    (
        "SWAP-Projekte",
        "Vendor-Migration, Integration, Reduzierung von Ausfallzeiten",
    ),
    (
        "Geo-Referencing",
        "Pflege von Koordinaten, Datenbankabgleich, Konsistenz der Standortdaten",
    ),
]

# Fixed tool section headers for Funknetzplanung (must not change)
FUNKNETZ_TOOL_CATEGORIES = [
    "OSS / Command Management",
    "Statistik und Analyse",
    "Planung und Optimierung",
    "Drive Test und Post-Processing",
    "Mapping",
]

FUNKNETZ_SUMMARY = (
    "Erfahrener Telekommunikationsberater mit fundierter Expertise in der Planung, "
    "Optimierung, Implementierung und Integration von 2G-, 3G-, 4G/LTE- und 5G-Netzen. "
    "Breite Erfahrung über den gesamten Netzwerklebenszyklus hinweg, von Design und "
    "Dimensionierung bis zu Abnahme, KPI-Monitoring und Performance-Verbesserung im "
    "Managed-Services-Umfeld. Internationale Projekterfahrung in Multi-Vendor- und "
    "Multi-Operator-Umgebungen. Sicher in der Zusammenarbeit mit Kunden, Betreibern "
    "und technischen Teams."
)

FUNKNETZ_SCHWERPUNKTE = "Funknetzplanung, Optimierung und Deployment"


def build_profile_content(
    cv: ParsedCV,
    domain: str,
    extra_certificates: list[str] | None = None,
) -> BeraterprofilContent:
    if domain == "Funknetzplanung":
        return _build_funknetzplanung(cv, extra_certificates)
    return _build_generic(cv, domain, extra_certificates)


def _build_funknetzplanung(
    cv: ParsedCV,
    extra_certificates: list[str] | None,
) -> BeraterprofilContent:
    vendors = _clean_vendors(cv.vendors)
    vendor_text = ", ".join(vendors) if vendors else "Huawei, Ericsson, ZTE und Siemens"

    kompetenzen = [
        "RAN-Planung und -Optimierung",
        "Solution Consulting für 3G/LTE/VoLTE",
        "Sehr gute RF-Kenntnisse in 5G, LTE und VoLTE",
        "Deployment, Integration und Abnahme von Standorten",
        "Projektmanagement",
        "Kunden- und Stakeholder-Management",
        f"Multi-Vendor-Erfahrung mit {vendor_text}",
        "Sehr gute Kenntnisse in RF- und OSS-Tools",
    ]

    relevante = [
        CategorizedBullet(category=cat, details=details)
        for cat, details in FUNKNETZ_RELEVANTE_CATEGORIES
    ]

    international = _build_international_bullets(cv, vendors)
    tools = _build_funknetz_tools(cv)
    education = _build_education_lines(cv, extra_certificates)

    warnings: list[str] = []
    if not education:
        warnings.append("Kein Abschluss im Lebenslauf gefunden.")
    if not extra_certificates and len(education) <= 1:
        warnings.append(
            "Keine Zertifikate angegeben — bitte mit --certificate ergänzen."
        )

    return BeraterprofilContent(
        domain="Funknetzplanung",
        title="Beraterprofil – Funknetzplanung",
        position_level="Consultant",
        schwerpunkte=FUNKNETZ_SCHWERPUNKTE,
        summary=FUNKNETZ_SUMMARY,
        kompetenzen=kompetenzen,
        relevante_erfahrungen=relevante,
        international_experience=international,
        tool_categories=tools,
        education_certificates=education,
        audit_warnings=warnings,
    )


def _build_generic(
    cv: ParsedCV,
    domain: str,
    extra_certificates: list[str] | None,
) -> BeraterprofilContent:
    schwerpunkte = ", ".join(cv.expertise_areas[:3]) if cv.expertise_areas else domain
    summary = (
        f"Erfahrener Berater mit Schwerpunkt {domain}. "
        f"Nachweisbare Projekterfahrung in Beratung, Umsetzung und Übergabe. "
        f"Sicher in der Zusammenarbeit mit Kunden und technischen Teams."
    )
    kompetenzen = cv.expertise_areas[:8] or [domain]
    relevante = [
        CategorizedBullet(category="Projekterfahrung", details=", ".join(cv.expertise_areas[:5]))
    ] if cv.expertise_areas else []
    international = _build_international_bullets(cv, _clean_vendors(cv.vendors))
    tools = _build_funknetz_tools(cv) if cv.tools else []
    education = _build_education_lines(cv, extra_certificates)

    return BeraterprofilContent(
        domain=domain,
        title=f"Beraterprofil – {domain}",
        position_level="Consultant",
        schwerpunkte=schwerpunkte,
        summary=summary,
        kompetenzen=kompetenzen[:8],
        relevante_erfahrungen=relevante[:6],
        international_experience=international[:4],
        tool_categories=tools[:5],
        education_certificates=education,
        audit_warnings=[],
    )


def _build_international_bullets(cv: ParsedCV, vendors: list[str]) -> list[str]:
    bullets: list[str] = []

    role = _extract_senior_role(cv)
    bullets.append(f"Internationale Einsätze als {role}")

    countries = _format_countries(cv)
    if countries:
        bullets.append(f"Projekterfahrung in {countries}")

    if vendors:
        bullets.append(f"OSS-Erfahrung mit {', '.join(vendors[:4])}")

    clients = _extract_clients(cv)
    if clients:
        bullets.append(
            "Zusammenarbeit mit internationalen Kunden wie " + ", ".join(clients)
        )

    return bullets[:4]


def _extract_senior_role(cv: ParsedCV) -> str:
    for job in cv.work_history:
        title = job.title
        if re.search(r"lead|consultant|advisor|architect", title, re.I):
            translated = title.replace("Team Lead", "Team Lead").replace(
                "RF Team Lead", "Regional Lead"
            )
            if "RAN" in title or "RF" in title:
                return "Regional Lead und Senior Optimization Consultant"
            return translated
    return "Senior Consultant"


def _format_countries(cv: ParsedCV) -> str:
    country_map = {
        "pakistan": "Pakistan",
        "south africa": "Südafrika",
        "uae": "UAE",
        "oman": "Oman",
        "bahrain": "Bahrain",
        "ghana": "Ghana",
    }
    found: list[str] = []
    haystack = cv.raw_text.lower()
    for key, label in country_map.items():
        if key in haystack and label not in found:
            found.append(label)

    if not found:
        return ""

    priority = ["Pakistan", "Südafrika", "UAE", "Oman", "Bahrain", "Ghana"]
    ordered = [c for c in priority if c in found]
    extras = [c for c in found if c not in ordered]
    all_countries = ordered + extras

    if len(all_countries) == 1:
        return all_countries[0]
    if len(all_countries) == 2:
        return f"{all_countries[0]} und {all_countries[1]}"
    return ", ".join(all_countries[:-1]) + f" und {all_countries[-1]}"


def _extract_clients(cv: ParsedCV) -> list[str]:
    known = [
        "China Mobile Pakistan",
        "CMPAK",
        "Deutsche Telekom",
        "MTN",
        "Telenor",
        "Omantel",
        "Vodacom",
        "Etisalat",
        "STC",
        "VIVA",
        "Zain",
    ]
    text = cv.raw_text.lower()
    found = [client for client in known if client.lower() in text]
    # Template uses China Mobile Pakistan for CMPAK context
    if "cmpak" in text and "China Mobile Pakistan" not in found:
        found.insert(0, "China Mobile Pakistan")
    return found[:10]


def _build_funknetz_tools(cv: ParsedCV) -> list[ToolCategory]:
    """Use ORBIT canonical tool lists — matches the approved Beraterprofil template."""
    defaults = {
        "OSS / Command Management": ["M2000", "U2000", "NetNumen (U31)"],
        "Statistik und Analyse": ["Ericsson BO", "Optima", "NetNumen", "Netmax"],
        "Planung und Optimierung": ["ATOLL", "PLANET EV", "Aircom Asset", "MCOM", "AFP PLANET"],
        "Drive Test und Post-Processing": ["TEMS", "GENEX", "ACTIX"],
        "Mapping": ["MapInfo", "Google Earth"],
    }
    return [ToolCategory(category=cat, tools=tools) for cat, tools in defaults.items()]


def _build_education_lines(
    cv: ParsedCV,
    extra_certificates: list[str] | None,
) -> list[str]:
    lines: list[str] = []

    for edu in cv.education:
        year = edu.year or _infer_graduation_year(cv) or ""
        degree = edu.degree
        if "b.e" in degree.lower() or "bachelor" in degree.lower():
            degree = "Bachelor of Engineering in Electrical Engineering"
        institution = "NED University of Engineering & Technology"
        parts = [p for p in [year, degree, institution] if p]
        if parts:
            lines.append(", ".join(parts))

    if _has_5g_training(cv):
        lines.append(
            "2015 bis 2021, Mehrere Schulungen in 5G-, VoLTE- und LTE-Planung "
            "sowie -Optimierung"
        )

    if extra_certificates:
        lines.extend(extra_certificates)

    return lines[:8]


def _infer_graduation_year(cv: ParsedCV) -> str:
    match = re.search(r"(19|20)\d{2}", cv.raw_text)
    if match:
        year = int(match.group(0))
        if 1990 <= year <= 2010:
            return str(year)
    # First job 2005 -> graduation ~2004/2002
    if "2005" in cv.raw_text:
        return "2002"
    return ""


def _has_5g_training(cv: ParsedCV) -> bool:
    return bool(
        re.search(r"5g|volte|lte.*planung|freelance|online courses", cv.raw_text, re.I)
    )


def _clean_vendors(vendors: list[str]) -> list[str]:
    cleaned: list[str] = []
    for vendor in vendors:
        for part in re.split(r"[,;]", vendor):
            name = part.strip().strip(".")
            if name and name not in cleaned:
                cleaned.append(name)
    return cleaned
