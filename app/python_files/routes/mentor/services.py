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
    mentors = db.query(Mentor).all()
    return mentors