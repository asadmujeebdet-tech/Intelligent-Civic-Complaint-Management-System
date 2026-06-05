"""
CivicLens AI — main entry point

Run Streamlit (deploy):  streamlit run app.py
Run API + HTML UI:       python run_server.py
"""
import sys

# ---------------------------------------------------------------------------
# Streamlit mode — executed when: streamlit run app.py
# ---------------------------------------------------------------------------
if "streamlit" in sys.modules:
    import streamlit as st

    st.set_page_config(
        page_title="CivicLens AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    @st.cache_resource
    def init_database():
        from backend.app.database import Database
        Database.connect()
        return True

    try:
        init_database()
        db_ok = True
    except Exception as e:
        db_ok = False
        st.sidebar.error(f"Database: {e}")

    st.title("CivicLens AI")
    st.subheader("Intelligent Civic Complaint Management System")

    col1, col2, col3 = st.columns(3)
    if db_ok:
        from backend.app.services.complaint_service import ComplaintService
        stats = ComplaintService.get_dashboard_stats()
        col1.metric("Total Complaints", stats.get("total_complaints", 0))
        col2.metric("Open", stats.get("open_complaints", 0))
        col3.metric("Resolved", stats.get("resolved_complaints", 0))
    else:
        col1.metric("Total Complaints", "—")
        col2.metric("Open", "—")
        col3.metric("Resolved", "—")

    st.markdown("""
    ### Welcome
    Use the **sidebar** to navigate — Home, Report Issue, Track Status, Analytics, and Admin.

    | Page | Description |
    |------|-------------|
    | Report Issue | Submit a civic complaint with AI classification |
    | Track Status | Track complaint by ID and submit feedback |
    | Analytics | Dashboard with KPIs, charts, and AI insights |
    | Admin | Manage complaints, update status, view details |
    """)

    st.info("For the full HTML UI locally: `python run_server.py` → http://localhost:8000")

# ---------------------------------------------------------------------------
# API server mode — executed when: python app.py  (or python run_server.py)
# ---------------------------------------------------------------------------
elif __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
