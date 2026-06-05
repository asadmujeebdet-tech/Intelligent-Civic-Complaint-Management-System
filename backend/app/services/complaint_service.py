import logging
import secrets
from datetime import datetime, timedelta
from backend.app.utils.time_utils import system_now
from typing import List, Optional

from bson import ObjectId

from backend.app.database import get_db
from backend.app.models.complaint import (
    ComplaintCreate,
    StatusEnum,
    OPEN_STATUSES,
    RESOLVED_STATUSES,
    LEGACY_STATUS_MAP,
)
from backend.app.services.ai_service import ai_service
from backend.app.services.status_history_service import StatusHistoryService

logger = logging.getLogger(__name__)

CATEGORIES = [
    "Roads", "Water", "Electricity", "Sanitation",
    "Traffic", "Public Safety", "Environment",
]


class ComplaintService:
    """Service for complaint operations."""

    @staticmethod
    def _generate_complaint_id() -> str:
        date_str = system_now().strftime("%Y%m%d")
        return f"CL-{date_str}-{secrets.token_hex(3).upper()}"

    @staticmethod
    def _normalize_status(status: str) -> str:
        if not status:
            return StatusEnum.OPEN.value
        return LEGACY_STATUS_MAP.get(status.lower(), status)

    @staticmethod
    def _build_lookup_query(complaint_id: str) -> dict:
        clauses = [{"complaint_id": complaint_id}]
        if ObjectId.is_valid(complaint_id):
            clauses.append({"_id": ObjectId(complaint_id)})
        return {"$or": clauses}

    @staticmethod
    def _serialize_complaint(complaint: dict) -> dict:
        complaint["_id"] = str(complaint["_id"])
        if not complaint.get("complaint_id"):
            complaint["complaint_id"] = complaint["_id"]
        complaint["status"] = ComplaintService._normalize_status(complaint.get("status", StatusEnum.OPEN.value))
        if complaint.get("priority") is not None and "priority_score" not in complaint:
            complaint["priority_score"] = complaint["priority"]
        if not complaint.get("feedback"):
            complaint["feedback"] = {"rating": None, "comment": "", "submitted_at": None}
        return complaint

    @staticmethod
    def create_complaint(complaint_data: ComplaintCreate) -> dict:
        try:
            db = get_db()
            language = complaint_data.language or ai_service.detect_language(complaint_data.text)
            if hasattr(language, "value"):
                language = language.value
            ai_classification = ai_service.classify_complaint(
                complaint_data.text, complaint_data.location
            )
            embeddings = ai_service.get_embeddings(complaint_data.text)
            now = system_now()
            complaint_id = ComplaintService._generate_complaint_id()

            complaint_doc = {
                "complaint_id": complaint_id,
                "text": complaint_data.text,
                "category": ai_classification.category,
                "severity": ai_classification.severity,
                "priority": ai_classification.priority,
                "priority_score": ai_classification.priority,
                "language": str(language),
                "location": complaint_data.location,
                "latitude": complaint_data.latitude,
                "longitude": complaint_data.longitude,
                "status": StatusEnum.OPEN.value,
                "assigned_department": ai_classification.department,
                "resolution_notes": "",
                "created_at": now,
                "updated_at": now,
                "department": ai_classification.department,
                "ai_recommendation": ai_classification.recommendation,
                "ai_confidence": ai_classification.confidence,
                "embeddings": embeddings,
                "duplicate_group_id": None,
                "feedback": {"rating": None, "comment": "", "submitted_at": None},
            }

            result = db.complaints.insert_one(complaint_doc)
            mongo_id = str(result.inserted_id)
            complaint_doc["_id"] = mongo_id

            StatusHistoryService.record_status_change(
                mongo_id, StatusEnum.OPEN.value, "citizen"
            )
            ComplaintService._check_and_group_duplicates(mongo_id, embeddings)

            logger.info(f"Complaint created: {complaint_id}")
            return complaint_doc
        except Exception as e:
            logger.error(f"Error creating complaint: {e}")
            raise

    @staticmethod
    def _check_and_group_duplicates(complaint_id: str, embeddings: list, threshold: float = 0.85):
        try:
            db = get_db()
            if not embeddings:
                return

            similar = db.complaints.find({
                "embeddings": {"$exists": True},
                "_id": {"$ne": ObjectId(complaint_id)},
                "status": {"$in": list(OPEN_STATUSES)},
            }).limit(50)

            duplicates = []
            for complaint in similar:
                if complaint.get("embeddings"):
                    similarity = ai_service.calculate_similarity(embeddings, complaint["embeddings"])
                    if similarity >= threshold:
                        duplicates.append(str(complaint["_id"]))

            if duplicates:
                complaint = db.complaints.find_one({"_id": ObjectId(complaint_id)})
                group_data = {
                    "issue_type": "duplicate_cluster",
                    "complaint_ids": [complaint_id] + duplicates,
                    "created_at": system_now(),
                    "hotspot_location": complaint.get("location") if complaint else "",
                }
                result = db.complaint_groups.insert_one(group_data)
                group_id = str(result.inserted_id)
                for cid in [complaint_id] + duplicates:
                    db.complaints.update_one(
                        {"_id": ObjectId(cid)},
                        {"$set": {"duplicate_group_id": group_id}},
                    )
        except Exception as e:
            logger.warning(f"Duplicate check warning: {e}")

    @staticmethod
    def get_complaint(complaint_id: str) -> Optional[dict]:
        try:
            db = get_db()
            complaint = db.complaints.find_one(ComplaintService._build_lookup_query(complaint_id))
            if complaint:
                return ComplaintService._serialize_complaint(complaint)
            return None
        except Exception as e:
            logger.error(f"Error getting complaint: {e}")
            return None

    @staticmethod
    def get_all_complaints(
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        try:
            db = get_db()
            query = {}

            if status:
                query["status"] = status
            if category:
                query["category"] = category
            if severity:
                query["severity"] = severity
            if location:
                query["location"] = {"$regex": location, "$options": "i"}
            if search:
                query["$or"] = [
                    {"text": {"$regex": search, "$options": "i"}},
                    {"location": {"$regex": search, "$options": "i"}},
                    {"complaint_id": {"$regex": search, "$options": "i"}},
                ]
            if date_from or date_to:
                date_filter = {}
                if date_from:
                    date_filter["$gte"] = datetime.fromisoformat(date_from.replace("Z", ""))
                if date_to:
                    date_filter["$lte"] = datetime.fromisoformat(date_to.replace("Z", ""))
                query["created_at"] = date_filter

            total = db.complaints.count_documents(query)
            complaints = list(
                db.complaints.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            return [ComplaintService._serialize_complaint(c) for c in complaints], total
        except Exception as e:
            logger.error(f"Error getting complaints: {e}")
            return [], 0

    @staticmethod
    def update_complaint(complaint_id: str, update_data: dict) -> bool:
        try:
            db = get_db()
            complaint = db.complaints.find_one(ComplaintService._build_lookup_query(complaint_id))
            if not complaint:
                return False

            mongo_id = str(complaint["_id"])
            updated_by = update_data.pop("updated_by", "admin")
            update_data["updated_at"] = system_now()

            if "status" in update_data:
                status_val = update_data["status"]
                if hasattr(status_val, "value"):
                    status_val = status_val.value
                update_data["status"] = ComplaintService._normalize_status(status_val)
                StatusHistoryService.record_status_change(
                    mongo_id,
                    update_data["status"],
                    updated_by,
                )

            result = db.complaints.update_one(
                {"_id": ObjectId(mongo_id)},
                {"$set": update_data},
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            logger.error(f"Error updating complaint: {e}")
            return False

    @staticmethod
    def submit_feedback(complaint_id: str, rating: int, comment: str) -> bool:
        try:
            db = get_db()
            complaint = db.complaints.find_one(ComplaintService._build_lookup_query(complaint_id))
            if not complaint:
                return False

            status = ComplaintService._normalize_status(complaint.get("status", ""))
            if status not in RESOLVED_STATUSES:
                return False

            if complaint.get("feedback", {}).get("rating") is not None:
                return False

            feedback = {
                "rating": rating,
                "comment": comment,
                "submitted_at": system_now(),
            }
            db.complaints.update_one(
                {"_id": complaint["_id"]},
                {"$set": {"feedback": feedback, "updated_at": system_now()}},
            )
            return True
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return False

    @staticmethod
    def get_dashboard_stats() -> dict:
        try:
            db = get_db()
            total = db.complaints.count_documents({})
            open_count = db.complaints.count_documents({"status": {"$in": list(OPEN_STATUSES)}})
            in_progress = db.complaints.count_documents({"status": StatusEnum.IN_PROGRESS.value})
            resolved = db.complaints.count_documents({"status": {"$in": list(RESOLVED_STATUSES)}})
            critical = db.complaints.count_documents({"severity": "Critical"})
            duplicate_complaints = db.complaints.count_documents({"duplicate_group_id": {"$ne": None}})
            duplicate_groups = db.complaint_groups.count_documents({})
            high_priority = db.complaints.count_documents({"priority": {"$gte": 70}})

            category_breakdown = {
                cat: db.complaints.count_documents({"category": cat}) for cat in CATEGORIES
            }
            severity_breakdown = {
                sev: db.complaints.count_documents({"severity": sev})
                for sev in ["Low", "Medium", "High", "Critical"]
            }

            status_breakdown = {}
            for status in list(StatusEnum):
                count = db.complaints.count_documents({"status": status.value})
                if count:
                    status_breakdown[status.value] = count
            for legacy, mapped in LEGACY_STATUS_MAP.items():
                count = db.complaints.count_documents({"status": legacy})
                if count:
                    status_breakdown[mapped] = status_breakdown.get(mapped, 0) + count

            top_locations = list(db.complaints.aggregate([
                {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5},
            ]))

            now = system_now()
            complaint_trend = []
            for i in range(6, -1, -1):
                day = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
                next_day = day + timedelta(days=1)
                count = db.complaints.count_documents({
                    "created_at": {"$gte": day, "$lt": next_day},
                })
                complaint_trend.append({
                    "date": day.strftime("%Y-%m-%d"),
                    "count": count,
                })

            resolution_time_analysis = []
            resolved_complaints = db.complaints.find({
                "status": {"$in": list(RESOLVED_STATUSES)},
                "updated_at": {"$exists": True},
            }).limit(100)
            buckets = {"< 1 day": 0, "1-3 days": 0, "3-7 days": 0, "> 7 days": 0}
            for c in resolved_complaints:
                created = c.get("created_at")
                updated = c.get("updated_at", created)
                if created and updated:
                    days = (updated - created).days
                    if days < 1:
                        buckets["< 1 day"] += 1
                    elif days <= 3:
                        buckets["1-3 days"] += 1
                    elif days <= 7:
                        buckets["3-7 days"] += 1
                    else:
                        buckets["> 7 days"] += 1
            resolution_time_analysis = [{"range": k, "count": v} for k, v in buckets.items()]

            feedback_pipeline = list(db.complaints.aggregate([
                {"$match": {"feedback.rating": {"$ne": None}}},
                {"$group": {
                    "_id": None,
                    "avg_rating": {"$avg": "$feedback.rating"},
                    "count": {"$sum": 1},
                }},
            ]))
            avg_rating = feedback_pipeline[0]["avg_rating"] if feedback_pipeline else 0
            feedback_count = feedback_pipeline[0]["count"] if feedback_pipeline else 0
            satisfaction_score = round((avg_rating / 5) * 100, 1) if avg_rating else 0

            resolved_with_feedback = db.complaints.count_documents({
                "status": {"$in": list(RESOLVED_STATUSES)},
                "feedback.rating": {"$ne": None},
            })

            ratings_dist = {str(i): 0 for i in range(1, 6)}
            rating_counts = list(db.complaints.aggregate([
                {"$match": {"feedback.rating": {"$ne": None}}},
                {"$group": {"_id": "$feedback.rating", "count": {"$sum": 1}}},
            ]))
            for r in rating_counts:
                ratings_dist[str(r["_id"])] = r["count"]

            heatmap_points = []
            geo_complaints = db.complaints.find(
                {"latitude": {"$ne": None}, "longitude": {"$ne": None}},
                {"latitude": 1, "longitude": 1, "severity": 1, "category": 1, "location": 1},
            ).limit(500)
            for c in geo_complaints:
                heatmap_points.append({
                    "lat": c.get("latitude"),
                    "lng": c.get("longitude"),
                    "severity": c.get("severity"),
                    "category": c.get("category"),
                    "location": c.get("location"),
                })

            resolved_pct = (resolved / total * 100) if total > 0 else 0

            return {
                "total_complaints": total,
                "open_complaints": open_count,
                "in_progress_complaints": in_progress,
                "resolved_complaints": resolved,
                "resolved_percentage": round(resolved_pct, 2),
                "critical_count": critical,
                "duplicate_complaints": duplicate_complaints,
                "high_priority_count": high_priority,
                "average_rating": round(avg_rating, 2) if avg_rating else 0,
                "satisfaction_score": satisfaction_score,
                "feedback_count": feedback_count,
                "resolved_with_feedback": resolved_with_feedback,
                "status_breakdown": status_breakdown,
                "category_breakdown": category_breakdown,
                "severity_breakdown": severity_breakdown,
                "top_locations": [
                    {"location": loc["_id"], "count": loc["count"]}
                    for loc in top_locations
                ],
                "complaint_trend": complaint_trend,
                "resolution_time_analysis": resolution_time_analysis,
                "feedback_ratings_distribution": ratings_dist,
                "heatmap_points": heatmap_points,
                "duplicate_clusters": duplicate_groups,
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
