from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.activities import Activities
from app.db.models.MCA_assignments import MentorshipAssessment
from app.core.dependencies import get_current_program_faculty
from app.core.password import hash_password
from app.services.email_services import send_email

router = APIRouter()


class CreateMentorRequest(BaseModel):
    mentor_id: str
    mentor_name: str
    mentor_email: EmailStr
    mentor_phoneno: str
    mentor_department: str


def _base_student_query_in_programs(db: Session, program_list: list):
    """Students whose student_program is in program_list."""
    return (
        db.query(Student)
        .filter(Student.student_program.in_(program_list))
    )


@router.get("/stats")
def program_faculty_stats(
    member_id: str,
    current: dict = Depends(get_current_program_faculty),
    db: Session = Depends(get_db),
):
    """Stats for this member's allocated programs only."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    allocated = current.get("allocated_programs") or []
    if not allocated:
        return {
            "programs": [],
            "total_students": 0,
            "total_mentors": 0,
            "signed_up": 0,
            "profile_created": 0,
            "form_filled": 0,
            "swot_generated": 0,
            "activities_generated": 0,
            "mca_filled": 0,
            "by_program": [],
        }
    
    # Students in allocated programs
    base = _base_student_query_in_programs(db, allocated)
    total_students = base.count()
    
    # Get unique mentor IDs from students in these programs
    student_usns = [r.student_usn for r in base.with_entities(Student.student_usn).all()]
    mentor_ids = [r.assigned_mentor for r in base.with_entities(Student.assigned_mentor).distinct().all() if r.assigned_mentor]
    total_mentors = len(set(mentor_ids)) if mentor_ids else 0
    
    signed_up = base.filter(
        Student.student_email.isnot(None),
        Student.student_password.isnot(None),
    ).count()
    
    profile_created = base.filter(
        Student.student_name.isnot(None),
        Student.student_email.isnot(None),
        Student.student_phoneno.isnot(None),
        Student.student_program.isnot(None),
        Student.linkedin.isnot(None),
        Student.semester.isnot(None),
    ).count()
    
    form_filled = db.query(PsychometricResponse).filter(PsychometricResponse.student_usn.in_(student_usns)).count() if student_usns else 0
    swot_generated = db.query(Report).filter(Report.student_usn.in_(student_usns)).count() if student_usns else 0
    activities_generated = db.query(Activities).filter(Activities.student_usn.in_(student_usns)).count() if student_usns else 0
    mca_filled = db.query(MentorshipAssessment).filter(MentorshipAssessment.student_usn.in_(student_usns)).count() if student_usns else 0
    
    # Stats by program
    program_counts = (
        db.query(Student.student_program, func.count(Student.student_usn))
        .filter(Student.student_program.in_(allocated))
        .group_by(Student.student_program)
        .all()
    )
    by_program = [{"program": p, "student_count": c} for p, c in program_counts]
    
    return {
        "programs": allocated,
        "total_students": total_students,
        "total_mentors": total_mentors,
        "signed_up": signed_up,
        "profile_created": profile_created,
        "form_filled": form_filled,
        "swot_generated": swot_generated,
        "activities_generated": activities_generated,
        "mca_filled": mca_filled,
        "by_program": by_program,
    }


@router.get("/filters")
def program_faculty_filters(
    member_id: str,
    current: dict = Depends(get_current_program_faculty),
    db: Session = Depends(get_db),
):
    """Return this member's allocated programs and mentors for those programs."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    allocated = current.get("allocated_programs") or []
    programs = sorted(allocated)
    
    # Get mentors who have students in these programs
    student_usns = db.query(Student.student_usn).filter(Student.student_program.in_(allocated)).all()
    student_usn_list = [s[0] for s in student_usns]
    
    mentor_ids = db.query(Student.assigned_mentor).filter(
        Student.student_program.in_(allocated),
        Student.assigned_mentor.isnot(None)
    ).distinct().all()
    mentor_id_list = [m[0] for m in mentor_ids if m[0]]
    
    mentors = []
    if mentor_id_list:
        mentor_objs = (
            db.query(Mentor.mentor_id, Mentor.mentor_name, Mentor.mentor_department)
            .filter(Mentor.mentor_id.in_(mentor_id_list))
            .order_by(Mentor.mentor_department, Mentor.mentor_name)
            .all()
        )
        mentors = [
            {"mentor_id": m.mentor_id, "mentor_name": m.mentor_name or m.mentor_id, "department": m.mentor_department or ""}
            for m in mentor_objs
        ]
    
    # Departments that match allocated programs (for create mentor dropdown and mentor list)
    allowed_depts = sorted(_departments_from_programs(allocated))
    
    return {"programs": programs, "mentors": mentors, "departments": allowed_depts}


