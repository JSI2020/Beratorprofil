"""Generation pipeline for the Streamlit app."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from src.utils.export_name import DEFAULT_EXPORT_STEM

from src.generator.pptx_generator import generate_pptx
from src.llm.client import llm_available, resolve_llm_config
from src.llm.gap_fill import fill_missing_from_cv_with_llm, missing_profile_fields
from src.llm.profile_generator import generate_profile_from_cv_text, revise_profile_with_manager_comment
from src.models.schemas import BeraterprofilContent, CategorizedBullet, ToolCategory
from src.parser.cv_hints import extract_cv_hints
from src.parser.cv_parser import parse_cv
from src.parser.cv_text import extract_cv_text
from src.transformer.content_transformer import content_from_dict
from src.transformer.cv_only_builder import build_profile_from_cv_only
from src.transformer.template_profiles import build_profile_content

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


def _resolve_domain(parsed, domain: str | None) -> str:
    from src.transformer.content_transformer import classify_domain_from_cv

    return domain or classify_domain_from_cv(parsed)


def generate_profile(
    cv_path: Path,
    *,
    domain: str | None = None,
    use_llm: bool | None = None,
    strict_template: bool = False,
    extra_certificates: list[str] | None = None,
) -> tuple[BeraterprofilContent, dict]:
    """CV-only rules first, LLM gap-fill for missing fields, optional full LLM."""
    parsed = parse_cv(cv_path)
    cv_text = extract_cv_text(cv_path)
    domain_resolved = _resolve_domain(parsed, domain)

    if use_llm is None:
        use_llm = False

    steps: list[str] = []

    if strict_template:
        content = build_profile_content(parsed, domain_resolved, extra_certificates)
        steps.append("ORBIT-Template")
    else:
        content = build_profile_from_cv_only(parsed, domain_resolved, extra_certificates)
        steps.append("CV-only Regeln")

        missing_before = missing_profile_fields(content)
        if missing_before and llm_available():
            content = fill_missing_from_cv_with_llm(content, cv_text)
            missing_after = missing_profile_fields(content)
            if len(missing_after) < len(missing_before):
                steps.append(f"LLM gap-fill ({', '.join(missing_before)})")
            else:
                steps.append("LLM gap-fill (keine Ergänzung)")
        elif missing_before:
            steps.append("gap-fill übersprungen (kein API-Key)")
            content.audit_warnings.append(
                "Fehlende Felder — LLM gap-fill nicht möglich (kein API-Key): "
                + ", ".join(missing_before)
            )

        if use_llm and llm_available():
            try:
                content = generate_profile_from_cv_text(
                    cv_text,
                    domain=domain_resolved,
                    extra_certificates=extra_certificates,
                    extraction_hints=extract_cv_hints(cv_text),
                    cv_only=True,
                )
                steps.append("LLM Volltext")
                still_missing = missing_profile_fields(content)
                if still_missing and llm_available():
                    content = fill_missing_from_cv_with_llm(content, cv_text)
                    if still_missing:
                        steps.append(f"gap-fill nach LLM ({', '.join(still_missing)})")
            except Exception as exc:
                content.audit_warnings.append(f"LLM Volltext fehlgeschlagen: {exc}")
                steps.append("LLM Volltext fehlgeschlagen")

    mode = " → ".join(steps)

    audit = {
        "generation_mode": mode,
        "data_source": "uploaded_cv_only",
        "cv_filename": cv_path.name,
        "cv_text_length": len(cv_text),
        "education_count": len(content.education_certificates),
        "missing_fields_after": missing_profile_fields(content),
        "beraterprofil": content.to_dict(),
    }
    return content, audit


def apply_manager_feedback(
    current: BeraterprofilContent,
    manager_comment: str,
    *,
    cv_text: str | None = None,
    extra_certificates: list[str] | None = None,
) -> BeraterprofilContent:
    if not llm_available():
        raise RuntimeError("LLM API key required for manager feedback revisions")

    return revise_profile_with_manager_comment(
        current,
        manager_comment,
        cv_text=cv_text,
        parsed_cv=None,
        extra_certificates=extra_certificates,
        cv_only=True,
    )


def import_profile_from_pptx(pptx_path: Path) -> tuple[BeraterprofilContent, dict]:
    from src.web.pptx_import import import_profile_from_pptx as _import

    return _import(pptx_path)


def export_pptx(
    content: BeraterprofilContent,
    *,
    photo_path: Path | None = None,
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{DEFAULT_EXPORT_STEM}.pptx"
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
    return content_from_dict(json.loads(text))


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
