from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List

class MeetingResponseRequest(BaseModel):
    status: str  # "approved" or "rejected"

class MeetingApptRequest(BaseModel):
    meeting_date: str
    meeting_mode: str  # "online" | "offline"
    venue: Optional[str] = None  # Required when meeting_mode == "offline"

class MeetingScheduleRequest(BaseModel):
    meeting_date: str
    venue: str
    meeting_mode: Optional[str] = "offline"  # "online" | "offline"
    google_meet_link: Optional[str] = None  # For mentor-created online meetings
    student_usns: list[str]  # Supports multiple students

class ProgressNotesRequest(BaseModel):
    progress_notes: str

class MeetingResponse(BaseModel):
    id: str
    meeting_date: datetime
    progress_notes: Optional[str] = None
    status: str
    venue: str
    agenda: Optional[str] = None
    mentor_id: str
    student_usn: List[str]
    student_names: Optional[List[str]] = None  # Names corresponding to student_usn
    duration: Optional[int] = None
    created_at: datetime
    meeting_mode: Optional[str] = "offline"
    google_meet_link: Optional[str] = None

    class Config:
        from_attributes = True
