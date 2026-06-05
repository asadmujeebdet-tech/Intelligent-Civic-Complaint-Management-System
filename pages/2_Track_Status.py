import logging

import streamlit as st

from backend.app.services.complaint_service import ComplaintService
from backend.app.services.status_history_service import StatusHistoryService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, page_title

logger = logging.getLogger("civiclens.track")

st.set_page_config(page_title="Track Status", page_icon="🔍", layout="wide")
apply_theme()
page_title("Track Complaint", "fa-search")

if not ensure_db():
    st.stop()

with st.container(border=True):
    cid = st.text_input("Tracking ID", placeholder="e.g. CL-20240604-ABC123")
    go = st.button("Search", type="primary", use_container_width=True)

if go and cid.strip():
    try:
        complaint = ComplaintService.get_complaint(cid.strip())
        if not complaint:
            st.error("Complaint not found.")
        else:
            st.success(f"**{complaint.get('complaint_id') or complaint['_id']}**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status", complaint.get("status", "—"))
            c2.metric("Category", complaint.get("category", "—"))
            c3.metric("Severity", complaint.get("severity", "—"))
            c4.metric("Department", complaint.get("assigned_department") or "—")

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

            status = str(complaint.get("status", ""))
            has_fb = (complaint.get("feedback") or {}).get("rating")
            if status in ("Resolved", "Closed", "resolved") and not has_fb:
                st.markdown("#### Rate Your Experience")
                with st.form("feedback"):
                    rating = st.slider("Rating", 1, 5, 5)
                    comment = st.text_area("Comment")
                    if st.form_submit_button("Submit Feedback", type="primary"):
                        ok = ComplaintService.submit_feedback(complaint["_id"], rating, comment)
                        st.success("Thank you!") if ok else st.error("Could not submit feedback.")
                        if ok:
                            st.rerun()
    except Exception as exc:
        logger.exception("Track failed")
        st.error("Service temporarily unavailable.")
        st.caption(str(exc))
