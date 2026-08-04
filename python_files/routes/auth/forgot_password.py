from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import json
from sqlalchemy.orm import Session
from app.utils.id_utils import generate_otp
from app.utils.cache import redis_client
from app.db.models.mentors import Mentor
from app.db.models.students import Student
from app.db.database import get_db
from app.core.password import hash_password
from app.services.email_services import send_email

router = APIRouter()

# Endpoint 1: Forgot Password (Step 1: Generate and send OTP)
@router.post("/forgot-password")
def forgot_password(id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Sends an OTP to the registered email for the given user ID (either mentor or student).
    """
    # Check if the ID belongs to a mentor or student and fetch the email
    mentor = db.query(Mentor).filter_by(mentor_id=id).first()
    if mentor:
        email = mentor.mentor_email
        user_type = "mentor"
    else:
        student = db.query(Student).filter_by(student_usn=id).first()
        if student:
            email = student.student_email
            user_type = "student"
        else:
            raise HTTPException(status_code=404, detail="ID not found")

    # Generate OTP & store in Redis
    generated_otp = generate_otp(6)
    redis_client.setex(f"otp:{id}", 300, json.dumps({"otp": generated_otp, "email": email}))  # Expires in 5 mins
    
    email_subject = "Password Reset OTP"
    email_body = f"""
<h2 style="color: #333;">Password Reset Request</h2>
<p style="font-size: 16px; color: #555;">
Dear <strong>{user_type.capitalize()}</strong>,
</p>

<p style="font-size: 16px; color: #555;">
We received a request to reset the password for your account. To proceed, please use the One-Time Password (OTP) below:
</p>

<div style="background-color: #f4f4f4; border: 1px dashed #888; padding: 15px; margin: 20px 0; text-align: center; font-size: 22px; font-weight: bold; color: #222;">
{generated_otp}
</div>

<p style="font-size: 16px; color: #555;">
If you did not request this change, you can safely ignore this email. Your account is secure, and no further action is required.
</p>

<p style="font-size: 16px; color: #555;">
Thank you for being a valued part of our community.
</p>

<p style="font-size: 16px; color: #333;">
Best regards,<br>
<strong>Team Biogred</strong>
</p>
"""

    background_tasks.add_task(send_email, email, email_subject, email_body)

    return {"message": f"OTP sent to your registered email address for {user_type}"}

# Endpoint 2: Verify OTP (Step 2: Verify OTP before resetting password)
@router.post("/verify-otp")
def verify_otp(id: str, otp: str):
    """
    Verifies the OTP for the given user ID.
    """
    # Fetch OTP data from Redis
    otp_data_json = redis_client.get(f"otp:{id}")
    if not otp_data_json:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    otp_data = json.loads(otp_data_json)
    if otp_data["otp"] != otp:
        raise HTTPException(status_code=400, detail="Incorrect OTP")
    
    return {"message": "OTP verified successfully. You can now reset your password."}

# Endpoint 3: Reset Password (Step 3: Reset password after OTP verification)
@router.post("/reset-password")
def reset_password(id: str, new_password: str, confirm_password: str, otp: str, db: Session = Depends(get_db)):
    """
    Resets the password for the given user ID, but only after OTP verification.
    """
    # Fetch OTP data from Redis
    otp_data_json = redis_client.get(f"otp:{id}")
    if not otp_data_json:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    otp_data = json.loads(otp_data_json)
    if otp_data["otp"] != otp:
        raise HTTPException(status_code=400, detail="Incorrect OTP")
    
    # Check if the ID belongs to a mentor or student
    mentor = db.query(Mentor).filter_by(mentor_id=id).first()
    if mentor:
        user = mentor
        user.mentor_password = hash_password(new_password)
    else:
        student = db.query(Student).filter_by(student_usn=id).first()
        if student:
            user = student
            user.student_password = hash_password(new_password)
        else:
            raise HTTPException(status_code=404, detail="ID not found")
    
    # Check password confirmation
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    db.commit()
    redis_client.delete(f"otp:{id}")  # Remove OTP after successful password reset
    
    return {"message": "Password updated successfully."}
