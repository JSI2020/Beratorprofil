---
name: orbit-beraterprofil-ui
description: Modern Streamlit UI design for the ORBIT Beraterprofil generator. Use when building or updating app.py, Streamlit styles, DESIGN.md, or the web frontend. Follow DESIGN.md tokens (navy #0B1F2A, teal #0D9488). Reference cv_onepager_tool workflow — upload CV, preview JSON, export PPTX — but content is personalized per CV via Beratorprofil pipeline.
---

# ORBIT Beraterprofil UI Skill

## Design system

Read `DESIGN.md` at project root before changing UI. Key tokens:

- Primary navy: `#0B1F2A`
- Teal accent: `#0D9488`
- Background: `#F4F7F9`
- Font: DM Sans

Apply via `src/web/styles.py` and `.streamlit/config.toml`.

## UX workflow (from cv_onepager_tool pattern)

1. Upload CV (any person — PDF/DOCX/TXT)
2. Optional: domain, position, certificates, photo
3. **Profil generieren** → LLM/rules pipeline
4. Three-column preview + editable JSON
5. **PowerPoint erstellen** → download PPTX + JSON audit

## Code layout

```
app.py                 # Streamlit entry
src/web/pipeline.py    # wraps parse → transform → generate
src/web/preview.py     # hero + 3-column preview
src/web/styles.py      # DESIGN.md CSS
config/domains.yaml    # domain dropdown
```

## Rules

- German UI labels for consultants/HR
- Never hardcode consultant-specific content in UI
- Show `audit_warnings` before export
- Delete temp uploads unless `STORE_UPLOADS=true`
- Use existing `transform_cv` + `generate_pptx` — do not duplicate LLM logic in app.py

## Run

```powershell
streamlit run app.py
```
