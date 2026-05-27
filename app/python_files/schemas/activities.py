from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivityTrackingSchema(BaseModel):
    activity_id: str
    activities: str
    duration_type: str  # short_term, mid_term, long_term
    deadline: Optional[datetime]
    remarks: Optional[str]
    completed_in: Optional[int]
    percentage: Optional[int]
    benefitted: Optional[bool]
    proof: Optional[str]  # Link to proof file (jpg, png, pdf, etc.)

    class Config:
        from_attributes = True

class UpdateActivityTrackingSchema(BaseModel):
    remarks: Optional[str]
    completed_in: Optional[int]
    benefitted: Optional[bool]
    proof: Optional[str]  # Allow updating the proof field

    class Config:
        from_attributes = True

class ActivityReviewRequest(BaseModel):
    status: str  # "Approved" or "Rejected"
    percentage: int = None  # Required only if approved
    rejection_reason: str = None  # Required only if rejected

class ActivitySubmissionsSchema(BaseModel):
    submission_id: str
    activity_id: str
    student_usn: str
    mentor_id: str
    proof: str
    submitted_at: datetime
    status: str
    rejection_reason: Optional[str] = None
    percentage: Optional[int]
    completed_in: Optional[int] = None

    class Config:
        from_attributes = True  # Allows SQLAlchemy models to be serialized

class ActivityMSubmissionsSchema(BaseModel):
    submission_id: str
    activity_id: str
    activity_name: str  # Added activity name
    student_usn: str
    student_name: str  # Added student name
    mentor_id: str
    proof: str
    submitted_at: datetime
    status: str
    rejection_reason: Optional[str] = None
    completed_in: Optional[int] = None

    class Config:
        from_attributes = True  # Allows SQLAlchemy models to be serialized

# Request model for review
class ActivityReviewRequest(BaseModel):
    status: str  # "Approved" or "Rejected"
    percentage: int = None  # Required only if approved
    rejection_reason: str = None  # Required only if rejected
