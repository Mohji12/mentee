from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.db.database import Base


class EmployabilityAssessment(Base):
    __tablename__ = "employability_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    performance_level = Column(String(50), nullable=False)
    assessed_by = Column(String(255), nullable=True)
    assessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    remarks = Column(Text, nullable=True)
