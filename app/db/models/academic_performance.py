from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint
from app.db.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class AcademicPerformanceLock(Base):
    """Tracks one-time submission of academic performance per student (no ALTER on students)."""
    __tablename__ = "academic_performance_lock"

    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), primary_key=True)
    submitted_at = Column(DateTime, nullable=False)


class AcademicPerformance(Base):
    __tablename__ = "academic_performance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)  # 1-3 for BSc, 1-4 for MSc
    course = Column(String(255), nullable=False)
    grade = Column(String(50), nullable=True)
    overall_attendance = Column(String(50), nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False)  # Row-level lock: once saved, cannot edit/delete
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="academic_performance")


class AcademicPerformanceMarksheet(Base):
    """Stores marksheet URLs per semester per student."""
    __tablename__ = "academic_performance_marksheets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)  # 1-3 for BSc, 1-4 for MSc
    marksheet_url = Column(String(500), nullable=False)  # S3 key/path
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Unique constraint: one marksheet per student per semester
    __table_args__ = (
        {'mysql_engine': 'InnoDB'},
    )

    student = relationship("Student", back_populates="academic_performance_marksheets")


class StudentSecondaryMarksheet(Base):
    """Stores 10th and 12th standard marksheet URLs per student (prerequisite before semester data)."""
    __tablename__ = "student_secondary_marksheets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False)
    standard = Column(Integer, nullable=False)  # 10 or 12
    marksheet_url = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("student_usn", "standard", name="uq_student_secondary_standard"),
        {"mysql_engine": "InnoDB"},
    )

    student = relationship("Student", back_populates="secondary_marksheets")
