"""Streamlit frontend for ORBIT Beraterprofil generation."""

from __future__ import annotations

import src.bootstrap  # noqa: F401 — clear stale __pycache__ once per process

import json
from datetime import datetime
from pathlib import Path

import streamlit as st
import yaml

from src.utils.export_name import default_export_filename
from src.web.pipeline import (
    apply_manager_feedback,
    cleanup_temp,
    content_from_json,
    content_to_json,
    export_pptx,
    generate_profile,
    init_env,
    llm_status,
    save_upload_temporarily,
    validate_for_export,
)
from src.web.pptx_import import import_profile_from_pptx
from src.parser.cv_text import extract_cv_text
from src.web.preview import render_hero, render_llm_badge, render_preview, render_warnings
from src.web.settings_panel import render_settings_panel
from src.web.styles import inject_styles

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config" / "domains.yaml"


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def reset_session() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def clear_profile_state() -> None:
    """Drop prior profile data — each upload starts fresh."""
    st.session_state.profile_json = ""
    st.session_state.audit_json = ""
    st.session_state.generation_mode = ""
    st.session_state.profile_source = ""
    st.session_state.cv_raw_text = ""
    st.session_state.manager_history = []
    st.session_state.photo_temp_path = None


def init_session_state() -> None:
    defaults = {
        "profile_json": "",
        "audit_json": "",
        "generation_mode": "",
        "profile_source": "",
        "cv_raw_text": "",
        "manager_history": [],
        "photo_temp_path": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_main_workflow(opts: dict, status: dict) -> None:
    st.markdown('<div class="orbit-main-panel">', unsafe_allow_html=True)

    render_hero()
    render_llm_badge(status["active"], status.get("provider"))
    st.caption("Build: pipeline-v2 · Standard = CV-Regeln + LLM gap-fill (LLM-Volltext optional)")

    if opts["use_llm"] and not status["active"]:
        st.warning("LLM ist aktiviert, aber kein API-Key gefunden — es wird regelbasiert generiert.")

    st.markdown('<div class="orbit-card"><div class="orbit-card-title">Schritt 1 — Profil laden</div>', unsafe_allow_html=True)

    source_mode = st.radio(
        "Quelle",
        ["Neues Profil aus CV", "Bestehendes Beraterprofil (PPTX)"],
        horizontal=True,
        label_visibility="collapsed",
    )

    uploaded_cv = None
    uploaded_pptx = None

    if source_mode == "Neues Profil aus CV":
        uploaded_cv = st.file_uploader(
            "Lebenslauf hochladen (PDF, DOCX, TXT)",
            type=["pdf", "docx", "doc", "txt", "md"],
            label_visibility="collapsed",
            key="cv_upload",
        )
    else:
        uploaded_pptx = st.file_uploader(
            "Beraterprofil PowerPoint hochladen (.pptx)",
            type=["pptx"],
            label_visibility="collapsed",
            key="pptx_upload",
        )
        st.caption("Laden Sie ein bestehendes ORBIT-Beraterprofil hoch, um es per Manager-Feedback zu aktualisieren.")

    st.markdown("</div>", unsafe_allow_html=True)

    col_action, col_new = st.columns([3, 1])
    with col_action:
        if source_mode == "Neues Profil aus CV":
            action_clicked = st.button(
                "Profil generieren",
                type="primary",
                disabled=uploaded_cv is None,
                use_container_width=True,
            )
        else:
            action_clicked = st.button(
                "Profil aus PPTX laden",
                type="primary",
                disabled=uploaded_pptx is None,
                use_container_width=True,
            )
    with col_new:
        if st.button("Neue Session", use_container_width=True, type="secondary"):
            reset_session()
            st.rerun()

    if action_clicked and uploaded_cv:
        clear_profile_state()
        cv_path = save_upload_temporarily(uploaded_cv)
        try:
            if opts["photo"]:
                photo_path = save_upload_temporarily(opts["photo"])
                st.session_state.photo_temp_path = str(photo_path)

            st.session_state.cv_raw_text = extract_cv_text(cv_path)
            st.session_state.profile_source = "cv"

            spinner = (
                "LLM extrahiert Daten aus dem hochgeladenen CV…"
                if opts["use_llm"]
                else "Regelbasierte Extraktion aus dem hochgeladenen CV…"
            )
            with st.spinner(spinner):
                try:
                    content, audit = generate_profile(
                        cv_path,
                        domain=opts["domain"],
                        use_llm=opts["use_llm"],
                        strict_template=opts["strict_template"],
                        extra_certificates=opts["certificates"] or None,
                    )
                    audit["cv_filename"] = uploaded_cv.name

                    if opts["position_override"] != "Aus CV ableiten":
                        content.position_level = opts["position_override"]

                    st.session_state.profile_json = content_to_json(content)
                    st.session_state.audit_json = json.dumps(audit, ensure_ascii=False, indent=2)
                    st.session_state.generation_mode = audit.get("generation_mode", "Regelbasiert")
                    st.success(f"Profil erstellt — {audit.get('generation_mode', '')}")
                    if audit.get("education_count", 0) == 0:
                        st.warning(
                            "Abschluss/Zertifikate: 0 Einträge gefunden. "
                            "Prüfen Sie Audit / CV-Text oder aktivieren Sie LLM-Volltext."
                        )
                except Exception as exc:
                    st.error(f"Profil-Generierung fehlgeschlagen: {exc}")
                    st.caption("Tipp: Deaktivieren Sie „LLM verwenden“ für regelbasierte Extraktion ohne API-Key.")
        finally:
            cleanup_temp(cv_path)

    if action_clicked and uploaded_pptx:
        clear_profile_state()
        pptx_path = save_upload_temporarily(uploaded_pptx)
        try:
            with st.spinner("Beraterprofil aus PowerPoint wird gelesen…"):
                content, audit = import_profile_from_pptx(pptx_path)
                st.session_state.profile_json = content_to_json(content)
                st.session_state.audit_json = json.dumps(audit, ensure_ascii=False, indent=2)
                st.session_state.generation_mode = audit.get("generation_mode", "Importiert aus PPTX")
                st.session_state.profile_source = "pptx"
                st.session_state.cv_raw_text = ""
        except Exception as exc:
            st.error(f"PPTX konnte nicht gelesen werden: {exc}")
        finally:
            cleanup_temp(pptx_path)

    if st.session_state.profile_json:
        _render_results(opts, status)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_manager_feedback(opts: dict, status: dict) -> None:
    st.markdown("---")
    st.markdown("#### Schritt 2 — Manager-Feedback (optional)")
    st.caption(
        "Manager kann Kommentare geben. Bei CV-Profilen wird nur das hochgeladene CV als Quelle verwendet."
    )

    manager_comment = st.text_area(
        "Manager-Kommentar",
        placeholder="z.B. Schwerpunkte stärker auf 5G legen, MTN-Projekt hervorheben, Summary kürzer formulieren…",
        height=100,
        key="manager_comment_input",
    )

    needs_cv = st.session_state.profile_source == "cv"
    can_revise = bool(st.session_state.profile_json) and status["active"]
    if needs_cv and not st.session_state.cv_raw_text:
        can_revise = False

    if st.button(
        "Profil mit Feedback aktualisieren",
        type="primary",
        disabled=not manager_comment.strip() or not can_revise,
        use_container_width=True,
    ):
        try:
            current = content_from_json(st.session_state.profile_json)
            cv_text = st.session_state.cv_raw_text if st.session_state.profile_source == "cv" else None
            with st.spinner("LLM aktualisiert das Profil nach Manager-Feedback…"):
                revised = apply_manager_feedback(
                    current,
                    manager_comment,
                    cv_text=cv_text,
                    extra_certificates=opts["certificates"] or None,
                )
                st.session_state.profile_json = content_to_json(revised)
                st.session_state.manager_history.append(
                    {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "comment": manager_comment.strip(),
                    }
                )
            st.success("Profil aktualisiert.")
            st.rerun()
        except Exception as exc:
            st.error(f"Feedback-Update fehlgeschlagen: {exc}")

    if st.session_state.manager_history:
        with st.expander(f"Feedback-Verlauf ({len(st.session_state.manager_history)})"):
            for entry in st.session_state.manager_history:
                st.markdown(f"**{entry['time']}** — {entry['comment']}")


def _render_results(opts: dict, status: dict) -> None:
    st.markdown("---")
    st.info(f"Aktiver Modus: **{st.session_state.generation_mode}**")

    try:
        content = content_from_json(st.session_state.profile_json)
    except json.JSONDecodeError as exc:
        st.error(f"JSON ungültig: {exc}")
        return

    render_warnings(content.audit_warnings)
    render_preview(content)

    _render_manager_feedback(opts, status)

    with st.expander("JSON bearbeiten", expanded=False):
        edited = st.text_area(
            "Profil-JSON",
            st.session_state.profile_json,
            height=420,
            label_visibility="collapsed",
        )
        st.session_state.profile_json = edited
        try:
            content = content_from_json(edited)
        except json.JSONDecodeError as exc:
            st.error(f"JSON ungültig: {exc}")
            return

    with st.expander("Audit / CV-Text"):
        if st.session_state.cv_raw_text:
            st.text_area(
                "Extrahierter CV-Text (einzige Quelle für diese Session)",
                st.session_state.cv_raw_text,
                height=200,
                disabled=True,
            )
        st.json(json.loads(st.session_state.audit_json) if st.session_state.audit_json else {})

    st.markdown("#### Schritt 3 — PowerPoint exportieren")
    can_export, issues = validate_for_export(content)
    if can_export:
        st.success("Validierung bestanden — bereit für Export")
    else:
        st.error("Validierung fehlgeschlagen")
        for issue in issues:
            st.write(f"- {issue}")

    export_filename = default_export_filename()
    if st.button("PowerPoint erstellen", type="primary", disabled=not can_export):
        photo = Path(st.session_state.photo_temp_path) if st.session_state.photo_temp_path else None
        output = export_pptx(
            content,
            photo_path=photo if photo and photo.exists() else None,
        )
        st.success(f"Erstellt: {output.name}")
        st.download_button(
            "PowerPoint herunterladen",
            data=output.read_bytes(),
            file_name=export_filename,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )
        st.download_button(
            "JSON Audit herunterladen",
            data=st.session_state.audit_json.encode("utf-8"),
            file_name=default_export_filename(suffix=".json"),
            mime="application/json",
            use_container_width=True,
        )


def main() -> None:
    init_env()
    st.set_page_config(
        page_title="Beraterprofil Generator | ORBIT",
        page_icon="◆",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    init_session_state()
    config = load_config()
    status = llm_status()

    col_settings, col_main = st.columns([1, 2.4], gap="large")

    with col_settings:
        opts = render_settings_panel(config)

    with col_main:
        render_main_workflow(opts, status)


if __name__ == "__main__":
    main()
