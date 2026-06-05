import json
import logging
from datetime import datetime, timedelta

from backend.app.database import get_db
from backend.app.models.complaint import RESOLVED_STATUSES, OPEN_STATUSES
from backend.app.services.ai_service import ai_service
from backend.app.prompts.prompt import (
    build_chatbot_prompt,
    CHATBOT_TEMPERATURE,
    CHATBOT_MAX_OUTPUT_TOKENS,
)

logger = logging.getLogger(__name__)


class ChatbotService:
    """AI analytics chatbot powered by Gemini."""

    @staticmethod
    def _build_context() -> dict:
        db = get_db()
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)

        total = db.complaints.count_documents({})
        today = db.complaints.count_documents({"created_at": {"$gte": today_start}})
        this_month = db.complaints.count_documents({"created_at": {"$gte": month_start}})
        this_week = db.complaints.count_documents({"created_at": {"$gte": week_ago}})

        open_count = db.complaints.count_documents({"status": {"$in": list(OPEN_STATUSES)}})
        in_progress = db.complaints.count_documents({"status": "In Progress"})
        resolved = db.complaints.count_documents({"status": {"$in": list(RESOLVED_STATUSES)}})
        critical = db.complaints.count_documents({"severity": "Critical"})
        unresolved_critical = db.complaints.count_documents({
            "severity": "Critical",
            "status": {"$nin": list(RESOLVED_STATUSES)},
        })

        category_breakdown = {}
        for cat in ["Roads", "Water", "Electricity", "Sanitation", "Traffic", "Public Safety", "Environment"]:
            category_breakdown[cat] = db.complaints.count_documents({"category": cat})

        severity_breakdown = {
            s: db.complaints.count_documents({"severity": s})
            for s in ["Low", "Medium", "High", "Critical"]
        }

        top_locations = list(db.complaints.aggregate([
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]))

        dept_breakdown = list(db.complaints.aggregate([
            {"$group": {"_id": "$assigned_department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]))

        feedback_pipeline = list(db.complaints.aggregate([
            {"$match": {"feedback.rating": {"$ne": None}}},
            {"$group": {"_id": None, "avg_rating": {"$avg": "$feedback.rating"}, "count": {"$sum": 1}}},
        ]))
        avg_rating = round(feedback_pipeline[0]["avg_rating"], 2) if feedback_pipeline else 0
        feedback_count = feedback_pipeline[0]["count"] if feedback_pipeline else 0

        resolution_rate = round((resolved / total * 100), 1) if total > 0 else 0

        return {
            "snapshot_time": now.isoformat(),
            "total_complaints": total,
            "complaints_today": today,
            "complaints_this_week": this_week,
            "complaints_this_month": this_month,
            "open_complaints": open_count,
            "in_progress_complaints": in_progress,
            "resolved_complaints": resolved,
            "resolution_rate_percent": resolution_rate,
            "critical_complaints_total": critical,
            "unresolved_critical_complaints": unresolved_critical,
            "category_breakdown": category_breakdown,
            "severity_breakdown": severity_breakdown,
            "top_locations": [{"location": l["_id"], "count": l["count"]} for l in top_locations],
            "department_workload": [{"department": d["_id"] or "Unassigned", "count": d["count"]} for d in dept_breakdown],
            "average_citizen_rating": avg_rating,
            "feedback_count": feedback_count,
            "satisfaction_percent": round((avg_rating / 5) * 100, 1) if avg_rating else 0,
        }

    @staticmethod
    def chat_with_complaints(question: str) -> str:
        context = ChatbotService._build_context()
        q_lower = question.lower().strip()

        is_report = any(w in q_lower for w in ["report", "summary", "executive", "weekly", "monthly"])
        prompt = build_chatbot_prompt(
            question,
            json.dumps(context, indent=2, default=str),
            is_report=is_report,
        )

        try:
            if ai_service.model:
                try:
                    response = ai_service.model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": CHATBOT_TEMPERATURE,
                            "max_output_tokens": CHATBOT_MAX_OUTPUT_TOKENS,
                        },
                    )
                except TypeError:
                    response = ai_service.model.generate_content(prompt)
                return response.text.strip()
            return ChatbotService._fallback_answer(question, context)
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return ChatbotService._fallback_answer(question, context)

    @staticmethod
    def _fallback_answer(question: str, context: dict) -> str:
        q = question.lower()
        if "report" in q or "summary" in q:
            return (
                f"**Overview**: {context['total_complaints']} total complaints in the system.\n"
                f"**Key Metrics**: {context['open_complaints']} open, {context['resolved_complaints']} resolved "
                f"({context['resolution_rate_percent']}% rate), {context['unresolved_critical_complaints']} unresolved critical.\n"
                f"**Recommendation**: Prioritize critical unresolved cases and top hotspot locations."
            )
        if "today" in q:
            return f"**Summary**: {context['complaints_today']} complaints received today."
        if "week" in q:
            return f"**Summary**: {context['complaints_this_week']} complaints this week."
        if "month" in q:
            return f"**Summary**: {context['complaints_this_month']} complaints this month."
        if "critical" in q:
            return f"**Summary**: {context['critical_complaints_total']} critical total, {context['unresolved_critical_complaints']} still unresolved."
        if "water" in q:
            return f"**Summary**: {context['category_breakdown'].get('Water', 0)} water-related complaints."
        if "category" in q or "top" in q:
            top = max(context["category_breakdown"], key=context["category_breakdown"].get, default="N/A")
            return f"**Summary**: Top category is {top} with {context['category_breakdown'].get(top, 0)} complaints."
        if "area" in q or "location" in q or "hotspot" in q:
            if context["top_locations"]:
                loc = context["top_locations"][0]
                return f"**Summary**: Most affected area is {loc['location']} ({loc['count']} complaints)."
            return "The database has no location data yet."
        if "pending" in q or "open" in q or "unresolved" in q:
            return f"**Summary**: {context['open_complaints']} open, {context['in_progress_complaints']} in progress."
        if "satisfaction" in q or "rating" in q or "feedback" in q:
            return f"**Summary**: Average rating {context['average_citizen_rating']}/5 from {context['feedback_count']} feedback submissions."
        return (
            f"**Summary**: {context['total_complaints']} total complaints. "
            f"Open: {context['open_complaints']}, Resolved: {context['resolved_complaints']}, "
            f"Critical unresolved: {context['unresolved_critical_complaints']}."
        )
