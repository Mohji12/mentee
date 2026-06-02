"""Helpers for separating active students from alumni (graduated) records."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Query, Session
from sqlalchemy import or_

from app.db.models.students import Student


def active_students_filter(query: Query) -> Query:
    """Exclude alumni from list/count queries (NULL is treated as active)."""
    return query.filter(or_(Student.is_alumni.is_(False), Student.is_alumni.is_(None)))


def batch_end_year(student_batch: Optional[str]) -> Optional[int]:
    if not student_batch or "-" not in str(student_batch):
        return None
    try:
        return int(str(student_batch).strip().split("-")[-1])
    except ValueError:
        return None


def is_batch_graduated(student_batch: Optional[str], *, today: Optional[date] = None) -> bool:
    """True when the batch academic end year has passed (July onwards)."""
    end_year = batch_end_year(student_batch)
    if end_year is None:
        return False
    today = today or date.today()
    if today.year > end_year:
        return True
    return today.year == end_year and today.month >= 7


def set_alumni_status(
    student: Student,
    is_alumni: bool,
    *,
    when: Optional[datetime] = None,
) -> None:
    student.is_alumni = is_alumni
    student.alumni_since = (when or datetime.utcnow()) if is_alumni else None


def sync_alumni_from_batches(db: Session) -> int:
    """Mark students as alumni when their batch end year has passed."""
    students = active_students_filter(db.query(Student)).all()
    updated = 0
    for student in students:
        if is_batch_graduated(student.student_batch):
            set_alumni_status(student, True)
            updated += 1
    if updated:
        db.commit()
    return updated
