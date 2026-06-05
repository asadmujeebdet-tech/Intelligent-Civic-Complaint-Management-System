from backend.app.utils.time_utils import system_now
from typing import List
import logging

from backend.app.database import get_db

logger = logging.getLogger(__name__)


class StatusHistoryService:
    """Track complaint status changes."""

    @staticmethod
    def record_status_change(
        complaint_id: str,
        status: str,
        updated_by: str = "system",
    ) -> None:
        try:
            db = get_db()
            db.status_history.insert_one({
                "complaint_id": complaint_id,
                "status": status,
                "updated_by": updated_by,
                "timestamp": system_now(),
            })
        except Exception as e:
            logger.error(f"Failed to record status history: {e}")

    @staticmethod
    def get_history(complaint_id: str) -> List[dict]:
        try:
            db = get_db()
            entries = list(
                db.status_history.find({"complaint_id": complaint_id})
                .sort("timestamp", 1)
            )
            for entry in entries:
                entry["_id"] = str(entry["_id"])
            return entries
        except Exception as e:
            logger.error(f"Failed to get status history: {e}")
            return []
