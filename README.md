# Beratorprofil

Automated generation of ORBIT **Beraterprofil** one-pager PowerPoint slides from consultant CVs.

## Features

- Parse CVs from **PDF**, **DOCX**, or **TXT**
- Transform content into German Beraterprofil structure
- Fill fixed ORBIT PowerPoint template with correct alignment
- Optional LLM enhancement (OpenAI / Anthropic)
- JSON audit file for review and quality checks

## Quick Start

```powershell
cd "C:\Personal\Agentic AI\Beratorprofil"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m src.main "C:\path\to\cv.pdf"
```

Output is written to `output/<Name>_Beraterprofil.pptx`.

## CLI Options

```powershell
python -m src.main cv.pdf `
  --domain "Funknetzplanung" `
  --photo "C:\path\to\photo.jpg" `
  --certificate "2026, PSM I, Scrum.org" `
  --json output\audit.json `
  --llm
```

| Flag | Description |
|------|-------------|
| `--domain` | Override inferred domain title |
| `--photo` | Consultant headshot |
| `--certificate` | Add certificate lines (repeatable) |
| `--json` | Custom audit JSON path |
| `--llm` | Use LLM (needs API key) |
| `--no-llm` | Force rules-based mode |

## Project Structure

```
Beratorprofil/
├── template/Beraterprofil_TEMPLATE.pptx   # ORBIT master slide
├── src/
│   ├── parser/cv_parser.py                # CV extraction
│   ├── transformer/content_transformer.py # German content rules + LLM
│   ├── generator/pptx_generator.py        # Template filler
│   └── main.py                            # CLI
├── prompts/beraterprofil_system.md        # LLM system prompt
├── output/                                # Generated files
└── tests/
```

## Beraterprofil Sections

1. **Title** — `Beraterprofil – {Fachgebiet}`
2. **Position** — Consultant / Senior Consultant + Schwerpunkte
3. **Summary** — German professional summary
4. **Kompetenzen** — 6–9 competency bullets
5. **Relevante Erfahrungen / Projekte** — thematic bullets with bold categories
6. **International experience** — countries, clients, vendors
7. **Tool-Kenntnisse** — categorized tools
8. **Abschluss / Zertifikate** — education and certifications

## Environment Variables

Copy `.env.example` to `.env` and set API keys if using `--llm`.

## Tests

```powershell
pytest tests/
```

## Repository

https://github.com/JSI2020/Beratorprofil.git
