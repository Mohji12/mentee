from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class CounselingStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    REFERRED = "referred"

class OutcomeStatus(str, Enum):
    FULLY_RESOLVED = "fully_resolved"
    PARTIALLY_RESOLVED = "partially_resolved"
    UNRESOLVED = "unresolved"
    NEEDS_FOLLOWUP = "needs_followup"

class CounselingSessionCreate(BaseModel):
    session_date: datetime = Field(..., description="Preferred session date and time")
    venue: Optional[str] = Field(None, description="Preferred venue for counseling")
    reason: str = Field(..., description="Reason for counseling session")
    is_urgent: bool = Field(default=False, description="Is this an urgent session")

class CounselingSessionUpdate(BaseModel):
    session_date: Optional[datetime] = Field(None, description="Updated session date and time")
    venue: Optional[str] = Field(None, description="Updated venue")
    reason: Optional[str] = Field(None, description="Updated reason")
    status: Optional[CounselingStatus] = Field(None, description="Session status")
    notes: Optional[str] = Field(None, description="Mentor notes")
    feedback: Optional[str] = Field(None, description="Session feedback")
    referred_to_name: Optional[str] = Field(None, description="Name of specialist when referring student")
    referred_to_contact: Optional[str] = Field(None, description="Contact of specialist when referring")


# Tabular feedback on session card: Issue Raised / Details of Resolution / Resolution (define before CounselingSessionResponse)
class IssueResolutionFeedbackRow(BaseModel):
    row_type: str = Field(..., description="issue_raised | details_of_resolution | resolution")
    description: Optional[str] = None
    feedback_date: Optional[date] = None
    status: Optional[str] = Field(None, description="WIP | Close")


class IssueResolutionFeedbackUpdate(BaseModel):
    rows: List[IssueResolutionFeedbackRow] = Field(..., description="Exactly 3 rows: issue_raised, details_of_resolution, resolution")


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
    referred_to_name: Optional[str] = None
    referred_to_contact: Optional[str] = None
    referred_at: Optional[datetime] = None
    
    # Feedback fields
    student_feedback: Optional[str] = None
    student_rating: Optional[int] = None
    student_feedback_date: Optional[datetime] = None
    student_feedback_file_url: Optional[str] = None  # URL to view/download mentee's uploaded file
    mentor_feedback: Optional[str] = None
    mentor_rating: Optional[int] = None
    mentor_feedback_date: Optional[datetime] = None
    mentor_feedback_file_url: Optional[str] = None  # URL to view/download mentor's proof (PDF)
    student_issues_proof_file_url: Optional[str] = None  # URL to view/download mentee's proof (issues form)
    mentor_resolution_proof_file_url: Optional[str] = None  # URL to view/download mentor's resolution proof
    issue_resolution_feedback_proof_file_url: Optional[str] = None  # URL for proof of issue-resolution feedback table

    # Student details
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    student_phoneno: Optional[str] = None
    
    # Mentor details
    mentor_name: Optional[str] = None
    mentor_email: Optional[str] = None
    mentor_phoneno: Optional[str] = None
    issue_resolution_feedback: Optional[List[IssueResolutionFeedbackRow]] = None  # 3 rows for session card table
    
    # Outcome and Follow-up Tracking
    outcome_status: Optional[str] = None  # fully_resolved, partially_resolved, unresolved, needs_followup
    outcome_notes: Optional[str] = None
    followup_date: Optional[date] = None
    followup_scheduled: Optional[bool] = False
    parent_session_id: Optional[str] = None  # Links to original session for follow-ups

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


# Issues Raised & Resolved (review table after session)
class IssueResolutionRow(BaseModel):
    issues_raised: str = Field(..., description="Issues raised")
    date_issue_raised: date = Field(..., description="Date of issue raised (YYYY-MM-DD)")
    resolution_details: Optional[str] = Field(None, description="Details of resolution (filled by mentor)")
    date_resolution_provided: Optional[date] = Field(None, description="Date of resolution (filled by mentor)")


class IssuesResolutionSubmit(BaseModel):
    rows: List[IssueResolutionRow] = Field(..., description="List of issues and resolutions")


class IssueResolutionResponse(BaseModel):
    id: int
    counseling_id: str
    serial_no: int
    issues_raised: str
    date_issue_raised: date
    resolution_details: Optional[str] = None
    date_resolution_provided: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Mentor updates resolution only
class IssueResolutionUpdateRow(BaseModel):
    id: int = Field(..., description="Row id to update")
    resolution_details: Optional[str] = Field(None, description="Details of resolution provided")
    date_resolution_provided: Optional[date] = Field(None, description="Date of resolution provided (YYYY-MM-DD)")


class IssuesResolutionUpdate(BaseModel):
    rows: List[IssueResolutionUpdateRow] = Field(..., description="Resolution updates per row")


# Outcome and Follow-up Tracking Schemas
class OutcomeUpdate(BaseModel):
    outcome_status: str = Field(..., description="Outcome status: fully_resolved, partially_resolved, unresolved, needs_followup")
    outcome_notes: Optional[str] = Field(None, description="Notes about the outcome")
    followup_date: Optional[date] = Field(None, description="Suggested follow-up date if needed")

class FollowupSchedule(BaseModel):
    session_date: datetime = Field(..., description="Follow-up session date and time")
    venue: str = Field(..., description="Venue for follow-up session")
    reason: Optional[str] = Field(None, description="Reason for follow-up (auto-filled from parent)")
    is_urgent: bool = Field(default=False, description="Is this an urgent session")

class SessionChainResponse(BaseModel):
    sessions: List["CounselingSessionResponse"]
    total_sessions: int
    original_session_id: Optional[str] = None

class FollowupDueResponse(BaseModel):
    counseling_id: str
    student_usn: str
    student_name: Optional[str] = None
    session_date: datetime
    followup_date: date
    outcome_status: str
    outcome_notes: Optional[str] = None
    days_until_followup: int
    is_overdue: bool

    class Config:
        from_attributes = True
