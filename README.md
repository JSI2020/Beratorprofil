# Beratorprofil

Automated generation of ORBIT **Beraterprofil** one-pager PowerPoint slides from consultant CVs.

## Features

- Parse CVs from **PDF**, **DOCX**, or **TXT**
- Transform content into German Beraterprofil structure
- Fill fixed ORBIT PowerPoint template with correct alignment
- Optional LLM enhancement (DeepSeek / Mistral / OpenAI / Anthropic)
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

## Web App (Streamlit)

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 — upload any CV, preview the generated profile, edit JSON if needed, download PowerPoint.

Design tokens live in `DESIGN.md` (Google [design.md](https://github.com/google-labs-code/design.md) format).

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

Copy `.env.example` to `.env` (already included) and add your API key.

### DeepSeek (recommended)

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-key-here
DEEPSEEK_MODEL=deepseek-chat
```

Get a key at https://platform.deepseek.com/

### Mistral

```env
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your-key-here
MISTRAL_MODEL=mistral-large-latest
```

Get a key at https://console.mistral.ai/

Then run with LLM:

```powershell
python -m src.main cv.pdf --llm
```

Without an API key, rules-based mode still works with `--no-llm`.

## Tests

```powershell
pytest tests/
```

## Repository

https://github.com/JSI2020/Beratorprofil.git
