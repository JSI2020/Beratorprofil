"""Round-trip tests for Beraterprofil PPTX import."""

from pathlib import Path

from src.generator.pptx_generator import generate_pptx
from src.parser.pptx_parser import parse_beraterprofil_pptx
from src.transformer.template_profiles import build_profile_content
from tests.test_template_alignment import _telecom_cv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = PROJECT_ROOT / "template" / "Beraterprofil_TEMPLATE.pptx"


def test_pptx_round_trip_preserves_core_fields(tmp_path):
    content = build_profile_content(_telecom_cv(), "Funknetzplanung")
    output = tmp_path / "Beraterprofil.pptx"
    generate_pptx(content, TEMPLATE, output)

    imported = parse_beraterprofil_pptx(output)

    assert imported.domain == content.domain
    assert imported.title == content.title
    assert imported.position_level == content.position_level
    assert imported.schwerpunkte.strip()
    assert len(imported.kompetenzen) >= 3
    assert len(imported.relevante_erfahrungen) >= 1
    assert len(imported.tool_categories) >= 1
