"""Tests for bilingual CV hint extraction and table-aware preprocessing."""

from src.parser.cv_hints import extract_cv_hints, prepare_cv_for_llm


ENGLISH_CV_WITH_TABLE = """
John Example
Senior Telecom Engineer

Professional Summary
Experienced RAN consultant with 10+ years in LTE and 5G.

Work Experience
RF Engineer | 2018 - Present
Ericsson | Project: MTN South Africa

Education
[TABLE]
2012 | B.E. Electrical Engineering | University of Engineering Lahore
2018 | PSM I | Scrum.org

Certifications
[TABLE]
HCIA-RAN | Huawei
ITIL Foundation | AXELOS

TOOLS
OSS: M2000, U2000
Planning: Atoll, Planet
"""


def test_prepare_cv_marks_english_education_section():
    prepared = prepare_cv_for_llm(ENGLISH_CV_WITH_TABLE)
    assert "## SECTION: EDUCATION ##" in prepared
    assert "## SECTION: CERTIFICATIONS ##" in prepared
    assert "[TABLE]" in prepared


def test_extract_cv_hints_finds_education_in_english_cv():
    prepared = prepare_cv_for_llm(ENGLISH_CV_WITH_TABLE)
    hints = extract_cv_hints(prepared)

    assert "education" in hints["detected_sections"]
    joined = " ".join(hints["education_candidates"]).lower()
    assert "b.e." in joined or "electrical" in joined
    assert any("psm" in line.lower() for line in hints["certification_candidates"] + hints["education_candidates"])
    assert any("huawei" in line.lower() or "hcia" in line.lower() for line in hints["certification_candidates"])


def test_extract_cv_hints_finds_tools():
    prepared = prepare_cv_for_llm(ENGLISH_CV_WITH_TABLE)
    hints = extract_cv_hints(prepared)
    tools = " ".join(hints["tool_candidates"]).lower()
    assert "m2000" in tools or "atoll" in tools
