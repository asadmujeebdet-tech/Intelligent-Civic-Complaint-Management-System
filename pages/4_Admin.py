import streamlit as st

from backend.app.services.complaint_service import ComplaintService
from backend.app.services.status_history_service import StatusHistoryService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, page_header

st.set_page_config(page_title="Admin - CivicLens AI", page_icon="🛡️", layout="wide")
apply_theme()
page_header("Admin — Complaint Management", "🛡️")
st.caption("Manage complaints, update status, and add resolution notes.")

if not ensure_db():
    st.stop()

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        search = st.text_input("Search", placeholder="ID, text, or location")
    with c2:
        status_f = st.selectbox("Status", ["", "Open", "Under Review", "Assigned", "In Progress", "Resolved", "Closed"])
    with c3:
        category_f = st.selectbox(
            "Category",
            ["", "Roads", "Water", "Electricity", "Sanitation", "Traffic", "Public Safety", "Environment"],
        )

complaints, total = ComplaintService.get_all_complaints(
    limit=50,
    search=search or None,
    status=status_f or None,
    category=category_f or None,
)

st.write(f"Showing **{len(complaints)}** of **{total}** complaints")

if not complaints:
    st.info("No complaints match your filters.")
    st.stop()

options = {
    f"{c.get('complaint_id', c['_id'][:8])} — {c.get('category')} — {c.get('status')}": c["_id"]
    for c in complaints
}
selected = st.selectbox("Select complaint", list(options.keys()))
cid = options[selected]
complaint = ComplaintService.get_complaint(cid)

if not complaint:
    st.error("Could not load complaint.")
    st.stop()

with st.expander("Complaint Details", expanded=True):
    st.write("**Description:**", complaint.get("text"))
    st.write("**Location:**", complaint.get("location"))
    st.write("**Category / Severity:**", complaint.get("category"), "/", complaint.get("severity"))
    st.write("**Department:**", complaint.get("assigned_department") or complaint.get("department") or "—")

    history = StatusHistoryService.get_history(cid)
    if history:
        st.markdown("**Status History**")
        for h in history:
            ts = h.get("timestamp")
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if hasattr(ts, "strftime") else str(ts)
            st.markdown(f"- {h.get('status')} at {ts_str}")

st.markdown("#### Update Complaint")
status_options = ["Open", "Under Review", "Assigned", "In Progress", "Resolved", "Closed"]
current = complaint.get("status", "Open")
if current not in status_options:
    current = "Open"

with st.form("admin_update"):
    new_status = st.selectbox("Status", status_options, index=status_options.index(current))
    dept = st.text_input("Assigned Department", value=complaint.get("assigned_department") or "")
    notes = st.text_area("Resolution Notes", value=complaint.get("resolution_notes") or "", height=120)
    save = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

if save:
    ok = ComplaintService.update_complaint(
        cid,
        {
            "status": new_status,
            "assigned_department": dept,
            "resolution_notes": notes,
            "updated_by": "admin",
        },
    )
    if ok:
        st.success("Saved successfully!")
        st.rerun()
    else:
        st.error("Update failed.")
