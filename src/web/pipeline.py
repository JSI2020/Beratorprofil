"""Generation pipeline for the Streamlit app."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from src.generator.pptx_generator import generate_pptx
from src.llm.client import llm_available, resolve_llm_config
from src.models.schemas import BeraterprofilContent, CategorizedBullet, ToolCategory
from src.parser.cv_parser import parse_cv
from src.transformer.content_transformer import transform_cv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE = PROJECT_ROOT / "template" / "Beraterprofil_TEMPLATE.pptx"
OUTPUT_DIR = PROJECT_ROOT / "output"


def init_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def llm_status() -> dict:
    config = resolve_llm_config()
    if config:
        return {"active": True, "provider": config.provider, "model": config.model}
    return {"active": False, "provider": None, "model": None}


def save_upload_temporarily(uploaded_file) -> Path:
    suffix = Path(uploaded_file.name).suffix.lower()
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    handle.write(uploaded_file.getbuffer())
    handle.close()
    return Path(handle.name)


def cleanup_temp(path: Path | None) -> None:
    if path and path.exists() and os.getenv("STORE_UPLOADS", "false").lower() != "true":
        path.unlink(missing_ok=True)


def generate_profile(
    cv_path: Path,
    *,
    domain: str | None = None,
    use_llm: bool | None = None,
    strict_template: bool = False,
    extra_certificates: list[str] | None = None,
) -> tuple[BeraterprofilContent, dict]:
    parsed = parse_cv(cv_path)
    content = transform_cv(
        parsed,
        domain_override=domain or None,
        extra_certificates=extra_certificates,
        use_llm=use_llm,
        strict_template=strict_template,
    )
    audit = {
        "parsed_cv": parsed.to_dict(),
        "beraterprofil": content.to_dict(),
    }
    return content, audit


def export_pptx(
    content: BeraterprofilContent,
    *,
    photo_path: Path | None = None,
    output_name: str | None = None,
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = (output_name or "Beraterprofil").replace(" ", "_")
    output_path = OUTPUT_DIR / f"{safe}_Beraterprofil.pptx"
    generate_pptx(
        content=content,
        template_path=DEFAULT_TEMPLATE,
        output_path=output_path,
        photo_path=photo_path,
    )
    return output_path


def content_to_json(content: BeraterprofilContent) -> str:
    return json.dumps(content.to_dict(), ensure_ascii=False, indent=2)


def content_from_json(text: str) -> BeraterprofilContent:
    data = json.loads(text)
    return BeraterprofilContent(
        domain=data.get("domain", "IT-Beratung"),
        title=data.get("title", "Beraterprofil"),
        position_level=data.get("position_level", "Consultant"),
        schwerpunkte=data.get("schwerpunkte", ""),
        summary=data.get("summary", ""),
        kompetenzen=data.get("kompetenzen", []),
        relevante_erfahrungen=[
            CategorizedBullet(**item) for item in data.get("relevante_erfahrungen", [])
        ],
        international_experience=data.get("international_experience", []),
        tool_categories=[
            ToolCategory(category=item["category"], tools=item["tools"])
            for item in data.get("tool_categories", [])
        ],
        education_certificates=data.get("education_certificates", []),
        audit_warnings=data.get("audit_warnings", []),
    )


def validate_for_export(content: BeraterprofilContent) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if not content.schwerpunkte.strip():
        issues.append("Schwerpunkte fehlen")
    if not content.summary.strip():
        issues.append("Summary fehlt")
    if len(content.kompetenzen) < 3:
        issues.append("Mindestens 3 Kompetenzen erforderlich")
    if not content.relevante_erfahrungen:
        issues.append("Relevante Erfahrungen fehlen")
    if not content.international_experience:
        issues.append("Ausbildung/Karriere (international) fehlt")
    if not content.tool_categories:
        issues.append("Tool-Kenntnisse fehlen")
    return len(issues) == 0, issues
