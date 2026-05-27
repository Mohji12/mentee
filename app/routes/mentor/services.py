from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.activities import Activities
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report

router= APIRouter()

@router.get("/mentors")
def get_all_mentors(db: Session = Depends(get_db)):
    """Get all mentors from the database, ordered by department and name."""
    mentors = (
        db.query(Mentor)
        .order_by(Mentor.mentor_department, Mentor.mentor_name)
        .all()
    )
    # Return mentors with all fields explicitly
    return [
        {
            "mentor_id": mentor.mentor_id,
            "mentor_name": mentor.mentor_name,
            "mentor_department": mentor.mentor_department,
            "mentor_email": mentor.mentor_email,
            "mentor_phoneno": mentor.mentor_phoneno,
        }
        for mentor in mentors
    ]