from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.schemas.students import StudentProfileSchema, StudentEditSchema
from datetime import datetime, timezone

router = APIRouter()

@router.post("/createprofile")
def create_student_profile(student_usn: str, data: StudentProfileSchema, db: Session = Depends(get_db)):
    """
    Endpoint to create or update a student profile with calculated semester.
    Fields required: name, program, batch, phone number, assigned_mentor.
    """
    # Check if the student exists in the database
    student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

    # Ensure the student's profile is not already complete
    if student.student_name and student.student_program and student.student_batch:
        raise HTTPException(status_code=400, detail=f"Student with USN {student_usn} already has a profile")

    # Calculate semester based on batch start year
    try:
        start_year = int(data.student_batch.split('-')[0])  # Extract batch start year
        current_date = datetime.now(tz=timezone.utc)  # Updated UTC time
        months_since_batch_start = (current_date.year - start_year) * 12 + current_date.month - 7  # July is assumed as start month
        semester = (months_since_batch_start // 6) + 1
        if semester > 8:
            semester = 8  # Cap the semester at 8
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid batch format. Expected format: 'YYYY-YYYY'.")

    # Validate phone number
    if len(data.student_phoneno) != 10 or not data.student_phoneno.isdigit():
        raise HTTPException(status_code=400, detail="Invalid phone number. Must be a 10-digit numeric value.")

    # Update the student's profile
    student.student_name = data.student_name
    student.student_program = data.student_program
    student.student_batch = data.student_batch
    student.student_phoneno = data.student_phoneno  # Update phone number
    student.semester = semester
    student.assigned_mentor = data.assigned_mentor
    student.linkedin = data.linkedin

    # Commit changes to the database
    db.commit()

    return {"message": f"Profile updated successfully for Student USN {student_usn}"}

@router.get("/myprofile")
def get_student_profile(student_usn: str, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a student's profile by their USN.
    Includes mentor details if assigned.
    """
    # Fetch student details
    student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

    # Fetch mentor details
    mentor_name = "No Mentor Assigned"
    if student.assigned_mentor:
        mentor = db.query(Mentor).filter_by(mentor_id=student.assigned_mentor).first()
        if mentor:
            mentor_name = mentor.mentor_name

    # Construct and return the response
    return {
        "student_usn": student.student_usn,
        "student_name": student.student_name,
        "student_email": student.student_email,
        "student_phoneno": student.student_phoneno,  # Include phone number
        "student_program": student.student_program,
        "student_batch": student.student_batch,
        "semester": student.semester,
        "assigned_mentor": mentor_name,
        "linkedin": student.linkedin
    }

@router.put("/editprofile")
def edit_student_profile(student_usn: str, data: StudentEditSchema, db: Session = Depends(get_db)):
    """
    Endpoint to edit a student's profile (name and linkedin).
    Fields allowed for update: name, linkedin.
    """
    # Check if the student exists in the database
    student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

    # Update the student's name and linkedin
    if data.student_name:
        student.student_name = data.student_name  # Update name if provided
    if data.linkedin:
        student.linkedin = data.linkedin  # Update linkedin if provided

    # Commit changes to the database
    db.commit()

    return {"message": f"Profile updated successfully for Student USN {student_usn}"}
