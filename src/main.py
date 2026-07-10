"""CLI entry point for Beraterprofil generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.utils.filename import sanitize_filename
from src.generator.pptx_generator import generate_pptx
from src.parser.cv_parser import parse_cv
from src.transformer.content_transformer import transform_cv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = PROJECT_ROOT / "template" / "Beraterprofil_TEMPLATE.pptx"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an ORBIT Beraterprofil PowerPoint from a consultant CV.",
    )
    parser.add_argument("cv", help="Path to CV file (PDF, DOCX, or TXT)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output PPTX path (default: output/<name>_Beraterprofil.pptx)",
    )
    parser.add_argument(
        "-t",
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help="Path to Beraterprofil template PPTX",
    )
    parser.add_argument(
        "--photo",
        help="Optional consultant photo (JPEG/PNG)",
    )
    parser.add_argument(
        "--domain",
        help="Override inferred domain, e.g. 'Funknetzplanung'",
    )
    parser.add_argument(
        "--certificate",
        action="append",
        default=[],
        help="Extra certificate line: '2026, PSM I, Scrum.org'",
    )
    parser.add_argument(
        "--json",
        help="Optional path to write intermediate JSON audit file",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Use LLM transformation (requires OPENAI_API_KEY or ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Force rules-based transformation",
    )
    parser.add_argument(
        "--strict-template",
        action="store_true",
        help="Use rigid ORBIT template text instead of LLM-personalized content",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv(PROJECT_ROOT / ".env")

    parser = build_parser()
    args = parser.parse_args(argv)

    cv_path = Path(args.cv)
    if not cv_path.exists():
        print(f"CV not found: {cv_path}", file=sys.stderr)
        return 1

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        return 1

    parsed = parse_cv(cv_path)
    use_llm = None
    if args.llm:
        use_llm = True
    if args.no_llm:
        use_llm = False

    content = transform_cv(
        parsed,
        domain_override=args.domain,
        extra_certificates=args.certificate,
        use_llm=use_llm,
        strict_template=args.strict_template,
    )

    safe_name = sanitize_filename(parsed.name) if parsed.name else sanitize_filename(cv_path.stem)
    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / f"{safe_name}_Beraterprofil.pptx"

    generate_pptx(
        content=content,
        template_path=template_path,
        output_path=output_path,
        photo_path=args.photo,
    )

    if args.json:
        json_path = Path(args.json)
    else:
        json_path = output_path.with_suffix(".json")

    payload = {
        "source_cv": str(cv_path),
        "output_pptx": str(output_path),
        "parsed_cv": parsed.to_dict(),
        "beraterprofil": content.to_dict(),
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Beraterprofil created: {output_path}")
    print(f"Audit JSON: {json_path}")
    if content.audit_warnings:
        print("Warnings:")
        for warning in content.audit_warnings:
            print(f"  - {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
