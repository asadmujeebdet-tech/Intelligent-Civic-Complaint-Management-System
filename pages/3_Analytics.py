import logging

import pandas as pd
import streamlit as st

from backend.app.services.complaint_service import ComplaintService
from streamlit_ui.db import ensure_db
from streamlit_ui.theme import apply_theme, insight, kpi, page_title

logger = logging.getLogger("civiclens.analytics")

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")
apply_theme()

h1, h2 = st.columns([5, 1])
with h1:
    page_title("Analytics Dashboard", "fa-chart-line")
with h2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if not ensure_db():
    st.stop()

try:
    stats = ComplaintService.get_dashboard_stats()
    open_c = stats.get("open_complaints", 0)
    in_prog = stats.get("in_progress_complaints", 0)
    resolved = stats.get("resolved_complaints", 0)
    total = stats.get("total_complaints", 0)
    rate = stats.get("resolved_percentage") or round((resolved / max(total, 1)) * 100)

    r1 = st.columns(6)
    kpi(r1[0], "bg-pri", "fa-clipboard-list", "Total", total)
    kpi(r1[1], "bg-dan", "fa-folder-open", "Open", open_c)
    kpi(r1[2], "bg-warn", "fa-spinner", "In Progress", in_prog)
    kpi(r1[3], "bg-ok", "fa-check-circle", "Resolved", resolved)
    kpi(r1[4], "bg-dan", "fa-exclamation-triangle", "Critical", stats.get("critical_count", 0))
    kpi(r1[5], "bg-info", "fa-flag", "High Priority", stats.get("high_priority_count", 0))

    i1, i2, i3, i4 = st.columns(4)
    insight(i1, "fa-clone", "Duplicates", stats.get("duplicate_clusters", 0), "grouped reports")
    insight(i2, "fa-percentage", "Resolution Rate", f"{round(rate)}%", "")
    insight(i3, "fa-star", "Satisfaction", f"{round(stats.get('satisfaction_score', 0))}%", "")
    insight(i4, "fa-comments", "Feedback", stats.get("feedback_count", 0), "")

    c1, c2 = st.columns(2)
    cat = stats.get("category_breakdown", {})
    sev = stats.get("severity_breakdown", {})
    with c1:
        st.markdown("**Category Distribution**")
        if cat:
            st.bar_chart(pd.DataFrame({"Count": list(cat.values())}, index=list(cat.keys())))
    with c2:
        st.markdown("**Severity Breakdown**")
        if sev:
            st.bar_chart(pd.DataFrame({"Count": list(sev.values())}, index=list(sev.keys())))

    c3, c4 = st.columns(2)
    locs = stats.get("top_locations", [])
    with c3:
        st.markdown("**Top Locations**")
        if locs:
            st.bar_chart(pd.DataFrame(
                {"Count": [l.get("count", 0) for l in locs]},
                index=[l.get("location", "?") for l in locs],
            ))
    with c4:
        st.markdown("**Status Overview**")
        status = stats.get("status_breakdown") or {"Open": open_c, "In Progress": in_prog, "Resolved": resolved}
        st.bar_chart(pd.DataFrame({"Count": list(status.values())}, index=list(status.keys())))

    trend = stats.get("complaint_trend", [])
    st.markdown("**Complaint Trend (7 days)**")
    if trend:
        tdf = pd.DataFrame(trend)
        if "date" in tdf.columns:
            st.line_chart(tdf.set_index("date")["count"])
        else:
            st.line_chart(tdf)

except Exception as exc:
    logger.exception("Analytics failed")
    st.error("Service temporarily unavailable.")
    st.caption(str(exc))
