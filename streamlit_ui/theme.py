"""CivicLens styling — matches the HTML frontend palette."""
import streamlit as st

CSS = """
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e40af 0%, #2563EB 100%);
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span { color: #fff !important; }
    [data-testid="stSidebarNav"] a { font-weight: 600; color: #fff !important; }
    .civic-hero {
        background: linear-gradient(135deg, #2563EB 0%, #1e40af 100%);
        color: white; padding: 2.5rem 1.5rem; border-radius: 16px;
        text-align: center; margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(37,99,235,0.25);
    }
    .civic-hero h1 { font-size: 2.4rem; font-weight: 900; margin: 0 0 0.5rem; }
    .civic-hero p { font-size: 1.1rem; opacity: 0.95; margin: 0; }
    .civic-kpi {
        border-radius: 12px; padding: 1.2rem; text-align: center; color: white;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12); min-height: 110px;
    }
    .civic-kpi h6 { margin: 0 0 0.3rem; font-size: 0.85rem; opacity: 0.9; }
    .civic-kpi h3 { margin: 0; font-size: 1.9rem; font-weight: 800; }
    .civic-kpi i { font-size: 1.4rem; opacity: 0.85; display: block; margin-bottom: 0.3rem; }
    .bg-pri { background: linear-gradient(135deg, #2563EB, #1d4ed8); }
    .bg-dan { background: linear-gradient(135deg, #EF4444, #dc2626); }
    .bg-warn { background: linear-gradient(135deg, #F59E0B, #d97706); }
    .bg-ok { background: linear-gradient(135deg, #22C55E, #16a34a); }
    .bg-info { background: linear-gradient(135deg, #06B6D4, #0891b2); }
    .civic-insight {
        background: white; border: 2px solid #E2E8F0; border-radius: 12px;
        padding: 1.2rem; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .civic-insight h6 { color: #64748b; font-weight: 700; margin: 0.4rem 0; }
    .civic-insight p { color: #2563EB; font-size: 1.6rem; font-weight: 800; margin: 0; }
    .civic-insight small { color: #94a3b8; }
    .civic-h { font-weight: 800; color: #1E293B; font-size: 1.5rem; margin: 1rem 0; }
    div[data-testid="stMetric"] {
        background: white; border: 2px solid #E2E8F0; border-radius: 12px;
        padding: 0.6rem 1rem;
    }
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(
        f'<div class="civic-hero"><h1><i class="fas fa-landmark"></i> {title}</h1>'
        f"<p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def page_title(text: str, icon: str = ""):
    label = f'<i class="fas {icon}"></i> {text}' if icon else text
    st.markdown(f'<p class="civic-h">{label}</p>', unsafe_allow_html=True)


def kpi(col, css: str, icon: str, label: str, value):
    col.markdown(
        f'<div class="civic-kpi {css}"><i class="fas {icon}"></i>'
        f"<h6>{label}</h6><h3>{value}</h3></div>",
        unsafe_allow_html=True,
    )


def insight(col, icon: str, label: str, value, hint: str = ""):
    col.markdown(
        f'<div class="civic-insight"><i class="fas {icon}" style="color:#2563EB;font-size:1.4rem;"></i>'
        f"<h6>{label}</h6><p>{value}</p><small>{hint}</small></div>",
        unsafe_allow_html=True,
    )
