"""
CivicLens AI — Streamlit Cloud (standalone, no Render)

Deploy: streamlit run app.py
Local HTML UI: python run_server.py
"""
import logging
import sys

logging.basicConfig(level=logging.INFO)

if "streamlit" in sys.modules:
    import streamlit as st

    from backend.app.services.complaint_service import ComplaintService
    from streamlit_ui.db import ensure_db
    from streamlit_ui.theme import apply_theme, hero, insight, kpi

    st.set_page_config(
        page_title="CivicLens AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    hero("CivicLens AI", "Intelligent Civic Complaint Management System")

    if not ensure_db():
        st.stop()

    try:
        stats = ComplaintService.get_dashboard_stats()
        total = stats.get("total_complaints", 0)
        resolved = stats.get("resolved_complaints", 0)
        open_c = stats.get("open_complaints", 0)
        in_prog = stats.get("in_progress_complaints", 0)
        rate = round(stats.get("resolved_percentage") or (resolved / max(total, 1) * 100))

        c1, c2, c3 = st.columns(3)
        kpi(c1, "bg-pri", "fa-clipboard-list", "Total Complaints", total)
        kpi(c2, "bg-ok", "fa-check-circle", "Resolved", resolved)
        kpi(c3, "bg-warn", "fa-spinner", "Active Issues", open_c + in_prog)

        st.markdown('<p class="civic-h">Quick Actions</p>', unsafe_allow_html=True)
        a1, a2, a3 = st.columns(3)
        with a1:
            if st.button("📝 Report Issue", type="primary", use_container_width=True):
                st.switch_page("pages/1_Report_Issue.py")
        with a2:
            if st.button("🔍 Track Status", use_container_width=True):
                st.switch_page("pages/2_Track_Status.py")
        with a3:
            if st.button("📊 Analytics", use_container_width=True):
                st.switch_page("pages/3_Analytics.py")

        st.markdown('<p class="civic-h">Key Insights</p>', unsafe_allow_html=True)
        i1, i2, i3 = st.columns(3)
        insight(i1, "fa-chart-line", "Resolution Rate", f"{rate}%", "complaints resolved")
        insight(i2, "fa-star", "Satisfaction", f"{round(stats.get('satisfaction_score', 0))}%", "citizen feedback")
        insight(i3, "fa-comments", "Feedback", stats.get("feedback_count", 0), "responses received")

    except Exception:
        st.error("Service temporarily unavailable.")

elif __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
