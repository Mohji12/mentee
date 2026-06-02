import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.committee_member import CommitteeMember
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.activities import Activities
from app.db.models.MCA_assignments import MentorshipAssessment
from app.core.dependencies import get_current_leader
from app.utils.alumni import active_students_filter
from app.services.email_services import send_mentor_changed_notification
from app.core.password import hash_password, validate_password

router = APIRouter()


class AssignMentorRequest(BaseModel):
    mentor_id: Optional[str] = None  # None = unassign

class MentorCreate(BaseModel):
    mentor_id: str
    mentor_name: str
    mentor_department: str
    mentor_email: str
    mentor_phoneno: str
    mentor_password: str

@router.get("/stats")
def leader_stats(
    leader_id: str,
    current: dict = Depends(get_current_leader),
    db: Session = Depends(get_db),
):
    """System-wide stats for leader dashboard. Only accessible by leader role."""
    if current.get("leader_id") != leader_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    total_students = db.query(func.count(Student.student_usn)).scalar() or 0
    total_mentors = db.query(func.count(Mentor.mentor_id)).scalar() or 0
    signed_up = db.query(Student).filter(
        Student.student_email.isnot(None),
        Student.student_password.isnot(None),
    ).count()
    profile_created = db.query(Student).filter(
        Student.student_name.isnot(None),
        Student.student_email.isnot(None),
        Student.student_phoneno.isnot(None),
        Student.student_program.isnot(None),
        Student.linkedin.isnot(None),
        Student.semester.isnot(None),
    ).count()
    psychometric_filled = db.query(PsychometricResponse).count()
    report_generated = db.query(Report).count()
    activities_generated = db.query(Activities).count()
    mca_filled = db.query(MentorshipAssessment).count()
    dept_counts = (
        db.query(Mentor.mentor_department, func.count(Student.student_usn))
        .outerjoin(Student, Mentor.mentor_id == Student.assigned_mentor)
        .group_by(Mentor.mentor_department)
        .all()
    )
    departments = [{"department": d, "student_count": c} for d, c in dept_counts]
    return {
        "total_students": total_students,
        "total_mentors": total_mentors,
        "signed_up": signed_up,
        "profile_created": profile_created,
        "form_filled": psychometric_filled,
        "swot_generated": report_generated,
        "activities_generated": activities_generated,
        "mca_filled": mca_filled,
        "departments": departments,
    }


@router.get("/filters")
def leader_filters(
    leader_id: str,
    current: dict = Depends(get_current_leader),
    db: Session = Depends(get_db),
):
    """Return all departments present in the application and all mentors for filter dropdowns."""
    if current.get("leader_id") != leader_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # All departments from mentors
    mentor_depts = [
        str(row[0]).strip() for row in
        db.query(Mentor.mentor_department).distinct().filter(Mentor.mentor_department.isnot(None)).all()
        if row[0] and str(row[0]).strip()
    ]

    # Departments from committee members (department_faculty + allocated_departments for working_committee)
    committee_depts = set()
    for row in db.query(CommitteeMember.department, CommitteeMember.allocated_departments).all():
        dept, allocated = row[0], row[1]
        if dept and str(dept).strip():
            committee_depts.add(str(dept).strip())
        if allocated:
            try:
                arr = json.loads(allocated) if isinstance(allocated, str) else allocated
                if isinstance(arr, list):
                    for d in arr:
                        if d and str(d).strip():
                            committee_depts.add(str(d).strip())
            except (json.JSONDecodeError, TypeError):
                pass

    # Union and collect all department strings
    all_raw = sorted(set(mentor_depts) | committee_depts)

    # Remove departments that should not appear in the list (short codes + spelling variants)
    DEPARTMENTS_TO_REMOVE = {
        "CIVIL",
        "CS",
        "ECE",
        "EEE",
        "IT",
        "MECH",
        "Data Analytics & Mathematial Science",
        "Physics and Electronics",
    }
    all_raw = [d for d in all_raw if d not in DEPARTMENTS_TO_REMOVE]

    # Deduplicate by normalized name (trim + lowercase) so "Forensic science" and "Forensic Science" appear once
    seen_normalized = set()
    all_departments = []
    for d in all_raw:
        key = d.strip().lower()
        if key and key not in seen_normalized:
            seen_normalized.add(key)
            all_departments.append(d.strip())

    mentors = db.query(Mentor.mentor_id, Mentor.mentor_name, Mentor.mentor_department).order_by(Mentor.mentor_department, Mentor.mentor_name).all()
    mentor_list = [
        {"mentor_id": m.mentor_id, "mentor_name": m.mentor_name or m.mentor_id, "department": m.mentor_department or ""}
        for m in mentors
    ]
    return {"departments": all_departments, "mentors": mentor_list}


