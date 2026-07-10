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
from src.llm.profile_generator import generate_profile_from_cv_text, revise_profile_with_manager_comment
from src.models.schemas import BeraterprofilContent, CategorizedBullet, ToolCategory
from src.parser.cv_text import extract_cv_text_with_hints, parse_cv_for_audit
from src.parser.pptx_parser import parse_beraterprofil_pptx
from src.transformer.content_transformer import content_from_dict, transform_cv

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
    """LLM-first: extract CV text → LLM creates template content → optional rules fallback."""
    cv_text, extraction_hints = extract_cv_text_with_hints(cv_path)
    parsed = parse_cv_for_audit(cv_path)

    if use_llm is None:
        use_llm = llm_available()

    if use_llm and llm_available() and not strict_template:
        try:
            content = generate_profile_from_cv_text(
                cv_text,
                domain=domain,
                extra_certificates=extra_certificates,
                parsed_cv=parsed,
                extraction_hints=extraction_hints,
            )
            mode = "LLM (Volltext-CV)"
        except Exception as exc:
            content = transform_cv(
                parsed,
                domain_override=domain,
                extra_certificates=extra_certificates,
                use_llm=False,
                strict_template=strict_template,
            )
            content.audit_warnings.append(f"LLM primary failed, rules fallback: {exc}")
            mode = "Regelbasiert (LLM-Fehler)"
    else:
        content = transform_cv(
            parsed,
            domain_override=domain,
            extra_certificates=extra_certificates,
            use_llm=False,
            strict_template=strict_template,
        )
        mode = "Regelbasiert" if strict_template else "Regelbasiert (kein API-Key)"

    audit = {
        "generation_mode": mode,
        "cv_text_length": len(cv_text),
        "extraction_hints": extraction_hints,
        "parsed_cv": parsed.to_dict(),
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
    parsed = None
    if cv_text:
        try:
            from src.models.schemas import ParsedCV

            parsed = ParsedCV(raw_text=cv_text)
        except Exception:
            pass

    return revise_profile_with_manager_comment(
        current,
        manager_comment,
        cv_text=cv_text,
        parsed_cv=parsed,
        extra_certificates=extra_certificates,
    )


def import_profile_from_pptx(pptx_path: Path) -> tuple[BeraterprofilContent, dict]:
    content = parse_beraterprofil_pptx(pptx_path)
    audit = {
        "generation_mode": "Importiert aus PPTX",
        "source_pptx": str(pptx_path),
        "beraterprofil": content.to_dict(),
    }
    return content, audit


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
