"""Inject DESIGN.md tokens as Streamlit custom CSS."""

from __future__ import annotations

DESIGN_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
    --orbit-bg: #F1F5F9;
    --orbit-surface: #FFFFFF;
    --orbit-text: #0F172A;
    --orbit-label: #0F172A;
    --orbit-muted: #64748B;
    --orbit-border: #CBD5E1;
    --orbit-input-bg: #FFFFFF;
    --orbit-accent: #0891B2;
    --orbit-accent-2: #06B6D4;
    --orbit-accent-soft: #E0F7FA;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    color: var(--orbit-text);
}

.stApp {
    background: var(--orbit-bg);
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

/* ── Settings column = first column in main layout ── */
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {
    background: transparent;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child h3,
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child strong {
    color: var(--orbit-text) !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-testid="stCaptionContainer"] p {
    color: var(--orbit-muted) !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child label p,
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-testid="stWidgetLabel"] p {
    color: var(--orbit-label) !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid var(--orbit-border) !important;
    border-radius: 10px !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-baseweb="select"] * {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    opacity: 1 !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child textarea {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid var(--orbit-border) !important;
    border-radius: 10px !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child textarea::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child .stCheckbox label span {
    color: #0F172A !important;
    font-weight: 500 !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    border: 1.5px dashed var(--orbit-border) !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-testid="stFileUploader"] * {
    color: #0F172A !important;
}
.block-container div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border-color: var(--orbit-border) !important;
    border-radius: 16px !important;
}

/* ── Settings wrap (legacy) ── */
.orbit-settings-wrap [data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--orbit-surface) !important;
    border-color: var(--orbit-border) !important;
    border-radius: 16px !important;
}
.orbit-settings-wrap h3 {
    color: var(--orbit-text) !important;
}
.orbit-settings-wrap .stCaption,
.orbit-settings-wrap [data-testid="stCaptionContainer"] p {
    color: var(--orbit-muted) !important;
}
.orbit-settings-wrap strong,
.orbit-settings-wrap [data-testid="stMarkdownContainer"] p {
    color: var(--orbit-text) !important;
}
.orbit-settings-wrap label,
.orbit-settings-wrap [data-testid="stWidgetLabel"] p {
    color: var(--orbit-label) !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
}
.orbit-settings-wrap [data-baseweb="select"] > div {
    background-color: var(--orbit-input-bg) !important;
    border: 1.5px solid var(--orbit-border) !important;
    border-radius: 10px !important;
    color: var(--orbit-text) !important;
}
.orbit-settings-wrap [data-baseweb="select"] span,
.orbit-settings-wrap [data-baseweb="select"] div[aria-selected],
.orbit-settings-wrap [data-baseweb="select"] div[value] {
    color: var(--orbit-text) !important;
    -webkit-text-fill-color: var(--orbit-text) !important;
    opacity: 1 !important;
}
.orbit-settings-wrap textarea {
    background: var(--orbit-input-bg) !important;
    color: var(--orbit-text) !important;
    border: 1.5px solid var(--orbit-border) !important;
    border-radius: 10px !important;
}
.orbit-settings-wrap textarea::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}
.orbit-settings-wrap .stCheckbox label span {
    color: var(--orbit-text) !important;
    font-weight: 500 !important;
}
.orbit-settings-wrap [data-testid="stFileUploader"] section {
    background: var(--orbit-input-bg) !important;
    border: 1.5px dashed var(--orbit-border) !important;
}
.orbit-settings-wrap [data-testid="stFileUploader"] span,
.orbit-settings-wrap [data-testid="stFileUploader"] small,
.orbit-settings-wrap [data-testid="stFileUploader"] p,
.orbit-settings-wrap [data-testid="stFileUploader"] button p {
    color: var(--orbit-text) !important;
}

/* ── Settings panel (legacy) ── */
.orbit-settings-panel {
    background: var(--orbit-surface);
    border: 1px solid var(--orbit-border);
    border-radius: 16px;
    padding: 1.25rem 1.35rem;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    position: sticky;
    top: 1rem;
}
.orbit-settings-panel h3 {
    color: var(--orbit-text) !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.2rem 0 !important;
}
.orbit-settings-panel .orbit-caption {
    color: var(--orbit-muted);
    font-size: 0.85rem;
    margin-bottom: 1rem;
}
.orbit-settings-section {
    margin-bottom: 1.1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #E2E8F0;
}
.orbit-settings-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}
.orbit-settings-section-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--orbit-accent);
    margin-bottom: 0.65rem;
}

