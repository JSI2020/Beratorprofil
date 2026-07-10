"""Three-column profile preview for Streamlit."""

from __future__ import annotations

import streamlit as st

from src.models.schemas import BeraterprofilContent


def render_hero() -> None:
    st.markdown(
        """
        <div class="orbit-hero">
            <h1>Beraterprofil Generator</h1>
            <p>Laden Sie einen Lebenslauf hoch — die KI erstellt eine personalisierte
            ORBIT-Einseiter-Präsentation. Funktioniert für jeden Berater.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_llm_badge(active: bool, provider: str | None = None) -> None:
    if active:
        label = f"● LLM aktiv — {provider}" if provider else "● LLM aktiv"
        st.markdown(f'<span class="orbit-badge orbit-badge-ok">{label}</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<span class="orbit-badge orbit-badge-warn">● Offline — regelbasierte Generierung</span>',
            unsafe_allow_html=True,
        )


def render_warnings(warnings: list[str]) -> None:
    if not warnings:
        return
    st.markdown("#### Hinweise zur Prüfung")
    for warning in warnings:
        st.markdown(f'<div class="orbit-warning">{warning}</div>', unsafe_allow_html=True)


def render_preview(content: BeraterprofilContent) -> None:
    st.markdown("#### Vorschau — Einseiten-Inhalt")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="orbit-preview-col">', unsafe_allow_html=True)
        st.markdown(f"**{content.title}**")
        st.markdown(f"**Position** · {content.position_level}")
        st.markdown(f"**Schwerpunkte** · {content.schwerpunkte}")
        st.markdown("**Summary**")
        st.markdown(content.summary)
        st.markdown("**Kompetenzen**")
        if content.kompetenzen:
            st.markdown(
                "<ul>" + "".join(f"<li>{k}</li>" for k in content.kompetenzen) + "</ul>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="orbit-preview-col">', unsafe_allow_html=True)
        st.markdown("**Relevante Erfahrungen**")
        for item in content.relevante_erfahrungen:
            st.markdown(f"**{item.category}** — {item.details}")
        st.markdown("**Tool-Kenntnisse**")
        for cat in content.tool_categories:
            tools = ", ".join(cat.tools)
            if tools:
                st.markdown(f"**{cat.category}** — {tools}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="orbit-preview-col">', unsafe_allow_html=True)
        st.markdown("**Ausbildung / Karriere**")
        for line in content.international_experience:
            st.markdown(f"- {line}")
        st.markdown("**Abschluss / Zertifikate**")
        for line in content.education_certificates:
            st.markdown(f"- {line}")
        st.markdown("</div>", unsafe_allow_html=True)
