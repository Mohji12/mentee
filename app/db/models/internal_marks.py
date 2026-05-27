from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class InternalMarksImportBatch(Base):
    """Metadata for one bulk import of consolidated internal marks (university-style)."""

    __tablename__ = "internal_marks_import_batch"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    semester = Column(Integer, nullable=False, index=True)
    section_code = Column(String(64), nullable=True)
    program_label = Column(String(512), nullable=True)
    branch_label = Column(String(512), nullable=True)
    title = Column(String(1024), nullable=True)
    academic_year = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=True)

    entries = relationship(
        "InternalMarksEntry",
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class InternalMarksEntry(Base):
    """One score cell: student × subject × component (e.g. Activity-1, Final IA)."""

    __tablename__ = "internal_marks_entry"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(
        Integer,
        ForeignKey("internal_marks_import_batch.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_usn = Column(
        String(255),
        ForeignKey("students.student_usn", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    semester = Column(Integer, nullable=False, index=True)
    subject_code = Column(String(64), nullable=False)
    subject_name = Column(String(512), nullable=True)
    component_key = Column(String(128), nullable=False)
    component_label = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    score = Column(String(32), nullable=True)

    batch = relationship("InternalMarksImportBatch", back_populates="entries")

    __table_args__ = (
        UniqueConstraint(
            "batch_id",
            "student_usn",
            "subject_code",
            "component_key",
            name="uq_internal_marks_entry_batch_usn_subj_comp",
        ),
        {"mysql_engine": "InnoDB"},
    )
