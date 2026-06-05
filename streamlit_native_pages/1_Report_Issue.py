import streamlit as st
from backend.app.database import Database
from backend.app.models.complaint import ComplaintCreate
from backend.app.services.complaint_service import ComplaintService

st.set_page_config(page_title="Report Issue - CivicLens AI", layout="wide")

try:
    Database.connect()
except Exception:
    pass

st.title("📝 Report a Civic Issue")
text = st.text_area("Complaint Description", min_chars=10, height=150)
location = st.text_input("Location")
language = st.selectbox("Language", ["", "English", "Urdu", "Roman Urdu"])
category = st.selectbox("Category (optional)", ["", "Roads", "Water", "Electricity", "Sanitation", "Traffic", "Public Safety", "Environment"])

if st.button("Submit Complaint", type="primary"):
    if len(text.strip()) < 10:
        st.error("Description must be at least 10 characters.")
    elif not location.strip():
        st.error("Location is required.")
    else:
        try:
            data = ComplaintCreate(text=text.strip(), location=location.strip(), language=language or None, category=category or None)
            result = ComplaintService.create_complaint(data)
            st.success("Complaint submitted!")
            st.code(result.get("complaint_id") or result.get("_id"), language=None)
            st.info("Save this Tracking ID to check status later.")
        except Exception as e:
            st.error(str(e))
