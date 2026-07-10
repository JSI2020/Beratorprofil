"""Settings panel for the Streamlit app."""

from __future__ import annotations

import streamlit as st

from src.web.pipeline import llm_status


def render_settings_panel(config: dict) -> dict:
    """Left settings column."""
    with st.container(border=True):
        st.markdown("### Einstellungen")
        st.caption("Profil-Optionen für diesen Lebenslauf")

        status = llm_status()
        if status["active"]:
            st.success(f"LLM aktiv · {status['provider']}")
        else:
            st.info("Kein LLM API-Key — Regelbasierte Generierung verfügbar.")

        st.markdown("**Profil**")
        domain_options = ["Automatisch erkennen"] + config.get("domains", [])
        domain_choice = st.selectbox("Fachgebiet", domain_options)
        domain = None if domain_choice == "Automatisch erkennen" else domain_choice

        position_levels = config.get("position_levels", ["Consultant", "Senior Consultant"])
        position_override = st.selectbox("Position (optional)", ["Aus CV ableiten"] + position_levels)

        st.markdown("**Generierung**")
        use_llm = st.checkbox(
            "LLM verwenden",
            value=llm_status()["active"],
            help="Ohne LLM: regelbasierte Extraktion nur aus dem hochgeladenen CV",
        )
        strict_template = st.checkbox(
            "Striktes ORBIT-Template",
            value=False,
            help="ORBIT-Mustertexte statt LLM-personalisiertem Inhalt",
        )

        st.markdown("**Optional**")
        cert_input = st.text_area(
            "Zertifikate",
            placeholder="2026, PSM I, Scrum.org",
            height=88,
            help="Eine Zeile pro Zertifikat",
        )
        certificates = [line.strip() for line in cert_input.splitlines() if line.strip()]

        photo = st.file_uploader("Beraterfoto", type=["jpg", "jpeg", "png"])

    return {
        "domain": domain,
        "position_override": position_override,
        "use_llm": use_llm,
        "strict_template": strict_template,
        "certificates": certificates,
        "photo": photo,
    }
