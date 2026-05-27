from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class CounselingSession(Base):
    __tablename__ = 'counseling_sessions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    counseling_id = Column(String(50), unique=True, index=True, nullable=False)
    student_usn = Column(String(255), ForeignKey('students.student_usn'), nullable=False)
    mentor_id = Column(String(255), ForeignKey('mentors.mentor_id'), nullable=False)
    
    # Session details
    session_date = Column(DateTime, nullable=False)
    venue = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default='scheduled')  # scheduled, completed, cancelled, rescheduled
    
    # Google Meet details
    google_meet_link = Column(String(500), nullable=True)
    meeting_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional fields
    notes = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    is_urgent = Column(Boolean, default=False)
    
    # Feedback fields
    student_feedback = Column(Text, nullable=True)
    student_rating = Column(Integer, nullable=True)  # 1-5 rating
    student_feedback_date = Column(DateTime, nullable=True)
    
    mentor_feedback = Column(Text, nullable=True)
    mentor_rating = Column(Integer, nullable=True)  # 1-5 rating
    mentor_feedback_date = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="counseling_sessions")
    mentor = relationship("Mentor", back_populates="counseling_sessions")

class CounselingAvailability(Base):
    __tablename__ = 'counseling_availability'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mentor_id = Column(String(255), ForeignKey('mentors.mentor_id'), nullable=False)
    
    # Availability details
    day_of_week = Column(String(10), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(String(10), nullable=False)   # HH:MM format
    end_time = Column(String(10), nullable=False)     # HH:MM format
    is_available = Column(Boolean, default=True)
    
    # Date range for availability
    available_from = Column(DateTime, nullable=True)
    available_until = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mentor = relationship("Mentor", back_populates="counseling_availability")
