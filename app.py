"""Streamlit frontend for ORBIT Beraterprofil generation."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import yaml

from src.web.pipeline import (
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
from src.web.preview import render_hero, render_llm_badge, render_preview, render_warnings
from src.web.settings_panel import render_settings_panel
from src.web.styles import inject_styles

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config" / "domains.yaml"


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def init_session_state() -> None:
    defaults = {
        "profile_json": "",
        "audit_json": "",
        "generation_mode": "",
        "consultant_name": "",
        "cv_temp_path": None,
        "photo_temp_path": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_main_workflow(opts: dict, status: dict) -> None:
    st.markdown('<div class="orbit-main-panel">', unsafe_allow_html=True)

    render_hero()
    render_llm_badge(status["active"], status.get("provider"))

    st.markdown('<div class="orbit-card"><div class="orbit-card-title">CV Upload</div>', unsafe_allow_html=True)
    uploaded_cv = st.file_uploader(
        "Lebenslauf hochladen",
        type=["pdf", "docx", "doc", "txt", "md"],
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col_gen, col_clear = st.columns([3, 1])
    with col_gen:
        generate_clicked = st.button(
            "Profil generieren",
            type="primary",
            disabled=uploaded_cv is None,
            use_container_width=True,
        )
    with col_clear:
        if st.button("Zurücksetzen", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if generate_clicked and uploaded_cv:
        cv_path = save_upload_temporarily(uploaded_cv)
        st.session_state.cv_temp_path = str(cv_path)
        try:
            if opts["photo"]:
                photo_path = save_upload_temporarily(opts["photo"])
                st.session_state.photo_temp_path = str(photo_path)

            with st.spinner("CV wird analysiert und Beraterprofil erstellt…"):
                content, audit = generate_profile(
                    cv_path,
                    domain=opts["domain"],
                    use_llm=opts["use_llm"],
                    strict_template=opts["strict_template"],
                    extra_certificates=opts["certificates"] or None,
                )

                if opts["position_override"] != "Aus CV ableiten":
                    content.position_level = opts["position_override"]

                st.session_state.profile_json = content_to_json(content)
                st.session_state.audit_json = json.dumps(audit, ensure_ascii=False, indent=2)
                st.session_state.consultant_name = audit["parsed_cv"].get("name") or Path(uploaded_cv.name).stem
                mode = "LLM" if opts["use_llm"] and status["active"] else "Regelbasiert"
                if opts["strict_template"]:
                    mode = "Striktes Template"
                st.session_state.generation_mode = mode
        finally:
            cleanup_temp(cv_path)

    if st.session_state.profile_json:
        _render_results()

    st.markdown("</div>", unsafe_allow_html=True)


def _render_results() -> None:
    st.markdown("---")
    st.info(f"Aktiver Modus: **{st.session_state.generation_mode}**")

    try:
        content = content_from_json(st.session_state.profile_json)
    except json.JSONDecodeError as exc:
        st.error(f"JSON ungültig: {exc}")
        return

    render_warnings(content.audit_warnings)
    render_preview(content)

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

    with st.expander("Audit / extrahierte CV-Daten"):
        st.json(json.loads(st.session_state.audit_json) if st.session_state.audit_json else {})

    can_export, issues = validate_for_export(content)
    if can_export:
        st.success("Validierung bestanden — bereit für PowerPoint-Export")
    else:
        st.error("Validierung fehlgeschlagen")
        for issue in issues:
            st.write(f"- {issue}")

    if st.button("PowerPoint erstellen", type="primary", disabled=not can_export):
        photo = Path(st.session_state.photo_temp_path) if st.session_state.photo_temp_path else None
        output = export_pptx(
            content,
            photo_path=photo if photo and photo.exists() else None,
            output_name=st.session_state.consultant_name or "Beraterprofil",
        )
        st.success(f"Erstellt: {output.name}")
        st.download_button(
            "PowerPoint herunterladen",
            data=output.read_bytes(),
            file_name=output.name,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )
        st.download_button(
            "JSON Audit herunterladen",
            data=st.session_state.audit_json.encode("utf-8"),
            file_name=output.with_suffix(".json").name,
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
