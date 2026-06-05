import asyncio
import logging

import streamlit as st

from backend.app.models.complaint import ComplaintCreate
from backend.app.services.complaint_service import ComplaintService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, page_title

logger = logging.getLogger("civiclens.report")

st.set_page_config(page_title="Report Issue", page_icon="📝", layout="wide")
apply_theme()
page_title("Report a Civic Issue", "fa-plus-circle")

if not ensure_db():
    st.stop()

with st.container(border=True):
    text = st.text_area("Complaint Description *", height=150, placeholder="Describe the issue…")
    location = st.text_input("Location *", placeholder="Street, area, or landmark")

    if len(location.strip()) >= 3:
        try:
            from backend.app.services.maps_service import MapsService

            result = asyncio.run(MapsService.autocomplete(location.strip()))
            suggestions = result.get("data") or result.get("suggestions") or []
            if suggestions:
                labels = [s.get("description", s.get("main_text", "")) for s in suggestions[:6]]
                pick = st.selectbox("Location suggestions (Google Maps)", [""] + labels)
                if pick:
                    location = pick
        except Exception as exc:
            logger.warning("Maps autocomplete: %s", exc)

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
                st.success("Complaint submitted!")
                st.code(result.get("complaint_id") or result.get("_id"))
                st.info("Save this Tracking ID for **Track Status**.")
            except Exception as exc:
                logger.exception("Submit failed")
                st.error("Service temporarily unavailable.")
                st.caption(str(exc))
