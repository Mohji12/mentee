from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.activities import Activities
from app.db.models.MCA_assignments import MentorshipAssessment
from app.core.dependencies import get_current_hod
from app.services.email_services import send_mentor_changed_notification

router = APIRouter()


class AssignMentorRequest(BaseModel):
    mentor_id: Optional[str] = None  # None = unassign


@router.get("/stats")
def hod_stats(
    member_id: str,
    current: dict = Depends(get_current_hod),
    db: Session = Depends(get_db),
):
    """HOD: Department-level stats. Only students and mentors in this department."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    dept = current.get("department") or ""
    if not dept:
        return {
            "department": dept,
            "total_students": 0,
            "total_mentors": 0,
            "signed_up": 0,
            "profile_created": 0,
            "form_filled": 0,
            "swot_generated": 0,
            "activities_generated": 0,
            "mca_filled": 0,
        }
    total_mentors = db.query(Mentor).filter(Mentor.mentor_department == dept).count()
    usn_list = [
        r[0]
        for r in db.query(Student.student_usn)
        .join(Mentor, Student.assigned_mentor == Mentor.mentor_id)
        .filter(Mentor.mentor_department == dept)
        .all()
    ]
    total_students = len(usn_list)
    if not usn_list:
        return {
            "department": dept,
            "total_students": 0,
            "total_mentors": total_mentors,
            "signed_up": 0,
            "profile_created": 0,
            "form_filled": 0,
            "swot_generated": 0,
            "activities_generated": 0,
            "mca_filled": 0,
        }
    signed_up = (
        db.query(Student)
        .filter(Student.student_usn.in_(usn_list), Student.student_email.isnot(None), Student.student_password.isnot(None))
        .count()
    )
    profile_created = (
        db.query(Student)
        .filter(
            Student.student_usn.in_(usn_list),
            Student.student_name.isnot(None),
            Student.student_email.isnot(None),
            Student.student_phoneno.isnot(None),
            Student.student_program.isnot(None),
            Student.linkedin.isnot(None),
            Student.semester.isnot(None),
        )
        .count()
    )
    psychometric_filled = db.query(PsychometricResponse).filter(PsychometricResponse.student_usn.in_(usn_list)).count()
    report_generated = db.query(Report).filter(Report.student_usn.in_(usn_list)).count()
    activities_generated = db.query(Activities).filter(Activities.student_usn.in_(usn_list)).count()
    mca_filled = db.query(MentorshipAssessment).filter(MentorshipAssessment.student_usn.in_(usn_list)).count()
    return {
        "department": dept,
        "total_students": total_students,
        "total_mentors": total_mentors,
        "signed_up": signed_up,
        "profile_created": profile_created,
        "form_filled": psychometric_filled,
        "swot_generated": report_generated,
        "activities_generated": activities_generated,
        "mca_filled": mca_filled,
    }


@router.get("/filters")
def hod_filters(
    member_id: str,
    current: dict = Depends(get_current_hod),
    db: Session = Depends(get_db),
):
    """HOD: Return mentors in this department for filtering."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    dept = current.get("department") or ""
    if not dept:
        return {"mentors": []}
    mentors = (
        db.query(Mentor.mentor_id, Mentor.mentor_name, Mentor.mentor_department)
        .filter(Mentor.mentor_department == dept)
        .order_by(Mentor.mentor_name)
        .all()
    )
    mentor_list = [
        {"mentor_id": m.mentor_id, "mentor_name": m.mentor_name or m.mentor_id, "department": m.mentor_department or ""}
        for m in mentors
    ]
    return {"mentors": mentor_list}


@router.get("/students")
def hod_students(
    member_id: str,
    mentor_id: Optional[str] = Query(None, description="Filter by assigned mentor"),
    current: dict = Depends(get_current_hod),
    db: Session = Depends(get_db),
):
    """HOD: List all students in this department. Optional mentor filter."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    dept = current.get("department") or ""
    if not dept:
        return []
    q = (
        db.query(
            Student,
            Mentor.mentor_name,
            Mentor.mentor_department,
            func.count(PsychometricResponse.student_usn).label("has_psy_response"),
            func.count(Report.student_usn).label("has_report"),
            func.count(Activities.student_usn).label("has_activities"),
            func.count(MentorshipAssessment.student_usn).label("has_mca_form"),
        )
        .join(Mentor, Student.assigned_mentor == Mentor.mentor_id)
        .filter(Mentor.mentor_department == dept)
        .outerjoin(PsychometricResponse, Student.student_usn == PsychometricResponse.student_usn)
        .outerjoin(Report, Student.student_usn == Report.student_usn)
        .outerjoin(Activities, Student.student_usn == Activities.student_usn)
        .outerjoin(MentorshipAssessment, Student.student_usn == MentorshipAssessment.student_usn)
    )
    if mentor_id:
        q = q.filter(Student.assigned_mentor == mentor_id)
    q = q.group_by(Student.student_usn, Mentor.mentor_name, Mentor.mentor_department).all()
    student_list = []
    for row in q:
        student, mentor_name, mentor_dept, has_psy, has_report, has_activities, has_mca = row
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
        if has_psy:
            statuses.append("Form Filled")
        if has_report:
            statuses.append("SWOT Generated")
        if has_activities:
            statuses.append("Activities Generated")
        if has_mca:
            statuses.append("MCA Form Filled")
        if not statuses:
            statuses.append("Not Started")
        student_list.append({
            "student_usn": student.student_usn,
            "student_name": student.student_name,
            "phone": student.student_phoneno,
            "program": student.student_program,
            "email": student.student_email,
            "linkedin": student.linkedin,
            "semester": student.semester,
            "ass_mentor": mentor_name or "No mentor assigned",
            "assigned_mentor": student.assigned_mentor,
            "department": mentor_dept or "",
            "status": " → ".join(statuses),
        })
    return student_list


@router.patch("/students/{student_usn}/mentor")
def hod_assign_student_mentor(
    member_id: str,
    student_usn: str,
    body: AssignMentorRequest,
    current: dict = Depends(get_current_hod),
    db: Session = Depends(get_db),
):
    """HOD: Assign or change a student's mentor (or unassign). Only for students in this department; new mentor must be in same department."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    dept = current.get("department") or ""
    if not dept:
        raise HTTPException(status_code=403, detail="No department assigned")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_usn} not found")
    if student.assigned_mentor:
        current_mentor = db.query(Mentor).filter(Mentor.mentor_id == student.assigned_mentor).first()
        if not current_mentor or current_mentor.mentor_department != dept:
            raise HTTPException(status_code=403, detail="Student is not in your department")
    if body.mentor_id is not None and body.mentor_id.strip():
        mentor = db.query(Mentor).filter(Mentor.mentor_id == body.mentor_id.strip()).first()
        if not mentor:
            raise HTTPException(status_code=404, detail=f"Mentor {body.mentor_id} not found")
        if mentor.mentor_department != dept:
            raise HTTPException(status_code=403, detail="Mentor is not in your department")
        student.assigned_mentor = body.mentor_id.strip()
    else:
        mentor = None
        student.assigned_mentor = None
    db.commit()
    if student.student_email:
        send_mentor_changed_notification(
            student.student_email,
            student.student_name or student_usn,
            new_mentor_name=mentor.mentor_name if mentor else None,
            new_mentor_email=mentor.mentor_email if mentor else None,
            new_mentor_phoneno=mentor.mentor_phoneno if mentor else None,
        )
    return {"message": "Mentor updated successfully", "student_usn": student_usn, "assigned_mentor": student.assigned_mentor}
