"""Tests for LLM gap-fill when rules miss CV fields."""

from src.llm.gap_fill import missing_profile_fields
from src.models.schemas import BeraterprofilContent


def test_missing_profile_fields_detects_empty_education():
    content = BeraterprofilContent(
        domain="IT-Beratung",
        title="Beraterprofil – IT-Beratung",
        position_level="Consultant",
        schwerpunkte="Netzplanung",
        summary="Summary text",
        kompetenzen=["A", "B", "C"],
        relevante_erfahrungen=[],
        international_experience=["International"],
        tool_categories=[],
        education_certificates=[],
    )
    missing = missing_profile_fields(content)
    assert "education_certificates" in missing
    assert "relevante_erfahrungen" in missing
    assert "tool_categories" in missing
