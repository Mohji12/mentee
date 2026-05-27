from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.schemas.auth import LoginSchema
from app.db.models.mentors import Mentor
from app.db.models.students import Student
from app.db.models.login import Login
from app.db.database import get_db
from app.core.password import verify_password
from app.core.security import create_access_token
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/api/verify-token")
async def verify_token_endpoint(current_user: dict = Depends(get_current_user)):
    """Endpoint to verify the token."""
    return {"user_data": current_user}

@router.get("/protected-endpoint")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['user_id']}! This is a protected endpoint."}

@router.post("/authenticate-user")
async def authenticate_user(login_data: LoginSchema, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # Check if the user is a mentor
    mentor = db.query(Mentor).filter_by(mentor_id=login_data.id).first()
    if mentor and verify_password(login_data.password, mentor.mentor_password):
        token_data = {"ms_ids": login_data.id, "role": "mentor"}
        token, jti = create_access_token(data=token_data)
        expires_in = 3600  # Expiration time in seconds (e.g., 1 hour)
        new_login = Login(
            ms_ids=login_data.id,
            access_token=token,
            jti=jti,
            timestamp=datetime.now(tz=timezone.utc),  # Updated UTC time
            exp_timestamp=datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)  # Updated UTC time
        )
        db.add(new_login)
        db.commit()
        return {"message": "Authenticated as Mentor", "role": "mentor", "access_token": token, "expires_in": expires_in}

    # Check if the user is a student
    student = db.query(Student).filter_by(student_usn=login_data.id).first()
    if student and verify_password(login_data.password, student.student_password):
        token_data = {"ms_ids": login_data.id, "role": "student"}
        token, jti = create_access_token(data=token_data)
        expires_in = 2700  # Expiration time in seconds (e.g., 45 minutes)
        new_login = Login(
            ms_ids=login_data.id,
            access_token=token,
            jti=jti,
            timestamp=datetime.now(tz=timezone.utc),  # Updated UTC time
            exp_timestamp=datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)  # Updated UTC time
        )
        db.add(new_login)
        db.commit()
        return {"message": "Authenticated as Student", "role": "student", "access_token": token, "expires_in": expires_in}

    raise HTTPException(status_code=401, detail="Invalid credentials")