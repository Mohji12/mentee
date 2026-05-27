from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.students import Student
from app.db.database import get_db
from app.schemas.psychometric import PsychometricForm
from datetime import datetime

router = APIRouter()

@router.post("/psychometric-form")
async def submit_psychometric_form(student_usn: str, form: PsychometricForm, db: Session = Depends(get_db)):
    # Step 1: Get the student's semester from the students table
    student = db.query(Student).filter_by(student_usn=student_usn).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Step 2: Get the most recent psychometric response for this student
    last_response = db.query(PsychometricResponse).filter_by(student_usn=student_usn).order_by(PsychometricResponse.submitted_at.desc()).first()
    
    if last_response:
        # Step 3: Check if the last response was submitted during the current semester
        last_submission_date = last_response.submitted_at
        
        # Determine if the semester is in the first half of the year (Spring - Jan to Jun)
        if 1 <= last_submission_date.month <= 6:
            semester_start_date = datetime.date(last_submission_date.year, 1, 1)  # Start of January
            semester_end_date = datetime.date(last_submission_date.year, 6, 30)  # End of June
        else:
            semester_start_date = datetime.date(last_submission_date.year, 7, 1)  # Start of July
            semester_end_date = datetime.date(last_submission_date.year, 12, 31)  # End of December
        
        # Step 4: Compare the last submission with the current semester's start and end date
        if semester_start_date <= last_submission_date.date() <= semester_end_date:
            raise HTTPException(status_code=400, detail="Psychometric form already submitted for this semester")
    
    # Step 5: Create a new psychometric response entry
    new_response = PsychometricResponse(
        student_usn=student_usn,
        **form.model_dump()  # Assuming the form is a Pydantic model and its fields match the columns in PsychometricResponse
    )

    # Step 6: Add the new response to the database and commit
    db.add(new_response)
    db.commit()

    return {"message": "Psychometric form submitted successfully"}
