import json
import logging
from datetime import datetime, timedelta

from backend.app.database import get_db
from backend.app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class InsightsService:
    """Generate AI civic insights for the dashboard."""

    @staticmethod
    def generate_insights() -> dict:
        db = get_db()
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        categories = ["Roads", "Water", "Electricity", "Sanitation", "Traffic", "Public Safety", "Environment"]
        category_counts = {c: db.complaints.count_documents({"category": c}) for c in categories}
        top_category = max(category_counts, key=category_counts.get) if any(category_counts.values()) else "N/A"

        growth = {}
        for cat in categories:
            recent = db.complaints.count_documents({"category": cat, "created_at": {"$gte": week_ago}})
            prior = db.complaints.count_documents({
                "category": cat,
                "created_at": {"$gte": two_weeks_ago, "$lt": week_ago},
            })
            growth[cat] = recent - prior
        fastest_growing = max(growth, key=growth.get) if any(growth.values()) else "N/A"

        top_loc = list(db.complaints.aggregate([
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1},
        ]))
        most_affected = top_loc[0]["_id"] if top_loc else "N/A"

        dept_pipeline = list(db.complaints.aggregate([
            {"$group": {"_id": "$assigned_department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 3},
        ]))
        dept_workload = ", ".join(
            f"{d['_id'] or 'Unassigned'}: {d['count']}" for d in dept_pipeline
        ) or "No department assignments yet"

        rating_pipeline = list(db.complaints.aggregate([
            {"$match": {"feedback.rating": {"$ne": None}}},
            {"$group": {"_id": None, "avg": {"$avg": "$feedback.rating"}, "count": {"$sum": 1}}},
        ]))
        avg_rating = rating_pipeline[0]["avg"] if rating_pipeline else 0
        feedback_count = rating_pipeline[0]["count"] if rating_pipeline else 0
        satisfaction_trend = (
            f"Average rating {avg_rating:.1f}/5 from {feedback_count} feedback submissions"
            if feedback_count else "No citizen feedback yet"
        )

        stats_context = {
            "top_issue_category": f"{top_category} ({category_counts.get(top_category, 0)} complaints)",
            "fastest_growing_issue": f"{fastest_growing} ({growth.get(fastest_growing, 0)} vs prior week)",
            "most_affected_area": most_affected,
            "department_workload": dept_workload,
            "citizen_satisfaction_trend": satisfaction_trend,
            "category_breakdown": category_counts,
        }

        summary = InsightsService._generate_summary(stats_context)
        return {**stats_context, "summary": summary}

    @staticmethod
    def _generate_summary(context: dict) -> str:
        prompt = f"""You are CivicLens AI. Generate a 2-3 sentence executive summary for government officials using ONLY this data:

{json.dumps(context, indent=2)}

Be concise. Highlight priorities and recommendations. Do not invent data."""

        try:
            if ai_service.model:
                response = ai_service.model.generate_content(prompt)
                return response.text.strip()
        except Exception as e:
            logger.error(f"Insights summary error: {e}")

        return (
            f"Top issue: {context['top_issue_category']}. "
            f"Fastest growing: {context['fastest_growing_issue']}. "
            f"Focus area: {context['most_affected_area']}."
        )
