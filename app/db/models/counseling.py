from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, Date
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
    status = Column(String(20), default='scheduled')  # scheduled, completed, cancelled, rescheduled, referred
    
    # Google Meet details
    google_meet_link = Column(String(500), nullable=True)
    meeting_id = Column(String(100), nullable=True)
    
    # Referral (when mentor refers student to specialist)
    referred_to_name = Column(String(255), nullable=True)
    referred_to_contact = Column(String(100), nullable=True)
    referred_at = Column(DateTime, nullable=True)
    
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
    student_feedback_file = Column(String(500), nullable=True)  # S3 key for uploaded file

    mentor_feedback = Column(Text, nullable=True)
    mentor_rating = Column(Integer, nullable=True)  # 1-5 rating
    mentor_feedback_date = Column(DateTime, nullable=True)
    mentor_feedback_file = Column(String(500), nullable=True)  # S3 key for mentor's proof (e.g. PDF)

    # Issues & resolution: mentee can upload proof of work done after session
    student_issues_proof_file = Column(String(500), nullable=True)  # S3 key for proof file
    # Mentor can upload proof for resolution (e.g. summary document)
    mentor_resolution_proof_file = Column(String(500), nullable=True)  # S3 key
    # Proof file for the 3-row issue-resolution feedback table (session card)
    issue_resolution_feedback_proof_file = Column(String(500), nullable=True)  # S3 key

    # Outcome and Follow-up Tracking
    outcome_status = Column(String(30), nullable=True)  # fully_resolved, partially_resolved, unresolved, needs_followup
    outcome_notes = Column(Text, nullable=True)
    followup_date = Column(Date, nullable=True)
    followup_scheduled = Column(Boolean, default=False)
    parent_session_id = Column(String(50), nullable=True)  # Links to original session for follow-ups

    # Relationships
    student = relationship("Student", back_populates="counseling_sessions")
    mentor = relationship("Mentor", back_populates="counseling_sessions")
    issues_resolutions = relationship("SessionIssuesResolution", back_populates="session", cascade="all, delete-orphan")
    issue_resolution_feedback = relationship("CounselingIssueResolutionFeedback", back_populates="session", cascade="all, delete-orphan")

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


class SessionIssuesResolution(Base):
    """Details of Issues Raised & Resolved - filled by student after completed session."""
    __tablename__ = 'session_issues_resolutions'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    counseling_id = Column(String(50), ForeignKey('counseling_sessions.counseling_id'), nullable=False)
    serial_no = Column(Integer, nullable=False)
    issues_raised = Column(Text, nullable=False)
    date_issue_raised = Column(Date, nullable=False)
    resolution_details = Column(Text, nullable=True)   # Filled by mentor
    date_resolution_provided = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("CounselingSession", back_populates="issues_resolutions")


class CounselingIssueResolutionFeedback(Base):
    """Tabular feedback on session card: Issue Raised by Mentor, Details of Resolution, Resolution (each with description, date, status)."""
    __tablename__ = "counseling_issue_resolution_feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    counseling_id = Column(String(50), ForeignKey("counseling_sessions.counseling_id"), nullable=False)
    row_type = Column(String(30), nullable=False)  # issue_raised | details_of_resolution | resolution
    description = Column(Text, nullable=True)
    feedback_date = Column(Date, nullable=True)
    status = Column(String(10), nullable=True)  # WIP | Close

    session = relationship("CounselingSession", back_populates="issue_resolution_feedback")


class CounselingEscalation(Base):
    """Escalation tracking for admin/HOD oversight."""
    __tablename__ = "counseling_escalations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("counseling_sessions.counseling_id"), nullable=False)
    escalated_by = Column(String(255), nullable=False)
    escalated_to = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default='open')  # open, acknowledged, resolved
    priority = Column(String(20), default='normal')  # low, normal, high, critical
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    session = relationship("CounselingSession")


class CounselingReminder(Base):
    """Reminder tracking for counseling sessions."""
    __tablename__ = "counseling_reminders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("counseling_sessions.counseling_id"), nullable=True)
    recipient_id = Column(String(255), nullable=False)  # mentor_id or student_usn
    recipient_type = Column(String(20), nullable=False)  # mentor, student
    reminder_type = Column(String(30), nullable=False)  # upcoming_session, followup_due, overdue_resolution
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    scheduled_for = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    status = Column(String(20), default='pending')  # pending, sent, read, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("CounselingSession")
