import streamlit as st
from backend.app.database import Database
from backend.app.services.complaint_service import ComplaintService
from backend.app.services.insights_service import InsightsService

st.set_page_config(page_title="Analytics - CivicLens AI", layout="wide")

try:
    Database.connect()
except Exception:
    pass

st.title("📊 Analytics Dashboard")
stats = ComplaintService.get_dashboard_stats()

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total", stats.get("total_complaints", 0))
c2.metric("Open", stats.get("open_complaints", 0))
c3.metric("Resolved", stats.get("resolved_complaints", 0))
c4.metric("Critical", stats.get("critical_count", 0))
c5.metric("Duplicates", stats.get("duplicate_complaints", 0))
c6.metric("Satisfaction", f"{stats.get('satisfaction_score', 0)}%")

st.subheader("Category Breakdown")
st.bar_chart(stats.get("category_breakdown", {}))

st.subheader("AI Civic Insights")
insights = InsightsService.generate_insights()
st.json(insights)
