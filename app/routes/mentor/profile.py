from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.mentors import Mentor
from app.db.database import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class MentorProfileUpdate(BaseModel):
    mentor_name: Optional[str] = None
    mentor_department: Optional[str] = None
    mentor_email: Optional[str] = None
    mentor_phoneno: Optional[str] = None

@router.get("/profile")
def get_mentor_profile(mentor_id: str, db: Session = Depends(get_db)):
    mentor = db.query(Mentor).filter_by(mentor_id=mentor_id.strip()).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"Mentor with ID {mentor_id} not found")

    # Return mentor details
    return {
        "mentor_id": mentor.mentor_id,
        "mentor_name": mentor.mentor_name,
        "mentor_department": mentor.mentor_department,
        "mentor_email": mentor.mentor_email,
        "mentor_phoneno": mentor.mentor_phoneno
    }

@router.put("/editprofile")
def edit_mentor_profile(mentor_id: str, profile_update: MentorProfileUpdate, db: Session = Depends(get_db)):
    mentor = db.query(Mentor).filter_by(mentor_id=mentor_id.strip()).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"Mentor with ID {mentor_id} not found")

    # Update mentor fields if provided
    if profile_update.mentor_name is not None:
        mentor.mentor_name = profile_update.mentor_name
    if profile_update.mentor_department is not None:
        mentor.mentor_department = profile_update.mentor_department
    if profile_update.mentor_email is not None:
        mentor.mentor_email = profile_update.mentor_email
    if profile_update.mentor_phoneno is not None:
        mentor.mentor_phoneno = profile_update.mentor_phoneno

    db.commit()
    return {"message": "Mentor profile updated successfully"}
