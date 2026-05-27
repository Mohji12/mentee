from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List

class MeetingResponseRequest(BaseModel):
    status: str  # "approved" or "rejected"

class MeetingApptRequest(BaseModel):
    meeting_date: str
    venue: str

class MeetingScheduleRequest(BaseModel):
    meeting_date: str
    venue: str
    student_usns: list[str]  # Supports multiple students

class ProgressNotesRequest(BaseModel):
    progress_notes: str

class MeetingResponse(BaseModel):
    id: str  # Use UUID4 instead of int if it's a UUID
    meeting_date: datetime
    progress_notes: Optional[str]  # Allow None values
    status: str
    venue: str
    agenda: Optional[str] = None  # ✅ New field
    mentor_id: str
    student_usn: List[str]  # <-- Change to List of strings
    duration: Optional[int] = None  # Duration in minutes (optional)
    created_at: datetime

    class Config:
        from_attributes = True
