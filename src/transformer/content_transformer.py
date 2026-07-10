"""Transform parsed CV data into German Beraterprofil content."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from src.models.schemas import (
    BeraterprofilContent,
    CategorizedBullet,
    ParsedCV,
    ToolCategory,
)

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
) -> BeraterprofilContent:
    if use_llm is None:
        use_llm = bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))

    if use_llm:
        try:
            return _transform_with_llm(cv, domain_override, extra_certificates)
        except Exception as exc:
            content = _transform_rules(cv, domain_override, extra_certificates)
            content.audit_warnings.append(f"LLM fallback used: {exc}")
            return content

    return _transform_rules(cv, domain_override, extra_certificates)


def _transform_rules(
    cv: ParsedCV,
    domain_override: str | None,
    extra_certificates: list[str] | None,
) -> BeraterprofilContent:
    domain = domain_override or _classify_domain(cv)
    years = _estimate_years(cv)
    position_level = "Senior Consultant" if years >= 10 else "Consultant"
    schwerpunkte = _derive_schwerpunkte(cv, domain)

    summary = _build_summary(cv, domain, years)
    kompetenzen = _build_kompetenzen(cv, domain)
    relevante = _build_relevante_erfahrungen(cv, domain)
    international = _build_international(cv)
    tools = _build_tool_categories(cv)
    education = _build_education_certificates(cv, extra_certificates)

    warnings: list[str] = []
    if not cv.education:
        warnings.append("No education found in CV.")
    if len(kompetenzen) < 6:
        warnings.append("Fewer than 6 competencies extracted.")
    if not cv.tools:
        warnings.append("No tools section found in CV.")

    return BeraterprofilContent(
        domain=domain,
        title=f"Beraterprofil – {domain}",
        position_level=position_level,
        schwerpunkte=schwerpunkte,
        summary=summary,
        kompetenzen=kompetenzen[:9],
        relevante_erfahrungen=relevante[:6],
        international_experience=international[:4],
        tool_categories=tools[:5],
        education_certificates=education,
        audit_warnings=warnings,
    )


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


def _estimate_years(cv: ParsedCV) -> int:
    years = re.findall(r"(19|20)\d{2}", cv.raw_text)
    if not years:
        return 5
    numeric = [int(y) for y in years]
    return max(1, 2026 - min(numeric))


def _derive_schwerpunkte(cv: ParsedCV, domain: str) -> str:
    if domain == "Funknetzplanung":
        return "Funknetzplanung, Optimierung und Deployment"
    if cv.expertise_areas:
        translated = [_translate_term(a) for a in cv.expertise_areas[:3]]
        return ", ".join(translated)
    if cv.work_history:
        return _translate_term(cv.work_history[0].title)
    return domain


def _build_summary(cv: ParsedCV, domain: str, years: int) -> str:
    core = ", ".join(_translate_term(a) for a in cv.expertise_areas[:4]) or domain
    vendors = ", ".join(cv.vendors[:4]) if cv.vendors else "führenden Technologieanbietern"
    countries = _unique_countries(cv)
    country_text = ", ".join(countries[:6]) if countries else "internationalen Märkten"

    return (
        f"Erfahrener {domain}-Berater mit über {years} Jahren fundierter Expertise in "
        f"{core}. Breite Erfahrung über den gesamten Projektlebenszyklus hinweg – von Planung "
        f"und Implementierung bis zu Abnahme, KPI-Monitoring und Performance-Verbesserung. "
        f"Internationale Projekterfahrung in {country_text} sowie Multi-Vendor-Umfeld "
        f"({vendors}). Sicher in der Zusammenarbeit mit Kunden, Betreibern und technischen Teams."
    )


def _build_kompetenzen(cv: ParsedCV, domain: str) -> list[str]:
    defaults_by_domain = {
        "Funknetzplanung": [
            "RAN-Planung und -Optimierung",
            "Solution Consulting für 3G/LTE/VoLTE/5G",
            "Deployment, Integration und Abnahme von Standorten",
            "Projektmanagement",
            "Kunden- und Stakeholder-Management",
            "Multi-Vendor-Erfahrung",
            "RF- und OSS-Tools",
            "KPI-Monitoring und Performance-Optimierung",
        ],
        "Software-Entwicklung": [
            "Anwendungsentwicklung",
            "API-Design und Integration",
            "Agile Softwareentwicklung",
            "Code-Qualität und Testing",
            "Cloud-native Architekturen",
            "DevOps und CI/CD",
        ],
    }

    if domain in defaults_by_domain:
        base = defaults_by_domain[domain]
    else:
        base = [_translate_term(a) for a in cv.expertise_areas]

    if cv.vendors:
        base.append(f"Multi-Vendor-Erfahrung mit {', '.join(cv.vendors[:4])}")
    return _dedupe(base)


def _build_relevante_erfahrungen(cv: ParsedCV, domain: str) -> list[CategorizedBullet]:
    if domain == "Funknetzplanung":
        return [
            CategorizedBullet(
                "Netzwerkplanung und Kapazitätsmanagement",
                "Site Planning, Coverage, Capacity",
            ),
            CategorizedBullet(
                "Performance-Optimierung",
                "KPI-Monitoring, UL/DL Throughput, HOSR, CDR, CSSR",
            ),
            CategorizedBullet(
                "Service Quality",
                "VIP-Beschwerden, Root Cause Analysis, Optimierungsempfehlungen",
            ),
            CategorizedBullet(
                "Drive Test Analysis",
                "Cluster-Analyse, DT-Logs, Layer-3-Analyse",
            ),
            CategorizedBullet(
                "SWAP-Projekte",
                "Vendor-Migration, Integration, Reduzierung von Ausfallzeiten",
            ),
            CategorizedBullet(
                "Geo-Referencing",
                "Pflege von Koordinaten, Datenbankabgleich, Konsistenz der Standortdaten",
            ),
        ]

    bullets: list[CategorizedBullet] = []
    themes = {
        "Planung": [],
        "Optimierung": [],
        "Projektleitung": [],
        "Integration": [],
        "Qualitätssicherung": [],
    }
    for job in cv.work_history:
        for bullet in job.bullets:
            lower = bullet.lower()
            if any(k in lower for k in ["plan", "design", "dimension"]):
                themes["Planung"].append(bullet)
            elif any(k in lower for k in ["optim", "kpi", "performance", "throughput"]):
                themes["Optimierung"].append(bullet)
            elif any(k in lower for k in ["lead", "manage", "coordinate", "team"]):
                themes["Projektleitung"].append(bullet)
            elif any(k in lower for k in ["integrat", "deploy", "implement", "rollout"]):
                themes["Integration"].append(bullet)
            else:
                themes["Qualitätssicherung"].append(bullet)

    for category, items in themes.items():
        if items:
            details = ", ".join(_shorten(_translate_term(i)) for i in items[:3])
            bullets.append(CategorizedBullet(category, details))
    return bullets


def _build_international(cv: ParsedCV) -> list[str]:
    countries = _unique_countries(cv)
    clients = _unique_clients(cv)
    lead_titles = [w.title for w in cv.work_history if re.search(r"lead|consultant|advisor", w.title, re.I)]

    bullets: list[str] = []
    if lead_titles:
        bullets.append(
            f"Internationale Einsätze als {_translate_term(lead_titles[0])}"
        )
    if countries:
        bullets.append(f"Projekterfahrung in {', '.join(countries)}")
    if cv.vendors:
        bullets.append(f"OSS-Erfahrung mit {', '.join(cv.vendors[:5])}")
    if clients:
        bullets.append(
            "Zusammenarbeit mit internationalen Kunden wie "
            + ", ".join(clients[:10])
        )
    return bullets


def _build_tool_categories(cv: ParsedCV) -> list[ToolCategory]:
    if not cv.tools:
        return []

    categories: dict[str, list[str]] = {
        "OSS / Command Management": [],
        "Statistik und Analyse": [],
        "Planung und Optimierung": [],
        "Drive Test und Post-Processing": [],
        "Mapping": [],
        "Sonstige Tools": [],
    }

    for tool_line in cv.tools:
        line = tool_line.lower()
        tool_names = re.sub(r"^[^:]*:\s*", "", tool_line)
        names = [n.strip() for n in re.split(r",|;", tool_names) if n.strip()]

        if any(k in line for k in ["oss", "command", "mfiol", "winfiol", "netnumen", "u31", "cno"]):
            key = "OSS / Command Management"
        elif any(k in line for k in ["stat", "bo", "optima", "netmax", "monitor"]):
            key = "Statistik und Analyse"
        elif any(k in line for k in ["atoll", "planet", "plan", "optim", "mcom", "nastar", "aircom"]):
            key = "Planung und Optimierung"
        elif any(k in line for k in ["drive", "tems", "genex", "actix", "probe"]):
            key = "Drive Test und Post-Processing"
        elif any(k in line for k in ["map", "google earth", "mapinfo"]):
            key = "Mapping"
        else:
            key = "Sonstige Tools"

        categories[key].extend(names or [tool_line])

    result: list[ToolCategory] = []
    for category, tools in categories.items():
        deduped = _dedupe(tools)
        if deduped:
            result.append(ToolCategory(category=category, tools=deduped[:8]))
    return result


def _build_education_certificates(
    cv: ParsedCV,
    extra_certificates: list[str] | None,
) -> list[str]:
    lines: list[str] = []
    for edu in cv.education:
        year = edu.year or ""
        degree = _translate_term(edu.degree)
        institution = edu.institution
        line = ", ".join(part for part in [year, degree, institution] if part)
        if line:
            lines.append(line)

    for cert in cv.certifications:
        line = ", ".join(part for part in [cert.year, cert.name, cert.issuer] if part)
        if line:
            lines.append(line)

    if extra_certificates:
        lines.extend(extra_certificates)

    return lines[:8]


def _unique_countries(cv: ParsedCV) -> list[str]:
    mapping = {
        "Germany": "Deutschland",
        "Pakistan": "Pakistan",
        "South Africa": "Südafrika",
        "UAE": "VAE",
        "Oman": "Oman",
        "Bahrain": "Bahrain",
        "Ghana": "Ghana",
    }
    found: list[str] = []
    for job in cv.work_history:
        for source in [job.country, job.project]:
            for key, value in mapping.items():
                if key.lower() in source.lower() and value not in found:
                    found.append(value)
    return found


def _unique_clients(cv: ParsedCV) -> list[str]:
    known = [
        "Deutsche Telekom",
        "China Mobile Pakistan",
        "CMPAK",
        "MTN",
        "Telenor",
        "Omantel",
        "Vodacom",
        "Etisalat",
        "VIVA",
        "Zain",
    ]
    text = cv.raw_text
    return [client for client in known if client.lower() in text.lower()]


def _translate_term(text: str) -> str:
    replacements = {
        "Strategic Network Planning": "Strategische Netzwerkplanung",
        "Solution Consultancy": "Solution Consulting",
        "RAN Planning & Optimization": "RAN-Planung und -Optimierung",
        "Project Management": "Projektmanagement",
        "Customer Relationship Management": "Kunden- und Stakeholder-Management",
        "Critical Decision-Making": "Kritische Entscheidungsfindung",
        "Access Management": "Access Management",
        "RF Planning": "RF-Planung",
        "Optimization": "Optimierung",
        "Planning": "Planung",
        "Team Lead": "Teamleitung",
        "Consultant": "Consultant",
        "B.E. (Electrical)": "Bachelor of Engineering in Electrical Engineering",
    }
    result = text.strip()
    for src, dst in replacements.items():
        result = re.sub(re.escape(src), dst, result, flags=re.IGNORECASE)
    return result


def _shorten(text: str, max_len: int = 60) -> str:
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _transform_with_llm(
    cv: ParsedCV,
    domain_override: str | None,
    extra_certificates: list[str] | None,
) -> BeraterprofilContent:
    prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "beraterprofil_system.md"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    user_payload = {
        "cv": cv.to_dict(),
        "domain_override": domain_override,
        "extra_certificates": extra_certificates or [],
    }

    if os.getenv("OPENAI_API_KEY"):
        return _call_openai(system_prompt, user_payload)
    if os.getenv("ANTHROPIC_API_KEY"):
        return _call_anthropic(system_prompt, user_payload)
    raise RuntimeError("No LLM API key configured")


def _call_openai(system_prompt: str, payload: dict) -> BeraterprofilContent:
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=0.2,
    )
    data = json.loads(response.choices[0].message.content)
    return _content_from_dict(data)


def _call_anthropic(system_prompt: str, payload: dict) -> BeraterprofilContent:
    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
    )
    text = response.content[0].text
    data = json.loads(text)
    return _content_from_dict(data)


def _content_from_dict(data: dict) -> BeraterprofilContent:
    return BeraterprofilContent(
        domain=data["domain"],
        title=data.get("title", f"Beraterprofil – {data['domain']}"),
        position_level=data.get("position_level", "Consultant"),
        schwerpunkte=data["schwerpunkte"],
        summary=data["summary"],
        kompetenzen=data["kompetenzen"],
        relevante_erfahrungen=[
            CategorizedBullet(**item) for item in data["relevante_erfahrungen"]
        ],
        international_experience=data["international_experience"],
        tool_categories=[
            ToolCategory(category=item["category"], tools=item["tools"])
            for item in data["tool_categories"]
        ],
        education_certificates=data["education_certificates"],
        audit_warnings=data.get("audit_warnings", []),
    )
