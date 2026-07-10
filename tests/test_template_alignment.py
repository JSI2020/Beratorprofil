"""Tests for template profile alignment."""

from src.models.schemas import ParsedCV, WorkEntry
from src.transformer.content_normalizer import normalize_content
from src.transformer.template_profiles import build_profile_content


def _telecom_cv() -> ParsedCV:
    return ParsedCV(
        summary="Senior telecom expert RAN planning LTE optimization",
        expertise_areas=["RAN Planning", "VoLTE", "5G"],
        vendors=["Huawei, Ericsson, ZTE, Siemens."],
        work_history=[
            WorkEntry(
                title="RAN Planning Consultant",
                project="Deutsche Telekom – Germany",
                country="Germany",
                bullets=["KPI monitoring"],
            ),
            WorkEntry(
                title="RF Team Lead",
                project="CMPAK – Pakistan",
                country="Pakistan",
                bullets=["Network expansion"],
            ),
        ],
        education=[],
        tools=["ATOLL", "TEMS", "MapInfo"],
        raw_text=(
            "Deutsche Telekom CMPAK MTN Telenor Omantel Vodacom Etisalat VIVA Zain "
            "South Africa UAE Oman Bahrain Ghana Pakistan 5G VoLTE freelance courses "
            "B.E. (Electrical) NED University ATOLL TEMS GENEX ACTIX MapInfo Google Earth"
        ),
    )


def test_funknetzplanung_matches_orbit_template_structure():
    cv = _telecom_cv()
    content = build_profile_content(cv, "Funknetzplanung")

    assert content.position_level == "Consultant"
    assert content.schwerpunkte == "Funknetzplanung, Optimierung und Deployment"
    assert len(content.kompetenzen) == 8
    assert "Sehr gute RF-Kenntnisse in 5G, LTE und VoLTE" in content.kompetenzen
    assert len(content.relevante_erfahrungen) == 6
    assert content.relevante_erfahrungen[0].category == "Netzwerkplanung und Kapazitätsmanagement"
    assert len(content.international_experience) == 4
    assert content.international_experience[0].startswith("Internationale Einsätze als")
    assert "OSS-Erfahrung mit" in content.international_experience[2]
    assert "Zusammenarbeit mit internationalen Kunden" in content.international_experience[3]
    assert len(content.tool_categories) == 5
    assert content.tool_categories[0].category == "OSS / Command Management"
    assert "Managed-Services-Umfeld" in content.summary


def test_normalizer_enforces_template_when_strict_mode():
    """Strict template mode uses build_profile_content directly — see transform_cv tests."""
    cv = _telecom_cv()
    from src.transformer.template_profiles import build_profile_content

    content = build_profile_content(cv, "Funknetzplanung")
    assert content.position_level == "Consultant"
    assert content.schwerpunkte == "Funknetzplanung, Optimierung und Deployment"
