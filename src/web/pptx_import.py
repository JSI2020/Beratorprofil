"""Import Beraterprofil from uploaded PPTX — isolated module for reliable app startup."""

from __future__ import annotations

from pathlib import Path

from src.models.schemas import BeraterprofilContent
from src.parser.pptx_parser import parse_beraterprofil_pptx


def import_profile_from_pptx(pptx_path: Path) -> tuple[BeraterprofilContent, dict]:
    content = parse_beraterprofil_pptx(pptx_path)
    audit = {
        "generation_mode": "Importiert aus PPTX",
        "source_pptx": str(pptx_path),
        "beraterprofil": content.to_dict(),
    }
    return content, audit