@router.get("/students")
def program_faculty_students(
    member_id: str,
    program: Optional[str] = Query(None, description="Filter by one allocated program"),
    mentor_id: Optional[str] = Query(None, description="Filter by assigned mentor"),
    current: dict = Depends(get_current_program_faculty),
    db: Session = Depends(get_db),
):
    """List students in allocated programs only. Optional program and mentor filters."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    allocated = current.get("allocated_programs") or []
    if not allocated:
        return []
    
    program_filter = [program] if program and program in allocated else allocated
    
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
        .outerjoin(Mentor, Student.assigned_mentor == Mentor.mentor_id)
        .filter(Student.student_program.in_(program_filter))
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
            "department": mentor_dept or "",
            "status": " → ".join(statuses),
        })
    return student_list


def _departments_from_programs(program_list: list) -> set:
    """Derive department names from program names, e.g. 'BSc. in Biochemistry & Chemistry' -> 'Biochemistry & Chemistry'."""
    departments = set()
    for p in program_list or []:
        if not p or " in " not in p:
            continue
        dept = p.split(" in ", 1)[1].strip()
        if dept:
            departments.add(dept)
    return departments


def _mentor_ids_in_programs(db: Session, program_list: list):
    """Set of mentor IDs that have at least one student in the given programs."""
    if not program_list:
        return set()
    rows = (
        db.query(Student.assigned_mentor)
        .filter(
            Student.student_program.in_(program_list),
            Student.assigned_mentor.isnot(None),
        )
        .distinct()
        .all()
    )
    return {r[0] for r in rows if r[0]}


def _generate_mentor_password(mentor_id: str, mentor_name: str) -> str:
    name_clean = "".join(c for c in mentor_name if c.isalpha())
    if len(name_clean) >= 3:
        first_three = name_clean[:3].upper()
    elif len(name_clean) > 0:
        first_three = name_clean.upper()
    else:
        first_three = "XYZ"
    return f"{mentor_id}@{first_three}"


@router.get("/mentors")
def program_faculty_mentors(
    member_id: str,
    current: dict = Depends(get_current_program_faculty),
    db: Session = Depends(get_db),
):
    """List mentors in departments that match the member's allocated programs (e.g. BSc. in X -> department X)."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    allocated = current.get("allocated_programs") or []
    allowed_departments = _departments_from_programs(allocated)
    
    if not allowed_departments:
        return []
    
    mentors = (
        db.query(
            Mentor.mentor_id,
            Mentor.mentor_name,
            Mentor.mentor_email,
            Mentor.mentor_phoneno,
            Mentor.mentor_department,
            func.count(Student.student_usn).label("student_count"),
        )
        .outerjoin(Student, Mentor.mentor_id == Student.assigned_mentor)
        .filter(Mentor.mentor_department.in_(allowed_departments))
        .group_by(
            Mentor.mentor_id,
            Mentor.mentor_name,
            Mentor.mentor_email,
            Mentor.mentor_phoneno,
            Mentor.mentor_department,
        )
        .order_by(Mentor.mentor_department, Mentor.mentor_name)
        .all()
    )
    return [
        {
            "mentor_id": m.mentor_id,
            "mentor_name": m.mentor_name or m.mentor_id,
            "mentor_email": m.mentor_email,
            "mentor_phoneno": m.mentor_phoneno,
            "mentor_department": m.mentor_department,
            "student_count": m.student_count or 0,
        }
        for m in mentors
    ]


