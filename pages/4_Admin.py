import streamlit as st
from backend.app.database import Database
from backend.app.services.complaint_service import ComplaintService
from backend.app.services.status_history_service import StatusHistoryService

st.set_page_config(page_title="Admin - CivicLens AI", layout="wide")

try:
    Database.connect()
except Exception:
    pass

st.title("🛡️ Admin — Complaint Management")
st.caption("Available to all users")

search = st.text_input("Search ID, text, or location")
status_f = st.selectbox("Status", ["", "Open", "Under Review", "Assigned", "In Progress", "Resolved", "Closed"])
category_f = st.selectbox("Category", ["", "Roads", "Water", "Electricity", "Sanitation", "Traffic", "Public Safety", "Environment"])

complaints, total = ComplaintService.get_all_complaints(
    limit=50, search=search or None, status=status_f or None, category=category_f or None
)

st.write(f"Showing {len(complaints)} of {total} complaints")

if complaints:
    options = {f"{c.get('complaint_id', c['_id'][:8])} — {c.get('category')} — {c.get('status')}": c["_id"] for c in complaints}
    selected = st.selectbox("Select complaint", list(options.keys()))
    cid = options[selected]
    complaint = ComplaintService.get_complaint(cid)

    if complaint:
        with st.expander("Complaint Details", expanded=True):
            st.write("**Text:**", complaint.get("text"))
            st.write("**Location:**", complaint.get("location"))
            st.write("**Department:**", complaint.get("assigned_department") or complaint.get("department"))

            history = StatusHistoryService.get_history(cid)
            st.write("**Status History:**")
            for h in history:
                ts = h.get("timestamp")
                ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts)
                st.markdown(f"- {h.get('status')} at {ts_str}")

        st.subheader("Update Complaint")
        status_options = ["Open", "Under Review", "Assigned", "In Progress", "Resolved", "Closed"]
        current = complaint.get("status", "Open")
        if current not in status_options:
            current = "Open"
        new_status = st.selectbox("Status", status_options, index=status_options.index(current))
        dept = st.text_input("Assigned Department", value=complaint.get("assigned_department") or "")
        notes = st.text_area("Resolution Notes", value=complaint.get("resolution_notes") or "")

        if st.button("Save Changes", type="primary"):
            ok = ComplaintService.update_complaint(cid, {
                "status": new_status,
                "assigned_department": dept,
                "resolution_notes": notes,
                "updated_by": "admin",
            })
            if ok:
                st.success("Saved! Details updated — select complaint again to refresh.")
                st.rerun()
            else:
                st.error("Update failed.")
