import pandas as pd
import streamlit as st

from backend.app.services.complaint_service import ComplaintService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, insight_card, kpi_card, page_header

st.set_page_config(page_title="Analytics - CivicLens AI", page_icon="📊", layout="wide")
apply_theme()

h1, h2 = st.columns([5, 1])
with h1:
    page_header("Analytics Dashboard", "📊")
with h2:
    refresh = st.button("🔄 Refresh", use_container_width=True)

if not ensure_db():
    st.stop()

if refresh:
    st.cache_data.clear()

stats = ComplaintService.get_dashboard_stats()

open_c = stats.get("open_complaints", 0)
in_prog = stats.get("in_progress_complaints", 0)
resolved = stats.get("resolved_complaints", 0)
total = stats.get("total_complaints", 0)
resolution_rate = stats.get("resolved_percentage")
if resolution_rate is None:
    resolution_rate = round((resolved / max(total, 1)) * 100)

# KPI row
r1 = st.columns(6)
kpi_card(r1[0], "bg-pri", "fa-clipboard-list", "Total", total)
kpi_card(r1[1], "bg-dan", "fa-folder-open", "Open", open_c)
kpi_card(r1[2], "bg-warn", "fa-spinner", "In Progress", in_prog)
kpi_card(r1[3], "bg-ok", "fa-check-circle", "Resolved", resolved)
kpi_card(r1[4], "bg-dan", "fa-exclamation-triangle", "Critical", stats.get("critical_count", 0))
kpi_card(r1[5], "bg-info", "fa-flag", "High Priority", stats.get("high_priority_count", 0))

st.markdown('<p class="civic-section"><i class="fas fa-lightbulb"></i> Key Insights</p>', unsafe_allow_html=True)
i1, i2, i3, i4 = st.columns(4)
insight_card(i1, "fa-clone", "Duplicate Clusters", stats.get("duplicate_clusters", 0), "grouped reports")
insight_card(i2, "fa-percentage", "Resolution Rate", f"{round(resolution_rate)}%", "complaints resolved")
insight_card(i3, "fa-star", "Citizen Satisfaction", f"{round(stats.get('satisfaction_score', 0))}%", "from feedback")
insight_card(i4, "fa-comments", "Feedback Received", stats.get("feedback_count", 0), "citizen responses")

st.markdown('<p class="civic-section"><i class="fas fa-chart-pie"></i> Analytics Overview</p>', unsafe_allow_html=True)

cat = stats.get("category_breakdown", {})
sev = stats.get("severity_breakdown", {})
locs = stats.get("top_locations", [])
trend = stats.get("complaint_trend", [])

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Category Distribution**")
    if cat:
        st.bar_chart(pd.DataFrame({"Complaints": list(cat.values())}, index=list(cat.keys())))
    else:
        st.caption("No data yet.")
with c2:
    st.markdown("**Severity Breakdown**")
    if sev:
        order = ["Low", "Medium", "High", "Critical"]
        sev_data = {k: sev.get(k, 0) for k in order if sev.get(k, 0)}
        if sev_data:
            st.bar_chart(pd.DataFrame({"Count": list(sev_data.values())}, index=list(sev_data.keys())))
        else:
            st.bar_chart(pd.DataFrame({"Count": list(sev.values())}, index=list(sev.keys())))
    else:
        st.caption("No data yet.")

c3, c4 = st.columns(2)
with c3:
    st.markdown("**Top Locations**")
    if locs:
        labels = [l.get("location", "Unknown") for l in locs]
        counts = [l.get("count", 0) for l in locs]
        st.bar_chart(pd.DataFrame({"Complaints": counts}, index=labels))
    else:
        st.caption("No location data yet.")
with c4:
    st.markdown("**Status Overview**")
    status_data = stats.get("status_breakdown") or {
        "Open": open_c,
        "In Progress": in_prog,
        "Resolved": resolved,
    }
    if status_data:
        st.bar_chart(pd.DataFrame({"Count": list(status_data.values())}, index=list(status_data.keys())))
    else:
        st.caption("No data yet.")

st.markdown("**Complaint Trend (Last 7 Days)**")
if trend:
    tdf = pd.DataFrame(trend)
    if "date" in tdf.columns and "count" in tdf.columns:
        st.line_chart(tdf.set_index("date")["count"])
    else:
        st.line_chart(tdf)
else:
    st.caption("No trend data yet.")
