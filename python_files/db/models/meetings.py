from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from app.db.database import Base
from datetime import datetime, timezone

class Meetings(Base):
    __tablename__ = "meetings"

    srno = Column(Integer, primary_key=True, index=True)
    id = Column(String(36), index=True)  # UUID for Meeting ID
    mentor_id = Column(String(50), ForeignKey("mentors.mentor_id"), nullable=False)
    student_usn = Column(String(50), ForeignKey("students.student_usn"), nullable=False)
    meeting_date = Column(DateTime, nullable=False)  # Meeting date and time
    venue = Column(String(255), nullable=False)  # Meeting venue
    progress_notes = Column(Text, nullable=True)  # Notes about the student's progress
    created_at = Column(DateTime, default=datetime.now(timezone.utc))  # Creation timestamp
    status = Column(String(20))
    attendance = Column(String(50))  # Attendance status
    agenda = Column(String(255), nullable=True)  # Meeting agenda
    duration = Column(Integer, nullable=True)  # Duration in minutes

    class Config:
        from_attributes = True
