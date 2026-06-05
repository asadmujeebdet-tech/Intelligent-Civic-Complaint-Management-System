import streamlit as st

from backend.app.services.complaint_service import ComplaintService
from backend.app.services.status_history_service import StatusHistoryService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, page_header

st.set_page_config(page_title="Track Status - CivicLens AI", page_icon="🔍", layout="wide")
apply_theme()
page_header("Track Complaint Status", "🔍")

if not ensure_db():
    st.stop()

with st.container(border=True):
    complaint_id = st.text_input("Tracking ID", placeholder="e.g. CL-20240604-ABC123")
    search = st.button("Search", type="primary", use_container_width=True)

if search and complaint_id.strip():
    complaint = ComplaintService.get_complaint(complaint_id.strip())
    if not complaint:
        st.error("Complaint not found. Check the Tracking ID and try again.")
    else:
        st.success(f"Found: **{complaint.get('complaint_id') or complaint['_id']}**")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Status", complaint.get("status", "—"))
        c2.metric("Category", complaint.get("category", "—"))
        c3.metric("Severity", complaint.get("severity", "—"))
        c4.metric("Department", complaint.get("assigned_department") or complaint.get("department") or "—")

        st.markdown("#### Status Timeline")
        history = StatusHistoryService.get_history(complaint["_id"])
        if not history:
            history = [{"status": "Open", "timestamp": complaint.get("created_at"), "updated_by": "citizen"}]

        for h in history:
            ts = h.get("timestamp")
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts)
            st.markdown(f"- **{h.get('status')}** — {ts_str} _(by {h.get('updated_by', 'system')})_")

        if complaint.get("resolution_notes"):
            st.markdown("#### Resolution Notes")
            st.info(complaint["resolution_notes"])
            if complaint.get("updated_at"):
                st.caption(f"Updated: {complaint['updated_at']}")

        status = complaint.get("status", "")
        has_feedback = (complaint.get("feedback") or {}).get("rating")
        if status in ("Resolved", "Closed", "resolved") and not has_feedback:
            st.markdown("#### Rate Your Experience")
            with st.form("feedback_form"):
                rating = st.slider("Rating", 1, 5, 5)
                comment = st.text_area("Comment (optional)")
                if st.form_submit_button("Submit Feedback", type="primary"):
                    ok = ComplaintService.submit_feedback(complaint["_id"], rating, comment)
                    if ok:
                        st.success("Thank you for your feedback!")
                        st.rerun()
                    else:
                        st.error("Could not submit feedback.")
