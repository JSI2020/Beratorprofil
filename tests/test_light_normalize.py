"""Tests for light normalization preserving LLM content."""

from src.models.schemas import BeraterprofilContent, CategorizedBullet, ParsedCV
from src.transformer.content_normalizer import normalize_content
from tests.test_template_alignment import _telecom_cv


def test_light_normalize_keeps_llm_summary():
    cv = _telecom_cv()
    llm_content = BeraterprofilContent(
        domain="Funknetzplanung",
        title="Beraterprofil – Funknetzplanung",
        position_level="Senior Consultant",
        schwerpunkte="RAN-Planung, VoLTE/5G",
        summary="Erfahrener Senior Consultant mit über 15 Jahren Expertise in VoLTE.",
        kompetenzen=["VoLTE/SRVCC & Carrier Aggregation", "RAN-Optimierung"],
        relevante_erfahrungen=[
            CategorizedBullet("VoLTE & Carrier Aggregation", "SRVCC, 2CC/3CC")
        ],
        international_experience=["Projekte in Deutschland und Pakistan"],
        tool_categories=[],
        education_certificates=[],
    )

    result = normalize_content(llm_content, cv, "Funknetzplanung")
    assert "15 Jahren" in result.summary
    assert result.position_level == "Senior Consultant"
    assert result.relevante_erfahrungen[0].category == "VoLTE & Carrier Aggregation"
