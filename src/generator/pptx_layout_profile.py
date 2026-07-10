"""Layout profile derived from user-tuned Farhan_Beraterprofil_LLM.pptx (Jul 2026)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShapeRect:
    left: int
    top: int
    width: int
    height: int


# Original ORBIT template anchors — used only to locate shapes before applying layout.
TEMPLATE_ANCHORS: dict[str, tuple[int, int]] = {
    "title": (503148, 27489),
    "position_labels": (2209140, 972000),
    "summary_label": (2209140, 1569297),
    "kompetenzen_label": (647403, 2650668),
    "position": (3727239, 970730),
    "schwerpunkte": (3727239, 1291395),
    "summary": (3727239, 1590943),
    "kompetenzen": (533999, 2943147),
    "relevante": (4062770, 2906571),
    "international": (7997235, 2906571),
    "education": (8022387, 4720513),
    "tools": (553881, 4846422),
    "tools_dup": (438105, 4788720),
}

# Fine-tuned text positions (EMU) — applied on every generation.
LAYOUT_PROFILE: dict[str, ShapeRect] = {
    "position_labels": ShapeRect(2209140, 1035571, 9441975, 202419),
    "summary_label": ShapeRect(2542032, 1569297, 9264030, 215444),
    "kompetenzen_label": ShapeRect(553881, 2643249, 1660923, 288000),
    "position": ShapeRect(3727239, 1050858, 5743933, 262013),
    "schwerpunkte": ShapeRect(3727239, 1363311, 5743933, 160631),
    "summary": ShapeRect(3727239, 1590943, 5743933, 872868),
    "kompetenzen": ShapeRect(533999, 2943147, 3416845, 1634286),
    "relevante": ShapeRect(4062770, 2906571, 3483661, 1930757),
    "international": ShapeRect(7997235, 2906571, 3957729, 1325133),
    "education": ShapeRect(8022387, 4720513, 3907423, 1758174),
    "tools": ShapeRect(553881, 4846422, 3416845, 1768227),
    "tools_dup": ShapeRect(438105, 4788720, 3416845, 1634286),
}

# Default right-column divider after Ausbildung content (adjusted in fit_text_box_and_divider).
RIGHT_COLUMN_LINE_LEFT = 8207528
RIGHT_COLUMN_LINE_TOP_HINT = 4315318
ABSCHLUSS_HEADER_TOP = 4370318
GAP_AFTER_TEXT_EMU = 55000

_TOLERANCE = 50000