/* All widgets inside settings panel */
.orbit-settings-panel label,
.orbit-settings-panel [data-testid="stWidgetLabel"] p {
    color: var(--orbit-label) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}
.orbit-settings-panel [data-baseweb="select"] > div {
    background-color: var(--orbit-input-bg) !important;
    border: 1.5px solid var(--orbit-border) !important;
    border-radius: 10px !important;
    color: var(--orbit-text) !important;
    min-height: 42px !important;
}
.orbit-settings-panel [data-baseweb="select"] span,
.orbit-settings-panel [data-baseweb="select"] div {
    color: var(--orbit-text) !important;
    -webkit-text-fill-color: var(--orbit-text) !important;
}
.orbit-settings-panel textarea {
    background: var(--orbit-input-bg) !important;
    color: var(--orbit-text) !important;
    border: 1.5px solid var(--orbit-border) !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
}
.orbit-settings-panel textarea::placeholder {
    color: #94A3B8 !important;
}
.orbit-settings-panel .stCheckbox label span {
    color: var(--orbit-text) !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
}
.orbit-settings-panel [data-testid="stFileUploader"] section {
    background: var(--orbit-input-bg) !important;
    border: 1.5px dashed var(--orbit-border) !important;
    border-radius: 12px !important;
}
.orbit-settings-panel [data-testid="stFileUploader"] span,
.orbit-settings-panel [data-testid="stFileUploader"] small,
.orbit-settings-panel [data-testid="stFileUploader"] p {
    color: var(--orbit-text) !important;
}

/* ── Hero ── */
.orbit-hero {
    background: linear-gradient(120deg, #0F172A 0%, #1E3A5F 45%, #0891B2 100%);
    border-radius: 18px;
    padding: 1.75rem 2rem;
    margin-bottom: 1rem;
    color: #fff;
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.12);
}
.orbit-hero h1 {
    color: #fff !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.35rem 0 !important;
}
.orbit-hero p {
    color: rgba(255,255,255,0.9) !important;
    margin: 0;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* ── Cards ── */
.orbit-card {
    background: var(--orbit-surface);
    border: 1px solid var(--orbit-border);
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 0.85rem;
}
.orbit-card-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--orbit-muted);
    margin-bottom: 0.75rem;
}

/* ── Badges ── */
.orbit-badge {
    display: inline-flex;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.85rem;
}
.orbit-badge-ok { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }
.orbit-badge-warn { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }

/* ── Main upload ── */
.orbit-main-panel [data-testid="stFileUploader"] section {
    border: 2px dashed #CBD5E1 !important;
    border-radius: 14px !important;
    background: #F8FAFC !important;
}
.orbit-main-panel [data-testid="stFileUploader"] span,
.orbit-main-panel [data-testid="stFileUploader"] small {
    color: var(--orbit-muted) !important;
}

/* ── Buttons ── */
.stButton > button[kind="primary"],
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span {
    background: linear-gradient(135deg, #0891B2, #06B6D4) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}
.stButton > button[kind="secondary"],
.stButton > button[kind="secondary"] p {
    background: #FFFFFF !important;
    color: var(--orbit-text) !important;
    border: 1.5px solid var(--orbit-border) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* ── Preview ── */
.orbit-preview-col {
    background: var(--orbit-surface);
    border: 1px solid var(--orbit-border);
    border-radius: 14px;
    padding: 1rem 1.15rem;
    min-height: 280px;
}
.orbit-preview-col strong { color: var(--orbit-accent) !important; }
.orbit-preview-col p, .orbit-preview-col li { color: var(--orbit-text) !important; font-size: 0.9rem; }

.orbit-warning {
    background: #FFFBEB;
    border-left: 4px solid #D97706;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    color: #78350F;
    font-size: 0.88rem;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
"""


def inject_styles() -> None:
    import streamlit as st

    st.markdown(f"<style>{DESIGN_CSS}</style>", unsafe_allow_html=True)