@router.get("/students")
def leader_students(
    leader_id: str,
    department: Optional[str] = Query(None, description="Filter by mentor department"),
    mentor_id: Optional[str] = Query(None, description="Filter by assigned mentor"),
    without_department: Optional[bool] = Query(False, description="Show only students without department (no mentor or mentor has no department)"),
    without_mentor: Optional[bool] = Query(False, description="Show only students without assigned mentor"),
    view: str = Query("active", description="active | alumni | all"),
    current: dict = Depends(get_current_leader),
    db: Session = Depends(get_db),
):
    """List all students (system-wide). Optional filters: department, mentor_id, without_department, without_mentor."""
    if current.get("leader_id") != leader_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    q = (
        db.query(
            Student,
            Mentor.mentor_name,
            Mentor.mentor_department,
            Mentor.mentor_id,
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
    if without_mentor:
        q = q.filter(Student.assigned_mentor.is_(None))
    if without_department:
        q = q.filter(
            or_(
                Student.assigned_mentor.is_(None),
                Mentor.mentor_department.is_(None),
                Mentor.mentor_department == "",
            )
        )
    if department:
        q = q.filter(Mentor.mentor_department == department)
    if mentor_id:
        q = q.filter(Student.assigned_mentor == mentor_id)
    if view == "alumni":
        q = q.filter(Student.is_alumni.is_(True))
    elif view == "active":
        q = active_students_filter(q)
    q = q.group_by(Student.student_usn, Mentor.mentor_name, Mentor.mentor_department, Mentor.mentor_id)
    all_students = q.all()
    student_list = []
    for row in all_students:
        student, mentor_name, mentor_dept, _mentor_id, has_psy, has_report, has_activities, has_mca = row
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
            "ass_mentor": mentor_name if mentor_name else "No mentor assigned",
            "assigned_mentor": student.assigned_mentor,
            "department": mentor_dept or "",
            "status": " → ".join(statuses),
        })
    return student_list


@router.patch("/students/{student_usn}/mentor")
def leader_assign_student_mentor(
    leader_id: str,
    student_usn: str,
    body: AssignMentorRequest,
    current: dict = Depends(get_current_leader),
    db: Session = Depends(get_db),
):
    """Assign or change a student's mentor (or unassign if mentor_id is null). Leader can do this for any student."""
    if current.get("leader_id") != leader_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_usn} not found")
    if body.mentor_id is not None and body.mentor_id.strip():
        mentor = db.query(Mentor).filter(Mentor.mentor_id == body.mentor_id.strip()).first()
        if not mentor:
            raise HTTPException(status_code=404, detail=f"Mentor {body.mentor_id} not found")
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

@router.post("/mentors")
def create_mentor(
    leader_id: str,
    body: MentorCreate,
    current: dict = Depends(get_current_leader),
    db: Session = Depends(get_db),
):
    """Create a new mentor under the leader dashboard."""
    if current.get("leader_id") != leader_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    existing_mentor = db.query(Mentor).filter(
        or_(Mentor.mentor_id == body.mentor_id, Mentor.mentor_email == body.mentor_email)
    ).first()
    if existing_mentor:
        raise HTTPException(status_code=400, detail="Mentor ID or Email already exists")
    
    validate_password(body.mentor_password)
    hashed_password = hash_password(body.mentor_password)
    
    new_mentor = Mentor(
        mentor_id=body.mentor_id,
        mentor_name=body.mentor_name,
        mentor_department=body.mentor_department,
        mentor_email=body.mentor_email,
        mentor_phoneno=body.mentor_phoneno,
        mentor_password=hashed_password,
    )
    db.add(new_mentor)
    db.commit()
    db.refresh(new_mentor)
    return {"message": "Mentor created successfully", "mentor_id": new_mentor.mentor_id}

@router.get("/mentors")
def get_all_mentors(
    leader_id: str,
    department: Optional[str] = Query(None, description="Filter by mentor department"),
    current: dict = Depends(get_current_leader),
    db: Session = Depends(get_db),
):
    """Get list of mentors."""
    if current.get("leader_id") != leader_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    q = db.query(Mentor)
    if department:
        q = q.filter(Mentor.mentor_department == department)
        
    mentors = q.all()
    return [
        {
            "mentor_id": m.mentor_id,
            "mentor_name": m.mentor_name,
            "mentor_department": m.mentor_department,
            "mentor_email": m.mentor_email,
            "mentor_phoneno": m.mentor_phoneno,
        }
        for m in mentors
    ]

@router.delete("/mentors/{mentor_id_to_delete}")
def delete_mentor(
    leader_id: str,
    mentor_id_to_delete: str,
    current: dict = Depends(get_current_leader),
    db: Session = Depends(get_db),
):
    """Delete a mentor."""
    if current.get("leader_id") != leader_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id_to_delete).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
        
    db.query(Student).filter(Student.assigned_mentor == mentor_id_to_delete).update({"assigned_mentor": None})
    
    db.delete(mentor)
    db.commit()
    return {"message": "Mentor deleted successfully"}
