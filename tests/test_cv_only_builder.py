"""Tests for CV-only profile builder (no ORBIT template filler)."""

from src.models.schemas import ParsedCV, WorkEntry
from src.transformer.cv_only_builder import build_profile_from_cv_only


def test_cv_only_builder_uses_parsed_fields_not_template():
    cv = ParsedCV(
        summary="Custom summary from CV only.",
        expertise_areas=["RAN Planning", "VoLTE"],
        work_history=[WorkEntry(title="RF Engineer", company="Ericsson", country="Germany")],
        tools=["ATOLL", "TEMS"],
        raw_text="Education\n2012 | B.E. | Test University",
    )
    content = build_profile_from_cv_only(cv, "Funknetzplanung")
    assert content.summary == "Custom summary from CV only."
    assert "RAN Planning" in content.schwerpunkte
    assert "Erfahrener Telekommunikationsberater" not in content.summary
