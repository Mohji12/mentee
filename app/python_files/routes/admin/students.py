from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models.admin import Admin
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.activities import Activities
from app.db.models.MCA_assignments import MentorshipAssessment
from app.db.models.mentee_competency_report import MenteeCompetencyReport

router = APIRouter()

@router.get("/get_all_students")
def get_all_students(admin_id: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if not admin:
        return JSONResponse(status_code=404, content={"detail": f"Admin with ID {admin_id} not found"})

    all_students = db.query(
        Student,
        Mentor.mentor_name,
        func.count(PsychometricResponse.student_usn).label("has_psy_response"),
        func.count(Report.student_usn).label("has_report"),
        func.count(Activities.student_usn).label("has_activities"),
        func.count(MentorshipAssessment.student_usn).label("has_mca_form")
    )\
    .outerjoin(Mentor, Student.assigned_mentor == Mentor.mentor_id)\
    .outerjoin(PsychometricResponse, Student.student_usn == PsychometricResponse.student_usn)\
    .outerjoin(Report, Student.student_usn == Report.student_usn)\
    .outerjoin(Activities, Student.student_usn == Activities.student_usn)\
    .outerjoin(MentorshipAssessment, Student.student_usn == MentorshipAssessment.student_usn)\
    .group_by(Student.student_usn, Mentor.mentor_name).all()

    if not all_students:
        return JSONResponse(status_code=404, content={"detail": "No students found in the database"})

    student_list = []
    for student, mentor_name, has_psy_response, has_report, has_activities, has_mca_form in all_students:
        statuses = []
        if student.student_email and student.student_password:
            statuses.append("Signed Up")
        if all([student.student_name, student.student_email, student.student_phoneno, student.student_program, student.semester]):
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

        student_list.append({
            "student_usn": student.student_usn,
            "student_name": student.student_name,
            "phone": student.student_phoneno,
            "program": student.student_program,
            "email": student.student_email,
            "linkedin": student.linkedin,
            "semester": student.semester,
            "ass_mentor": mentor_name if mentor_name else "No mentor assigned",
            "status": " → ".join(statuses)
        })

    return student_list

@router.get("/student_stats")
def get_student_statistics(admin_id: str, db: Session = Depends(get_db)):
    # Verify admin exists
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin with ID {admin_id} not found")

    # Total Students
    total_students = db.query(func.count(Student.student_usn)).scalar()

    # Signed Up: Only email and password are required
    signed_up = db.query(func.count()).filter(
        Student.student_email.isnot(None),
        Student.student_password.isnot(None)
    ).scalar()

    # Profile Created: All required fields in the Student table must be filled
    profile_created = db.query(func.count()).filter(
        Student.student_name.isnot(None),
        Student.student_email.isnot(None),
        Student.student_phoneno.isnot(None),
        Student.student_program.isnot(None),
        Student.linkedin.isnot(None),
        Student.semester.isnot(None)
    ).scalar()

    # Form Filled: Student must have a psychometric response entry
    psychometric_filled = db.query(func.count()).filter(
        PsychometricResponse.student_usn.isnot(None)
    ).scalar()

    # SWOT Generated: Student must have a report entry
    report_generated = db.query(func.count()).filter(
        Report.student_usn.isnot(None)
    ).scalar()

    # Activities Generated: Student must have an activity entry
    activities_generated = db.query(func.count()).filter(
        Activities.student_usn.isnot(None)
    ).scalar()

    # MCA Form Filled: Student must have a mentorship assessment entry
    mca_filled = db.query(func.count()).filter(
        MentorshipAssessment.student_usn.isnot(None)
    ).scalar()

    return {
        "total_students": total_students,
        "signed_up": signed_up,
        "profile_created": profile_created,
        "form_filled": psychometric_filled,
        "swot_generated": report_generated,
        "activities_generated": activities_generated,
        "mca_filled": mca_filled,
    }