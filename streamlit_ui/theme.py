"""CivicLens styling for native Streamlit pages."""
import streamlit as st

CIVIC_CSS = """
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    .stApp { background-color: #F8FAFC; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e40af 0%, #2563EB 100%);
    }
    [data-testid="stSidebar"] * { color: #fff !important; }
    [data-testid="stSidebarNav"] a { font-weight: 600; }
    .civic-hero {
        background: linear-gradient(135deg, #2563EB 0%, #1e40af 100%);
        color: white; padding: 2.5rem 2rem; border-radius: 16px;
        text-align: center; margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(37,99,235,0.25);
    }
    .civic-hero h1 { font-size: 2.5rem; font-weight: 900; margin: 0 0 0.5rem; }
    .civic-hero p { font-size: 1.1rem; opacity: 0.95; margin: 0; }
    .civic-kpi {
        border-radius: 12px; padding: 1.25rem; text-align: center; color: white;
        box-shadow: 0 4px 14px rgba(0,0,0,0.12); min-height: 120px;
    }
    .civic-kpi h6 { margin: 0 0 0.35rem; font-size: 0.85rem; opacity: 0.9; }
    .civic-kpi h3 { margin: 0; font-size: 2rem; font-weight: 800; }
    .civic-kpi i { font-size: 1.5rem; opacity: 0.85; margin-bottom: 0.35rem; display: block; }
    .bg-pri { background: linear-gradient(135deg, #2563EB, #1d4ed8); }
    .bg-dan { background: linear-gradient(135deg, #EF4444, #dc2626); }
    .bg-warn { background: linear-gradient(135deg, #F59E0B, #d97706); }
    .bg-ok { background: linear-gradient(135deg, #22C55E, #16a34a); }
    .bg-info { background: linear-gradient(135deg, #06B6D4, #0891b2); }
    .civic-insight {
        background: white; border: 2px solid #E2E8F0; border-radius: 12px;
        padding: 1.25rem; text-align: center; height: 100%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .civic-insight h6 { color: #64748b; font-weight: 700; margin: 0.5rem 0; }
    .civic-insight p { color: #2563EB; font-size: 1.75rem; font-weight: 800; margin: 0; }
    .civic-insight small { color: #94a3b8; }
    .civic-section { font-weight: 700; color: #1E293B; margin: 1.5rem 0 1rem; }
    .civic-card {
        background: white; border: 2px solid #E2E8F0; border-radius: 12px;
        padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] {
        background: white; border: 2px solid #E2E8F0; border-radius: 12px;
        padding: 0.75rem 1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
</style>
"""


def apply_theme():
    st.markdown(CIVIC_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(
        f'<div class="civic-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, icon: str = ""):
    label = f"{icon} {title}".strip()
    st.markdown(f'<p class="civic-section" style="font-size:1.6rem;">{label}</p>', unsafe_allow_html=True)


def kpi_card(col, css_class: str, icon: str, label: str, value):
    col.markdown(
        f'<div class="civic-kpi {css_class}"><i class="fas {icon}"></i>'
        f"<h6>{label}</h6><h3>{value}</h3></div>",
        unsafe_allow_html=True,
    )


def insight_card(col, icon: str, label: str, value, hint: str = ""):
    col.markdown(
        f'<div class="civic-insight"><i class="fas {icon}" style="color:#2563EB;font-size:1.5rem;"></i>'
        f"<h6>{label}</h6><p>{value}</p><small>{hint}</small></div>",
        unsafe_allow_html=True,
    )
