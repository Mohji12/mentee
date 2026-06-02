from io import BytesIO
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd

from app.db.database import get_db
from app.db.models.admin import Admin
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.activities import Activities
from app.db.models.MCA_assignments import MentorshipAssessment
from app.utils.alumni import active_students_filter, set_alumni_status, sync_alumni_from_batches

router = APIRouter()


class AlumniStatusUpdate(BaseModel):
    is_alumni: bool


class BulkAlumniByBatchRequest(BaseModel):
    student_batch: str = Field(..., min_length=1, description="Batch in YYYY-YYYY format")


def _build_statuses(student, has_psy_response, has_report, has_activities, has_mca_form) -> str:
    statuses = []
    if student.student_email and student.student_password:
        statuses.append("Signed Up")
    if all(
        [
            student.student_name,
            student.student_email,
            student.student_phoneno,
            student.student_program,
            student.semester,
        ]
    ):
        statuses.append("Profile Created")
    if has_psy_response:
        statuses.append("Form Filled")
    if has_report:
        statuses.append("SWOT Generated")
    if has_activities:
        statuses.append("Activities Generated")
    if has_mca_form:
        statuses.append("MCA Form Filled")
    if not statuses:
        statuses.append("Not Started")
    return " → ".join(statuses)


def _student_list_query(db: Session, *, alumni_only: bool = False, active_only: bool = False):
    q = (
        db.query(
            Student,
            Mentor.mentor_name,
            func.count(PsychometricResponse.student_usn).label("has_psy_response"),
            func.count(Report.student_usn).label("has_report"),
            func.count(Activities.student_usn).label("has_activities"),
            func.count(MentorshipAssessment.student_usn).label("has_mca_form"),
        )
        .outerjoin(Mentor, Student.assigned_mentor == Mentor.mentor_id)
        .outerjoin(PsychometricResponse, Student.student_usn == PsychometricResponse.student_usn)
        .outerjoin(Report, Student.student_usn == Report.student_usn)
        .outerjoin(Activities, Student.student_usn == Activities.student_usn)
        .outerjoin(MentorshipAssessment, Student.student_usn == MentorshipAssessment.student_usn)
    )
    if alumni_only:
        q = q.filter(Student.is_alumni.is_(True))
    elif active_only:
        q = active_students_filter(q)
    return q.group_by(Student.student_usn, Mentor.mentor_name)


def _rows_to_student_list(rows) -> list:
    student_list = []
    for student, mentor_name, has_psy, has_report, has_activities, has_mca in rows:
        student_list.append(
            {
                "student_usn": student.student_usn,
                "student_name": student.student_name,
                "phone": student.student_phoneno,
                "program": student.student_program,
                "email": student.student_email,
                "linkedin": student.linkedin,
                "semester": student.semester,
                "student_batch": student.student_batch,
                "ass_mentor": mentor_name if mentor_name else "No mentor assigned",
                "status": _build_statuses(student, has_psy, has_report, has_activities, has_mca),
                "is_alumni": bool(student.is_alumni),
                "alumni_since": student.alumni_since.isoformat() if student.alumni_since else None,
            }
        )
    return student_list


