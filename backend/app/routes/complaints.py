from fastapi import APIRouter, HTTPException, Query

from backend.app.models.complaint import (
    ComplaintCreate,
    ComplaintUpdate,
    DashboardStats,
    FeedbackCreate,
    FeedbackResponse,
    AIInsightsResponse,
)
from backend.app.services.complaint_service import ComplaintService
from backend.app.services.status_history_service import StatusHistoryService
from backend.app.services.insights_service import InsightsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/complaints", tags=["complaints"])


@router.post("/", status_code=201)
async def submit_complaint(complaint: ComplaintCreate):
    """Submit a new civic complaint."""
    try:
        return ComplaintService.create_complaint(complaint)
    except Exception as e:
        logger.error(f"Error submitting complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboard", response_model=DashboardStats)
async def get_dashboard():
    """Get dashboard analytics."""
    try:
        stats = ComplaintService.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/insights", response_model=AIInsightsResponse)
async def get_ai_insights():
    """Get AI-generated civic insights."""
    try:
        return InsightsService.generate_insights()
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{complaint_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(complaint_id: str, feedback: FeedbackCreate):
    """Submit citizen feedback for a resolved complaint."""
    success = ComplaintService.submit_feedback(
        complaint_id, feedback.rating, feedback.comment
    )
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Feedback not allowed. Complaint must be resolved and not already rated.",
        )
    return FeedbackResponse(success=True)


@router.get("/")
async def list_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str = Query(None),
    category: str = Query(None),
    severity: str = Query(None),
    location: str = Query(None),
    search: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
):
    """List complaints with filtering and search."""
    try:
        complaints, total = ComplaintService.get_all_complaints(
            skip=skip,
            limit=limit,
            status=status,
            category=category,
            severity=severity,
            location=location,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
        return {"status": "success", "total": total, "data": complaints}
    except Exception as e:
        logger.error(f"Error listing complaints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{complaint_id}/history")
async def get_status_history(complaint_id: str):
    """Get status change history for a complaint."""
    complaint = ComplaintService.get_complaint(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    history = StatusHistoryService.get_history(complaint["_id"])
    return {"status": "success", "data": history}


@router.get("/{complaint_id}")
async def get_complaint(complaint_id: str):
    """Get complaint by ID."""
    try:
        complaint = ComplaintService.get_complaint(complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return {"status": "success", "data": complaint}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{complaint_id}")
async def update_complaint(complaint_id: str, update_data: ComplaintUpdate):
    """Update complaint (admin)."""
    try:
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")

        success = ComplaintService.update_complaint(complaint_id, update_dict)
        if not success:
            raise HTTPException(status_code=404, detail="Complaint not found")

        return {"status": "success", "message": "Complaint updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
