"""Read CV documents with table-aware extraction."""

from __future__ import annotations

from pathlib import Path


def read_cv_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix in {".docx", ".doc"}:
        return _read_docx(path)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported CV format: {suffix}")


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        text = ""
        try:
            text = page.extract_text(extraction_mode="layout") or ""
        except (TypeError, ValueError):
            text = page.extract_text() or ""
        if text.strip():
            parts.append(text)
    return "\n".join(parts)


def _read_docx(path: Path) -> str:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(path))
    parts: list[str] = []

    for child in doc.element.body:
        if child.tag == qn("w:p"):
            text = Paragraph(child, doc).text.strip()
            if text:
                parts.append(text)
        elif child.tag == qn("w:tbl"):
            formatted = _format_table(Table(child, doc))
            if formatted:
                parts.append(formatted)

    return "\n".join(parts)


def _format_table(table) -> str:
    rows: list[str] = []
    for row in table.rows:
        cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
        cells = [cell for cell in cells if cell]
        if not cells:
            continue
        rows.append(" | ".join(cells))
    if not rows:
        return ""
    return "[TABLE]\n" + "\n".join(rows)
