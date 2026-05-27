from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.mentors import Mentor
from app.db.models.students import Student
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.activities import Activities
from app.db.models.mentee_competency_report import MenteeCompetencyReport
from app.db.models.MCA_assignments import MentorshipAssessment

router = APIRouter()

@router.get("/assigned_students")
def get_assigned_students(mentor_id: str, db: Session = Depends(get_db)):
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()

    if not assigned_students:
        raise HTTPException(status_code=404, detail="No students assigned to this mentor")

    student_list = []
    for student in assigned_students:
        statuses = []

        if student.student_email and student.student_password:
            statuses.append("Signed Up")
        if all([
            student.student_name, student.student_email, student.student_phoneno,
            student.student_program, student.semester
        ]):
            statuses.append("Profile Created")

        # Check for related records *inside* the loop, for each student:
        has_psychometric = db.query(PsychometricResponse).filter(PsychometricResponse.student_usn == student.student_usn).first()
        if has_psychometric:
            statuses.append("Form Filled")
        has_swot = db.query(Report).filter(Report.student_usn == student.student_usn).first()
        if has_swot:
            statuses.append("SWOT Generated")
        has_activities = db.query(Activities).filter(Activities.student_usn == student.student_usn).first()
        if has_activities:
            statuses.append("Activities Generated")
        has_mca = db.query(MentorshipAssessment).filter(MentorshipAssessment.student_usn == student.student_usn).first()
        if has_mca:
            statuses.append("MCA FORM Filled")

        # If all steps are present, override with complete flow status
        if all([student.student_email and student.student_password,
                all([
                    student.student_name, student.student_email, student.student_phoneno,
                    student.student_program, student.semester
                ]),
                has_psychometric, has_swot, has_activities, has_mca]):
            statuses = ["Complete Flow till MCA FORM Filled"]

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
            "status": " → ".join(statuses)
        })

    return student_list

@router.get("/student_stats")
def get_mentor_student_statistics(mentor_id: str, db: Session = Depends(get_db)):
    # Verify the mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    # Fetch assigned students
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    if not assigned_students:
        raise HTTPException(status_code=404, detail="No students assigned to this mentor")

    # Initialize counters
    psychometric_filled = 0
    report_generated = 0
    activities_generated = 0

    # Count unique students with observation recommendations
    observation_generated = db.query(
        MenteeCompetencyReport.student_usn
    ).filter(
        MenteeCompetencyReport.student_usn.in_([s.student_usn for s in assigned_students])
    ).distinct().count()

    # Count unique students with MCA form filled
    mca_filled = db.query(
        MentorshipAssessment.student_usn
    ).filter(
        MentorshipAssessment.student_usn.in_([s.student_usn for s in assigned_students])
    ).distinct().count()

    for student in assigned_students:
        # Check if the psychometric form is filled
        psychometric_entry = db.query(PsychometricResponse).filter(
            PsychometricResponse.student_usn == student.student_usn
        ).first()
        if psychometric_entry:
            psychometric_filled += 1

        # Check if the report is generated
        report_entry = db.query(Report).filter(Report.student_usn == student.student_usn).first()
        if report_entry:
            report_generated += 1

        # Check if activities are generated
        activity_entry = db.query(Activities).filter(
            Activities.student_usn == student.student_usn
        ).first()
        if activity_entry:
            activities_generated += 1

    # Return the statistics
    return {
        "total_students": len(assigned_students),
        "psychometric_form_filled": psychometric_filled,
        "report_generated": report_generated,
        "activities_generated": activities_generated,
        "mca_filled": mca_filled,
        "observation_generated": observation_generated,
    }
