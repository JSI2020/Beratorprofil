"""Layout adjustments that preserve template formatting."""

from __future__ import annotations

from src.generator.pptx_layout_profile import ABSCHLUSS_HEADER_TOP, GAP_AFTER_TEXT_EMU
from src.generator.pptx_shapes import find_right_column_divider

# Template fits ~4 bullets in this height
LINE_HEIGHT_EMU = 330000
MIN_TEXT_BOX_HEIGHT_EMU = 900000


def align_summary_with_schwerpunkte(shapes: dict, summary_text: str) -> None:
    """Match summary text box geometry and margins to Schwerpunkte."""
    from src.generator.pptx_text import set_minimal_plain_text

    schwerpunkte = shapes["schwerpunkte"]
    summary = shapes["summary"]

    summary.left = schwerpunkte.left
    summary.width = schwerpunkte.width

    schwerpunkte_tf = schwerpunkte.text_frame
    summary_tf = summary.text_frame
    summary_tf.margin_left = schwerpunkte_tf.margin_left
    summary_tf.margin_right = schwerpunkte_tf.margin_right
    summary_tf.margin_top = schwerpunkte_tf.margin_top
    summary_tf.margin_bottom = schwerpunkte_tf.margin_bottom

    set_minimal_plain_text(summary_tf, summary_text)


def fit_text_box_and_divider(slide, text_shape, lines: list[str]) -> None:
    """Grow Ausbildung text box to fit bullets; place divider line just below."""
    active_lines = [line for line in lines if line.strip()]
    active_paragraphs = max(len(active_lines), 1)
    wrapped_lines = sum(max(1, (len(line) + 54) // 55) for line in active_lines)
    needed_height = max(
        MIN_TEXT_BOX_HEIGHT_EMU,
        wrapped_lines * LINE_HEIGHT_EMU + 60000,
        active_paragraphs * LINE_HEIGHT_EMU + 60000,
    )

    max_bottom = ABSCHLUSS_HEADER_TOP - GAP_AFTER_TEXT_EMU * 2
    max_height = max(MIN_TEXT_BOX_HEIGHT_EMU, max_bottom - text_shape.top)
    text_shape.height = min(needed_height, max_height)

    line = find_right_column_divider(slide)
    if line is not None:
        line.top = text_shape.top + text_shape.height + GAP_AFTER_TEXT_EMU
