from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class CounselingStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class CounselingSessionCreate(BaseModel):
    session_date: datetime = Field(..., description="Preferred session date and time")
    venue: str = Field(..., description="Preferred venue for counseling")
    reason: str = Field(..., description="Reason for counseling session")
    is_urgent: bool = Field(default=False, description="Is this an urgent session")

class CounselingSessionUpdate(BaseModel):
    session_date: Optional[datetime] = Field(None, description="Updated session date and time")
    venue: Optional[str] = Field(None, description="Updated venue")
    reason: Optional[str] = Field(None, description="Updated reason")
    status: Optional[CounselingStatus] = Field(None, description="Session status")
    notes: Optional[str] = Field(None, description="Mentor notes")
    feedback: Optional[str] = Field(None, description="Session feedback")

class CounselingSessionResponse(BaseModel):
    id: int
    counseling_id: str
    student_usn: str
    mentor_id: str
    session_date: datetime
    venue: str
    reason: str
    status: str
    google_meet_link: Optional[str]
    meeting_id: Optional[str]
    notes: Optional[str]
    feedback: Optional[str]
    is_urgent: bool
    created_at: datetime
    updated_at: datetime
    
    # Feedback fields
    student_feedback: Optional[str] = None
    student_rating: Optional[int] = None
    student_feedback_date: Optional[datetime] = None
    mentor_feedback: Optional[str] = None
    mentor_rating: Optional[int] = None
    mentor_feedback_date: Optional[datetime] = None
    
    # Student details
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    student_phoneno: Optional[str] = None
    
    # Mentor details
    mentor_name: Optional[str] = None
    mentor_email: Optional[str] = None
    mentor_phoneno: Optional[str] = None

    class Config:
        from_attributes = True

class CounselingAvailabilityCreate(BaseModel):
    day_of_week: str = Field(..., description="Day of the week (Monday, Tuesday, etc.)")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    is_available: bool = Field(default=True, description="Is available on this day/time")
    available_from: Optional[datetime] = Field(None, description="Available from date")
    available_until: Optional[datetime] = Field(None, description="Available until date")

class CounselingAvailabilityResponse(BaseModel):
    id: int
    mentor_id: str
    day_of_week: str
    start_time: str
    end_time: str
    is_available: bool
    available_from: Optional[datetime]
    available_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GoogleMeetResponse(BaseModel):
    meeting_link: str
    meeting_id: str
    join_url: str
    created_at: datetime

class CounselingStats(BaseModel):
    total_sessions: int
    scheduled_sessions: int
    completed_sessions: int
    cancelled_sessions: int
    upcoming_sessions: int
    urgent_sessions: int

class StudentFeedbackSubmit(BaseModel):
    feedback: str = Field(..., description="Student feedback about the counseling session")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")

class MentorFeedbackSubmit(BaseModel):
    feedback: str = Field(..., description="Mentor feedback about the counseling session")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: Optional[str] = None