@router.get("/get_all_students")
def get_all_students(
    admin_id: str,
    view: Literal["active", "alumni", "all"] = Query("active", description="active | alumni | all"),
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if not admin:
        return JSONResponse(status_code=404, content={"detail": f"Admin with ID {admin_id} not found"})

    alumni_only = view == "alumni"
    active_only = view == "active"
    rows = _student_list_query(db, alumni_only=alumni_only, active_only=active_only).all()
    return _rows_to_student_list(rows)


@router.get("/student_stats")
def get_student_statistics(
    admin_id: str,
    include_alumni: bool = Query(False, description="Include alumni in statistics"),
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin with ID {admin_id} not found")

    def _student_count(*filters):
        q = db.query(func.count(Student.student_usn)).filter(*filters)
        if not include_alumni:
            q = active_students_filter(q)
        return q.scalar()

    total_students = _student_count()
    signed_up = _student_count(
        Student.student_email.isnot(None),
        Student.student_password.isnot(None),
    )
    profile_created = _student_count(
        Student.student_name.isnot(None),
        Student.student_email.isnot(None),
        Student.student_phoneno.isnot(None),
        Student.student_program.isnot(None),
        Student.linkedin.isnot(None),
        Student.semester.isnot(None),
    )

    active_usns = None if include_alumni else [
        r[0] for r in active_students_filter(db.query(Student.student_usn)).all()
    ]

    def _related_count(model, usn_column):
        q = db.query(func.count()).select_from(model)
        if active_usns is not None:
            if not active_usns:
                return 0
            q = q.filter(usn_column.in_(active_usns))
        else:
            q = q.filter(usn_column.isnot(None))
        return q.scalar()

    psychometric_filled = _related_count(PsychometricResponse, PsychometricResponse.student_usn)
    report_generated = _related_count(Report, Report.student_usn)
    activities_generated = _related_count(Activities, Activities.student_usn)
    mca_filled = _related_count(MentorshipAssessment, MentorshipAssessment.student_usn)

    total_alumni = db.query(func.count(Student.student_usn)).filter(Student.is_alumni.is_(True)).scalar()
    total_active = active_students_filter(db.query(func.count(Student.student_usn))).scalar()

    return {
        "total_students": total_students,
        "total_active": total_active,
        "total_alumni": total_alumni,
        "signed_up": signed_up,
        "profile_created": profile_created,
        "form_filled": psychometric_filled,
        "swot_generated": report_generated,
        "activities_generated": activities_generated,
        "mca_filled": mca_filled,
    }


@router.patch("/students/{student_usn}/alumni-status")
def update_student_alumni_status(
    admin_id: str,
    student_usn: str,
    body: AlumniStatusUpdate,
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin with ID {admin_id} not found")

    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    set_alumni_status(student, body.is_alumni)
    db.commit()
    db.refresh(student)
    return {
        "student_usn": student.student_usn,
        "is_alumni": bool(student.is_alumni),
        "alumni_since": student.alumni_since.isoformat() if student.alumni_since else None,
    }


@router.post("/students/mark-alumni-by-batch")
def mark_alumni_by_batch(
    admin_id: str,
    body: BulkAlumniByBatchRequest,
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin with ID {admin_id} not found")

    batch = body.student_batch.strip()
    students = (
        active_students_filter(db.query(Student))
        .filter(Student.student_batch == batch)
        .all()
    )
    if not students:
        raise HTTPException(status_code=404, detail=f"No active students found for batch {batch}")

    for student in students:
        set_alumni_status(student, True)
    db.commit()
    return {"updated": len(students), "student_batch": batch}


@router.post("/students/sync-alumni-from-batches")
def sync_alumni_from_batches_endpoint(admin_id: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin with ID {admin_id} not found")

    updated = sync_alumni_from_batches(db)
    return {"updated": updated, "message": f"Marked {updated} student(s) as alumni based on batch end year."}


@router.get("/export_mentors", response_class=StreamingResponse)
def export_mentors_excel(admin_id: str, db: Session = Depends(get_db)):
    """Export all mentor data to an Excel file. Password is excluded for security."""
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin with ID {admin_id} not found")

    mentors = db.query(Mentor).order_by(Mentor.mentor_id).all()
    if not mentors:
        raise HTTPException(status_code=404, detail="No mentors found in the database")

    rows = [
        {
            "Mentor ID": m.mentor_id,
            "Name": m.mentor_name or "",
            "Department": m.mentor_department or "",
            "Email": m.mentor_email or "",
            "Phone": m.mentor_phoneno or "",
        }
        for m in mentors
    ]
    df = pd.DataFrame(rows)
    buf = BytesIO()
    df.to_excel(buf, index=False, sheet_name="Mentors", engine="openpyxl")
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=mentors_export.xlsx"},
    )
