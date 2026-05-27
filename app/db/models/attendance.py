from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text
from app.db.database import Base
from datetime import datetime
import pytz

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    
    session_id = Column(String(255), primary_key=True)
    mentor_id = Column(String(255), ForeignKey("mentors.mentor_id"), nullable=False)
    session_name = Column(String(255), nullable=True)  # Optional name for the session
    qr_code_data = Column(Text, nullable=False)  # The data encoded in QR code
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None), nullable=False)
    expires_at = Column(DateTime, nullable=False)  # When the QR code expires (stored in IST)
    is_active = Column(Boolean, default=True)  # Whether the session is still active
    location = Column(String(255), nullable=True)  # Optional location/venue
    
    class Config:
        from_attributes = True

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), ForeignKey("attendance_sessions.session_id"), nullable=False)
    student_usn = Column(String(255), ForeignKey("students.student_usn"), nullable=False)
    mentor_id = Column(String(255), ForeignKey("mentors.mentor_id"), nullable=False)
    marked_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None), nullable=False)
    status = Column(String(50), default="present", nullable=False)  # present, absent, late
    notes = Column(Text, nullable=True)  # Optional notes
    
    class Config:
        from_attributes = True



