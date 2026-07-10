"""Basic tests for Beratorprofil pipeline."""

from pathlib import Path

from src.models.schemas import ParsedCV, WorkEntry
from src.transformer.content_transformer import transform_cv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_telecom_domain_classification():
    cv = ParsedCV(
        summary="Senior telecom expert with RAN planning and LTE optimization",
        expertise_areas=["RAN Planning", "VoLTE", "5G"],
        work_history=[
            WorkEntry(title="RAN Planning Consultant", project="Deutsche Telekom – Germany")
        ],
        tools=["ATOLL", "TEMS"],
        raw_text="Huawei Ericsson Deutsche Telekom RAN LTE",
    )
    content = transform_cv(cv, use_llm=False)
    assert content.domain == "Funknetzplanung"
    assert content.title == "Beraterprofil – Funknetzplanung"
    assert len(content.kompetenzen) >= 1
    assert "15 Jahren" not in content.summary  # no generic ORBIT template filler


def test_template_exists():
    template = PROJECT_ROOT / "template" / "Beraterprofil_TEMPLATE.pptx"
    assert template.exists()
