import streamlit as st

from backend.app.models.complaint import ComplaintCreate
from backend.app.services.complaint_service import ComplaintService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, page_header

st.set_page_config(page_title="Report Issue - CivicLens AI", page_icon="📝", layout="wide")
apply_theme()
page_header("Report a Civic Issue", "📝")

if not ensure_db():
    st.stop()

with st.container(border=True):
    text = st.text_area("Complaint Description *", height=150, placeholder="Describe the civic issue in detail…")
    location = st.text_input("Location *", placeholder="Street, area, or landmark")
    c1, c2 = st.columns(2)
    with c1:
        language = st.selectbox("Language", ["", "English", "Urdu", "Roman Urdu"])
    with c2:
        category = st.selectbox(
            "Category (optional)",
            ["", "Roads", "Water", "Electricity", "Sanitation", "Traffic", "Public Safety", "Environment"],
        )

    if st.button("Submit Complaint", type="primary", use_container_width=True):
        if len(text.strip()) < 10:
            st.error("Description must be at least 10 characters.")
        elif not location.strip():
            st.error("Location is required.")
        else:
            try:
                data = ComplaintCreate(
                    text=text.strip(),
                    location=location.strip(),
                    language=language or None,
                    category=category or None,
                )
                result = ComplaintService.create_complaint(data)
                st.success("Complaint submitted successfully!")
                tracking_id = result.get("complaint_id") or result.get("_id")
                st.code(tracking_id, language=None)
                st.info("Save this Tracking ID to check status on the **Track Status** page.")
            except Exception as exc:
                st.error(str(exc))
