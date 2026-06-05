from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class CategoryEnum(str, Enum):
    ROADS = "Roads"
    WATER = "Water"
    ELECTRICITY = "Electricity"
    SANITATION = "Sanitation"
    TRAFFIC = "Traffic"
    PUBLIC_SAFETY = "Public Safety"
    ENVIRONMENT = "Environment"


class SeverityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class StatusEnum(str, Enum):
    OPEN = "Open"
    UNDER_REVIEW = "Under Review"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class LanguageEnum(str, Enum):
    URDU = "Urdu"
    ENGLISH = "English"
    ROMAN_URDU = "Roman Urdu"


# Legacy status values for backward compatibility
LEGACY_STATUS_MAP = {
    "open": StatusEnum.OPEN.value,
    "in-progress": StatusEnum.IN_PROGRESS.value,
    "resolved": StatusEnum.RESOLVED.value,
}

OPEN_STATUSES = {
    StatusEnum.OPEN.value,
    StatusEnum.UNDER_REVIEW.value,
    StatusEnum.ASSIGNED.value,
    "open",
}

RESOLVED_STATUSES = {
    StatusEnum.RESOLVED.value,
    StatusEnum.CLOSED.value,
    "resolved",
    "closed",
}


class FeedbackSchema(BaseModel):
    rating: Optional[int] = None
    comment: str = ""
    submitted_at: Optional[datetime] = None


class ComplaintCreate(BaseModel):
    text: str = Field(..., min_length=10, max_length=2000)
    location: str = Field(..., min_length=2)
    category: Optional[str] = None
    language: Optional[LanguageEnum] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ComplaintUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    category: Optional[str] = None
    assigned_department: Optional[str] = None
    resolution_notes: Optional[str] = None
    updated_by: Optional[str] = "admin"


class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field("", max_length=1000)


class FeedbackResponse(BaseModel):
    success: bool = True


class ComplaintResponse(BaseModel):
    id: str = Field(alias="_id")
    complaint_id: Optional[str] = None
    text: str
    category: str
    severity: str
    priority: int
    priority_score: Optional[int] = None
    language: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    assigned_department: Optional[str] = ""
    resolution_notes: Optional[str] = ""
    created_at: datetime
    updated_at: Optional[datetime] = None
    duplicate_group_id: Optional[str] = None
    ai_recommendation: str
    department: Optional[str] = ""
    feedback: Optional[FeedbackSchema] = None

    class Config:
        populate_by_name = True


class AIClassificationResponse(BaseModel):
    category: str
    severity: str
    priority: int
    language: str
    department: str
    duplicate_group: Optional[str] = None
    recommendation: str
    confidence: float


class StatusHistoryEntry(BaseModel):
    complaint_id: str
    status: str
    updated_by: str
    timestamp: datetime


class DashboardStats(BaseModel):
    total_complaints: int
    open_complaints: int
    in_progress_complaints: int
    resolved_complaints: int
    resolved_percentage: float
    critical_count: int
    duplicate_complaints: int
    high_priority_count: int
    average_rating: float
    satisfaction_score: float
    feedback_count: int
    resolved_with_feedback: int
    status_breakdown: dict = {}
    category_breakdown: dict
    severity_breakdown: dict
    top_locations: List[dict]
    complaint_trend: List[dict] = []
    resolution_time_analysis: List[dict] = []
    feedback_ratings_distribution: dict = {}
    heatmap_points: List[dict] = []
    duplicate_clusters: int = 0


class AIInsightsResponse(BaseModel):
    top_issue_category: str
    fastest_growing_issue: str
    most_affected_area: str
    department_workload: str
    citizen_satisfaction_trend: str
    summary: str = ""


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500)


class ChatResponse(BaseModel):
    answer: str
