from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy.orm import Session
from app.schemas.auth import LoginSchema
from app.db.models.mentors import Mentor
from app.db.models.students import Student
from app.db.models.admin import Admin
from app.db.models.login import Login
from app.db.database import get_db
from app.core.password import verify_password
from app.core.security import create_access_token
from app.core.dependencies import verify_token

router = APIRouter()

@router.post("/login")
async def login(login_data: LoginSchema, db: Session = Depends(get_db)) -> Any:
    """Authenticate user (mentor, student, or admin) and return a JWT token."""
    user = None
    role = None

    # Check if user is a mentor
    mentor = db.query(Mentor).filter_by(mentor_id=login_data.id).first()
    if mentor and verify_password(login_data.password, mentor.mentor_password):
        user = mentor
        role = "mentor"
    else:
        # Check if user is a student
        student = db.query(Student).filter_by(student_usn=login_data.id).first()
        if student and verify_password(login_data.password, student.student_password):
            user = student
            role = "student"
        else:
            # Check if user is an admin
            admin = db.query(Admin).filter_by(admin_id=login_data.id).first()
            if admin:
                print(f"Admin found: {admin}")  # Debugging log for checking the admin retrieval
                if verify_password(login_data.password, admin.admin_password):
                    user = admin
                    role = "admin"
                else:
                    print("Incorrect password for admin")  # Log for incorrect password
            else:
                print("Admin not found.")  # Log if admin is not found

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token with jti
    token_data = {"ms_ids": login_data.id, "role": role}
    expires_in = 3600 if role == "mentor" else 2700 if role == "student" else 7200  # Admins have longer expiry
    token, jti = create_access_token(data=token_data, expires_delta=timedelta(seconds=expires_in))

    # Store login in DB with updated timestamp
    new_login = Login(
        ms_ids=login_data.id,
        access_token=token,
        jti=jti,  # Store the jti for future reference
        timestamp=datetime.now(timezone.utc),  # Updated for Lambda compatibility
        exp_timestamp=datetime.now(timezone.utc) + timedelta(seconds=expires_in),  # Updated for expiration timestamp
    )
    db.add(new_login)
    db.commit()

    return {
        "message": f"Welcome to {role.capitalize()} Dashboard",
        "role": role,
        "jti": jti,
        "access_token": token,
        "expires_in": expires_in,
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

@router.post("/logout/{ms_id_or_token}")
async def logout(ms_id_or_token: str, db: Session = Depends(get_db)):
    """Logout user by invalidating their token."""
    user_data = None
    try:
        # Check if the input is a token and verify it
        user_data = verify_token(ms_id_or_token)
    except HTTPException:
        pass  # If token verification fails, proceed with ms_id

    if user_data:
        # If token was verified, retrieve the jti
        ms_id = user_data["ms_ids"]
        jti = user_data["jti"]  # Extract the jti from the token payload
    else:
        # Use ms_id directly if the input is not a token
        ms_id = ms_id_or_token
        jti = None

    # Fetch the most recent session or specific session using jti
    if jti:
        session = db.query(Login).filter_by(jti=jti).first()
    else:
        session = db.query(Login).filter_by(ms_ids=ms_id).order_by(Login.timestamp.desc()).first()

    if not session:
        raise HTTPException(status_code=400, detail="No active session found")

    # Invalidate the token immediately by marking the session as inactive
    session.exp_timestamp = datetime.now(timezone.utc)  # Updated to UTC time using timezone aware datetime
    db.commit()

    # Optionally: If you want to track revoked tokens, you could store them in a separate table or a blacklist
    # If you decide to use the revoked_token variable, you can uncomment the following lines:
    # revoked_token = session.access_token
    # print(f"Token with jti {session.jti} has been revoked.")

    return {"message": "Successfully logged out and token has been invalidated"}
