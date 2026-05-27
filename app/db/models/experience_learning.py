from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class ExperienceLearning(Base):
    __tablename__ = "experience_learning"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(
        String(255), ForeignKey("students.student_usn"), nullable=True, index=True
    )
    mentor_id = Column(
        String(255), ForeignKey("mentors.mentor_id"), nullable=True, index=True
    )
    title = Column(String(255), nullable=False)
    detailed_explanation = Column(Text, nullable=False)
    proof_file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            '(student_usn IS NOT NULL AND mentor_id IS NULL) OR (student_usn IS NULL AND mentor_id IS NOT NULL)',
            name='check_student_or_mentor'
        ),
    )

    student = relationship("Student", back_populates="experience_learning")
    mentor = relationship("Mentor", back_populates="experience_learning")
