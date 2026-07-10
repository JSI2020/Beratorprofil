"""Fill the ORBIT Beraterprofil PowerPoint template."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pptx import Presentation

from src.generator.pptx_layout import align_summary_with_schwerpunkte, fit_text_box_and_divider
from src.generator.pptx_shapes import apply_layout_profile, find_all_content_shapes
from src.generator.pptx_text import (
    set_bullet_lines,
    set_categorized_lines,
    set_minimal_bullets,
    set_minimal_plain_text,
    set_plain_text,
)
from src.models.schemas import BeraterprofilContent


def generate_pptx(
    content: BeraterprofilContent,
    template_path: str | Path,
    output_path: str | Path,
    photo_path: str | Path | None = None,
) -> Path:
    template_path = Path(template_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prs = Presentation(str(template_path))
    slide = prs.slides[0]

    shapes = find_all_content_shapes(slide)
    apply_layout_profile(shapes)
    prototypes = _capture_prototypes(shapes)

    set_plain_text(shapes["title"].text_frame, content.title, prototypes["title"])
    set_plain_text(shapes["position"].text_frame, content.position_level, prototypes["position"])
    set_minimal_plain_text(shapes["schwerpunkte"].text_frame, content.schwerpunkte)
    set_minimal_bullets(shapes["kompetenzen"].text_frame, content.kompetenzen)
    align_summary_with_schwerpunkte(shapes, content.summary)

    set_categorized_lines(
        shapes["relevante"].text_frame,
        [(item.category, item.details) for item in content.relevante_erfahrungen],
        prototypes["relevante"],
    )
    set_bullet_lines(
        shapes["international"].text_frame,
        content.international_experience,
        prototypes["international"],
    )
    fit_text_box_and_divider(slide, shapes["international"], content.international_experience)

    set_categorized_lines(
        shapes["tools"].text_frame,
        [(cat.category, ", ".join(cat.tools)) for cat in content.tool_categories],
        prototypes["tools"],
    )
    set_bullet_lines(
        shapes["education"].text_frame,
        content.education_certificates,
        prototypes["education"],
    )

    _clear_shape_text(shapes["tools_dup"])

    if photo_path and Path(photo_path).exists():
        _replace_photo(slide, photo_path)

    prs.save(str(output_path))
    return output_path


def _capture_prototypes(shapes: dict) -> dict[str, object]:
    return {
        "title": _prototype(shapes["title"]),
        "position": _prototype(shapes["position"]),
        "relevante": _prototype(shapes["relevante"]),
        "international": _prototype(shapes["international"]),
        "tools": _prototype(shapes["tools"]),
        "education": _prototype(shapes["education"]),
    }


def _prototype(shape):
    return deepcopy(shape.text_frame.paragraphs[0]._p)


def _clear_shape_text(shape) -> None:
    if not shape.has_text_frame:
        return
    for paragraph in shape.text_frame.paragraphs:
        paragraph.text = ""


def _replace_photo(slide, photo_path: str | Path) -> None:
    photo_path = Path(photo_path)
    for shape in slide.shapes:
        if shape.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
            left, top, width, height = shape.left, shape.top, shape.width, shape.height
            shape_element = shape._element
            shape_element.getparent().remove(shape_element)
            slide.shapes.add_picture(str(photo_path), left, top, width=width, height=height)
            return
