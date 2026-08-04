from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint, Text, Index
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
    """Stores marksheet URLs and graduation metadata per semester per student."""
    __tablename__ = "academic_performance_marksheets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False, index=True)
    semester = Column(Integer, nullable=False, index=True)  # 1-3 for BSc, 1-4 for MSc
    marksheet_url = Column(String(500), nullable=False)  # S3 key/path
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Graduation metadata
    sgpa = Column(String(20), nullable=True)
    cgpa = Column(String(20), nullable=True)
    percentage = Column(String(20), nullable=True)
    total_credits = Column(String(20), nullable=True)
    backlogs = Column(String(100), nullable=True)
    result_status = Column(String(50), nullable=True)
    academic_year = Column(String(32), nullable=True)

    # Verification workflow
    verification_status = Column(String(50), nullable=False, default="pending", server_default="pending", index=True)
    remarks = Column(Text, nullable=True)
    uploaded_by = Column(String(255), nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    file_hash = Column(String(64), nullable=True)

    __table_args__ = (
        Index("idx_apm_usn_status", "student_usn", "verification_status"),
        Index("idx_apm_usn_semester", "student_usn", "semester"),
        {"mysql_engine": "InnoDB"},
    )

    student = relationship("Student", back_populates="academic_performance_marksheets")


class StudentSecondaryMarksheet(Base):
    """Stores 10th and 12th standard marksheet URLs and school metadata per student."""
    __tablename__ = "student_secondary_marksheets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False, index=True)
    standard = Column(Integer, nullable=False)  # 10 or 12
    marksheet_url = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # School education metadata
    document_type = Column(String(20), nullable=True)  # 10th / 12th
    board_university = Column(String(255), nullable=True)
    institution_name = Column(String(255), nullable=True)
    year_of_passing = Column(String(20), nullable=True)
    percentage_cgpa = Column(String(50), nullable=True)

    # Verification workflow
    verification_status = Column(String(50), nullable=False, default="pending", server_default="pending", index=True)
    remarks = Column(Text, nullable=True)
    uploaded_by = Column(String(255), nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    file_hash = Column(String(64), nullable=True)

    __table_args__ = (
        UniqueConstraint("student_usn", "standard", name="uq_student_secondary_standard"),
        Index("idx_ssm_usn_status", "student_usn", "verification_status"),
        Index("idx_ssm_year", "year_of_passing"),
        {"mysql_engine": "InnoDB"},
    )

    student = relationship("Student", back_populates="secondary_marksheets")
