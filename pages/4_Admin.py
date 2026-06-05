import logging

import streamlit as st

from backend.app.services.complaint_service import ComplaintService
from backend.app.services.status_history_service import StatusHistoryService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, page_title

logger = logging.getLogger("civiclens.admin")

st.set_page_config(page_title="Admin", page_icon="🛡️", layout="wide")
apply_theme()
page_title("Admin — Complaint Management", "fa-shield-alt")

if not ensure_db():
    st.stop()

try:
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            search = st.text_input("Search")
        with c2:
            status_f = st.selectbox("Status", ["", "Open", "Under Review", "Assigned", "In Progress", "Resolved", "Closed"])
        with c3:
            category_f = st.selectbox("Category", ["", "Roads", "Water", "Electricity", "Sanitation", "Traffic", "Public Safety", "Environment"])

    complaints, total = ComplaintService.get_all_complaints(
        limit=50, search=search or None, status=status_f or None, category=category_f or None,
    )
    st.caption(f"Showing {len(complaints)} of {total}")

    if not complaints:
        st.info("No complaints found.")
        st.stop()

    opts = {f"{c.get('complaint_id', c['_id'][:8])} — {c.get('category')} — {c.get('status')}": c["_id"] for c in complaints}
    sel = st.selectbox("Select complaint", list(opts.keys()))
    cid = opts[sel]
    complaint = ComplaintService.get_complaint(cid)

    if complaint:
        with st.expander("Details", expanded=True):
            st.write(complaint.get("text"))
            st.write(f"**Location:** {complaint.get('location')}")
            for h in StatusHistoryService.get_history(cid):
                ts = h.get("timestamp")
                ts_str = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, "strftime") else str(ts)
                st.markdown(f"- {h.get('status')} at {ts_str}")

        opts_s = ["Open", "Under Review", "Assigned", "In Progress", "Resolved", "Closed"]
        cur = complaint.get("status", "Open")
        if cur not in opts_s:
            cur = "Open"
        with st.form("update"):
            new_s = st.selectbox("Status", opts_s, index=opts_s.index(cur))
            dept = st.text_input("Department", value=complaint.get("assigned_department") or "")
            notes = st.text_area("Resolution Notes", value=complaint.get("resolution_notes") or "")
            if st.form_submit_button("Save", type="primary"):
                ok = ComplaintService.update_complaint(cid, {
                    "status": new_s, "assigned_department": dept,
                    "resolution_notes": notes, "updated_by": "admin",
                })
                st.success("Saved!") if ok else st.error("Update failed.")
                if ok:
                    st.rerun()
except Exception as exc:
    logger.exception("Admin failed")
    st.error("Service temporarily unavailable.")
    st.caption(str(exc))