@router.post("/mentors")
def program_faculty_create_mentor(
    member_id: str,
    request: CreateMentorRequest,
    current: dict = Depends(get_current_program_faculty),
    db: Session = Depends(get_db),
):
    """Create a new mentor. Department must match member's allocated programs (e.g. BSc. in X -> department X)."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    allowed_departments = _departments_from_programs(current.get("allocated_programs") or [])
    if request.mentor_department not in allowed_departments:
        raise HTTPException(
            status_code=400,
            detail=f"Department must be one of: {sorted(allowed_departments)}",
        )
    
    existing = db.query(Mentor).filter(Mentor.mentor_id == request.mentor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Mentor ID '{request.mentor_id}' already exists")
    
    existing_email = db.query(Mentor).filter(Mentor.mentor_email == request.mentor_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail=f"Email '{request.mentor_email}' already exists")
    
    plain_password = _generate_mentor_password(request.mentor_id, request.mentor_name)
    hashed_password = hash_password(plain_password)
    
    new_mentor = Mentor(
        mentor_id=request.mentor_id,
        mentor_name=request.mentor_name,
        mentor_department=request.mentor_department,
        mentor_email=request.mentor_email,
        mentor_phoneno=request.mentor_phoneno,
        mentor_password=hashed_password,
    )
    db.add(new_mentor)
    db.commit()
    db.refresh(new_mentor)
    
    email_subject = "Your Login Credentials for Mentee Tracker"
    email_body = f"""
    <h2>Welcome to Mentee Tracker!</h2>
    <p>Dear {request.mentor_name},</p>
    <p>Your mentor account has been created. Please find your login credentials below:</p>
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p><strong>Username (Mentor ID):</strong> {request.mentor_id}</p>
        <p><strong>Password:</strong> {plain_password}</p>
        <p><strong>Department:</strong> {request.mentor_department}</p>
    </div>
    <p>Please log in and change your password after first login for security.</p>
    <p>Best regards,<br>Mentee Tracker Team</p>
    """
    email_sent = send_email(request.mentor_email, email_subject, email_body)
    
    return {
        "message": "Mentor created successfully",
        "mentor_id": request.mentor_id,
        "mentor_name": request.mentor_name,
        "department": request.mentor_department,
        "email_sent": email_sent,
    }


@router.delete("/mentors/{mentor_id_to_delete}")
def program_faculty_delete_mentor(
    member_id: str,
    mentor_id_to_delete: str,
    current: dict = Depends(get_current_program_faculty),
    db: Session = Depends(get_db),
):
    """Delete a mentor. Allowed only if the mentor's department matches member's allocated programs."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    allowed_departments = _departments_from_programs(current.get("allocated_programs") or [])
    
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id_to_delete).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"Mentor '{mentor_id_to_delete}' not found")
    
    if mentor.mentor_department not in allowed_departments:
        raise HTTPException(
            status_code=403,
            detail="You can only delete mentors in departments that match your allocated programs",
        )
    
    student_count = db.query(Student).filter(Student.assigned_mentor == mentor_id_to_delete).count()
    if student_count > 0:
        db.query(Student).filter(Student.assigned_mentor == mentor_id_to_delete).update({Student.assigned_mentor: None})
    
    db.delete(mentor)
    db.commit()
    
    return {
        "message": f"Mentor '{mentor_id_to_delete}' deleted successfully",
        "mentor_id": mentor_id_to_delete,
        "students_unassigned": student_count,
    }
