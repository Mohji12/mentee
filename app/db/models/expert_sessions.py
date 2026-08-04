from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class ExpertSession(Base):
    __tablename__ = "expert_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    session_title = Column(String(255), nullable=False)
    session_date = Column(DateTime, nullable=False, index=True)
    expert_name = Column(String(255), nullable=False)
    expert_type = Column(String(50), nullable=False, default="industry")
    description = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    attendance = relationship("ExpertSessionAttendance", back_populates="session", cascade="all, delete-orphan")


class ExpertSessionAttendance(Base):
    __tablename__ = "expert_session_attendance"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    session_id = Column(Integer, ForeignKey("expert_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="attended")
    marked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ExpertSession", back_populates="attendance")
