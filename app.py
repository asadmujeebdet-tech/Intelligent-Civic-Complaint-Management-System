"""
CivicLens AI — Streamlit Cloud entry point

Deploy:  streamlit run app.py  (or Streamlit Cloud main file: app.py)
Local API + HTML UI:  python run_server.py
"""
import sys

if "streamlit" in sys.modules:
    import streamlit as st

    from streamlit_ui.db import ensure_db
    from streamlit_ui.theme import apply_theme, hero, insight_card, kpi_card

    st.set_page_config(
        page_title="CivicLens AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()

    hero(
        "CivicLens AI",
        "Intelligent Civic Complaint Management System",
    )

    st.markdown(
        "Empowering citizens to report civic issues with AI-powered analysis and government action."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📝 Report Issue", type="primary", use_container_width=True):
            st.switch_page("pages/1_Report_Issue.py")
    with c2:
        if st.button("📊 Analytics", use_container_width=True):
            st.switch_page("pages/3_Analytics.py")
    with c3:
        if st.button("🛡️ Admin", use_container_width=True):
            st.switch_page("pages/4_Admin.py")

    st.markdown('<p class="civic-section">Live Overview</p>', unsafe_allow_html=True)

    if ensure_db():
        from backend.app.services.complaint_service import ComplaintService

        stats = ComplaintService.get_dashboard_stats()
        total = stats.get("total_complaints", 0)
        resolved = stats.get("resolved_complaints", 0)
        open_c = stats.get("open_complaints", 0)
        in_prog = stats.get("in_progress_complaints", 0)
        rate = round(stats.get("resolved_percentage") or (resolved / max(total, 1) * 100))

        c1, c2, c3 = st.columns(3)
        kpi_card(c1, "bg-pri", "fa-clipboard-list", "Total Complaints", total)
        kpi_card(c2, "bg-ok", "fa-check-circle", "Resolved Cases", resolved)
        kpi_card(c3, "bg-warn", "fa-spinner", "Active Issues", open_c + in_prog)

        st.markdown('<p class="civic-section">Our Features</p>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        insight_card(f1, "fa-robot", "AI-Powered Analysis", "✓", "Classification & severity")
        insight_card(f2, "fa-chart-line", "Real-time Analytics", f"{rate}%", "Resolution rate")
        insight_card(f3, "fa-users", "Citizen Feedback", stats.get("feedback_count", 0), "Ratings received")

elif __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
