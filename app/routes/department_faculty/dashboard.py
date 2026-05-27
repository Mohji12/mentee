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
from app.core.dependencies import get_current_department_faculty
from app.core.password import hash_password
from app.services.email_services import send_email, send_mentor_changed_notification

router = APIRouter()


class CreateMentorRequest(BaseModel):
    mentor_id: str
    mentor_name: str
    mentor_email: EmailStr
    mentor_phoneno: str


class DeleteMentorRequest(BaseModel):
    mentor_id: str


class AssignMentorRequest(BaseModel):
    mentor_id: Optional[str] = None  # None = unassign


@router.get("/stats")
def department_faculty_stats(
    member_id: str,
    current: dict = Depends(get_current_department_faculty),
    db: Session = Depends(get_db),
):
    """Department-level stats. Only students and mentors in this department."""
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
def department_faculty_filters(
    member_id: str,
    current: dict = Depends(get_current_department_faculty),
    db: Session = Depends(get_db),
):
    """Return mentors in this faculty member's department for filtering."""
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


@router.get("/mentors")
def department_faculty_mentors(
    member_id: str,
    current: dict = Depends(get_current_department_faculty),
    db: Session = Depends(get_db),
):
    """Return detailed information about all mentors in this department."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    dept = current.get("department") or ""
    if not dept:
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
        .filter(Mentor.mentor_department == dept)
        .group_by(
            Mentor.mentor_id,
            Mentor.mentor_name,
            Mentor.mentor_email,
            Mentor.mentor_phoneno,
            Mentor.mentor_department,
        )
        .order_by(Mentor.mentor_name)
        .all()
    )
    mentor_list = [
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
    return mentor_list


@router.get("/students")
def department_faculty_students(
    member_id: str,
    mentor_id: Optional[str] = Query(None, description="Filter by assigned mentor"),
    current: dict = Depends(get_current_department_faculty),
    db: Session = Depends(get_db),
):
    """List all students in this department. Optional mentor filter."""
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
def department_faculty_assign_student_mentor(
    member_id: str,
    student_usn: str,
    body: AssignMentorRequest,
    current: dict = Depends(get_current_department_faculty),
    db: Session = Depends(get_db),
):
    """Assign or change a student's mentor (or unassign). Only for students in this department; new mentor must be in same department."""
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


def _generate_mentor_password(mentor_id: str, mentor_name: str) -> str:
    """Generate password as mentor_id@firstThreeLettersOfName."""
    # Extract first 3 letters (alphabet only, ignore spaces/special chars)
    name_clean = ''.join(c for c in mentor_name if c.isalpha())
    if len(name_clean) >= 3:
        first_three = name_clean[:3].upper()
    elif len(name_clean) > 0:
        first_three = name_clean.upper()
    else:
        # Fallback if name has no letters
        first_three = "XYZ"
    return f"{mentor_id}@{first_three}"


@router.post("/mentors")
def create_mentor(
    member_id: str,
    request: CreateMentorRequest,
    current: dict = Depends(get_current_department_faculty),
    db: Session = Depends(get_db),
):
    """Create a new mentor in the faculty member's department. Password auto-generated and emailed."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    dept = current.get("department") or ""
    if not dept:
        raise HTTPException(status_code=400, detail="No department assigned to faculty member")
    
    # Check if mentor_id already exists
    existing = db.query(Mentor).filter(Mentor.mentor_id == request.mentor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Mentor ID '{request.mentor_id}' already exists")
    
    # Check if email already exists
    existing_email = db.query(Mentor).filter(Mentor.mentor_email == request.mentor_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail=f"Email '{request.mentor_email}' already exists")
    
    # Generate password: mentor_id@firstThreeLettersOfName
    plain_password = _generate_mentor_password(request.mentor_id, request.mentor_name)
    hashed_password = hash_password(plain_password)
    
    # Create mentor (department is set to faculty's department)
    new_mentor = Mentor(
        mentor_id=request.mentor_id,
        mentor_name=request.mentor_name,
        mentor_department=dept,
        mentor_email=request.mentor_email,
        mentor_phoneno=request.mentor_phoneno,
        mentor_password=hashed_password,
    )
    db.add(new_mentor)
    db.commit()
    db.refresh(new_mentor)
    
    # Send email with credentials
    email_subject = "Your Login Credentials for Mentee Tracker"
    email_body = f"""
    <h2>Welcome to Mentee Tracker!</h2>
    <p>Dear {request.mentor_name},</p>
    <p>Your mentor account has been created in the Mentee Tracker system. Please find your login credentials below:</p>
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p><strong>Username (Mentor ID):</strong> {request.mentor_id}</p>
        <p><strong>Password:</strong> {plain_password}</p>
        <p><strong>Department:</strong> {dept}</p>
    </div>
    <p>Please log in using these credentials and change your password after first login for security.</p>
    <p>If you have any questions, please contact the administrator.</p>
    <p>Best regards,<br>Mentee Tracker Team</p>
    """
    email_sent = send_email(request.mentor_email, email_subject, email_body)
    
    return {
        "message": "Mentor created successfully",
        "mentor_id": request.mentor_id,
        "mentor_name": request.mentor_name,
        "department": dept,
        "email_sent": email_sent,
    }


@router.delete("/mentors/{mentor_id_to_delete}")
def delete_mentor(
    member_id: str,
    mentor_id_to_delete: str,
    current: dict = Depends(get_current_department_faculty),
    db: Session = Depends(get_db),
):
    """Delete a mentor from the faculty member's department. Unassigns students if any are assigned."""
    if current.get("member_id") != member_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    dept = current.get("department") or ""
    if not dept:
        raise HTTPException(status_code=400, detail="No department assigned to faculty member")
    
    # Find mentor
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id_to_delete).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"Mentor '{mentor_id_to_delete}' not found")
    
    # Verify mentor is in faculty's department
    if mentor.mentor_department != dept:
        raise HTTPException(status_code=403, detail="Mentor does not belong to your department")
    
    # Unassign students from this mentor (set assigned_mentor to NULL)
    student_count = db.query(Student).filter(Student.assigned_mentor == mentor_id_to_delete).count()
    if student_count > 0:
        db.query(Student).filter(Student.assigned_mentor == mentor_id_to_delete).update({Student.assigned_mentor: None})
    
    # Delete mentor
    db.delete(mentor)
    db.commit()
    
    return {
        "message": f"Mentor '{mentor_id_to_delete}' deleted successfully",
        "mentor_id": mentor_id_to_delete,
        "students_unassigned": student_count,
    }
