import streamlit as st
from backend.app.database import Database
from backend.app.services.complaint_service import ComplaintService
from backend.app.services.status_history_service import StatusHistoryService

st.set_page_config(page_title="Track Status - CivicLens AI", layout="wide")

try:
    Database.connect()
except Exception:
    pass

st.title("🔍 Track Complaint")
complaint_id = st.text_input("Enter Tracking ID (e.g. CL-20240604-ABC123)")

if st.button("Search", type="primary") and complaint_id.strip():
    complaint = ComplaintService.get_complaint(complaint_id.strip())
    if not complaint:
        st.error("Complaint not found.")
    else:
        st.success(f"Tracking ID: {complaint.get('complaint_id') or complaint['_id']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Status", complaint.get("status"))
        c2.metric("Category", complaint.get("category"))
        c3.metric("Severity", complaint.get("severity"))

        st.subheader("Status Timeline")
        history = StatusHistoryService.get_history(complaint["_id"])
        if not history:
            history = [{"status": "Open", "timestamp": complaint.get("created_at"), "updated_by": "citizen"}]
        for h in history:
            ts = h.get("timestamp")
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts)
            st.markdown(f"**{h.get('status')}** — {ts_str} (by {h.get('updated_by', 'system')})")

        if complaint.get("resolution_notes"):
            st.subheader("Resolution Notes")
            st.write(complaint["resolution_notes"])
            if complaint.get("updated_at"):
                st.caption(f"Updated: {complaint['updated_at']}")

        if complaint.get("status") in ("Resolved", "Closed", "resolved") and not (complaint.get("feedback") or {}).get("rating"):
            st.subheader("Rate Your Experience")
            rating = st.slider("Rating", 1, 5, 5)
            comment = st.text_area("Comment")
            if st.button("Submit Feedback"):
                ok = ComplaintService.submit_feedback(complaint["_id"], rating, comment)
                st.success("Thank you!") if ok else st.error("Could not submit feedback.")
