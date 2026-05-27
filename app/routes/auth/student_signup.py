from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import json
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.utils.cache import redis_client
from app.utils.id_utils import generate_otp
from app.schemas.auth import StudentSignupSchema, OTPValidationSchema
from app.db.models.students import Student
from app.db.database import get_db
from app.core.password import hash_password, validate_password
from app.services.email_services import send_email

router = APIRouter()

@router.post("/signup/student")
async def student_signup(data: StudentSignupSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Handles student signup, validates details, and sends OTP asynchronously.
    """
    # Validate password
    validate_password(data.student_password)

    # Check if email or USN is already registered
    existing_student = db.query(Student).filter(or_(Student.student_email == data.student_email, Student.student_usn == data.student_usn)).first()
    if existing_student:
        if existing_student.student_email == data.student_email and existing_student.student_usn == data.student_usn:
            raise HTTPException(status_code=400, detail=f"Email {data.student_email} and USN {data.student_usn} are already registered")
        elif existing_student.student_email == data.student_email:
            raise HTTPException(status_code=400, detail=f"Email {data.student_email} is already registered with USN {existing_student.student_usn}")
        elif existing_student.student_usn == data.student_usn:
            raise HTTPException(status_code=400, detail=f"USN {data.student_usn} is already registered with email {existing_student.student_email}")
        else:
            raise HTTPException(status_code=400, detail="Email or USN already registered")

    if data.student_password != data.student_confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Generate OTP & store in Redis
    otp = generate_otp(6)
    otp_data = {"otp": otp, "email": data.student_email, "password": hash_password(data.student_password)}
    redis_client.setex(f"otp:{data.student_usn}", 300, json.dumps(otp_data))  # Expires in 5 mins

    # Professional email message
    # Professional email message in HTML format
    email_subject = "Verification OTP for Your Registration"
    email_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{email_subject}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 90%;
            margin: 0 auto;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        h2 {{
            color: #4CAF50;
            font-size: 24px;
        }}
        p {{
            font-size: 16px;
            color: #333333;
            line-height: 1.6;
        }}
        .otp {{
            font-size: 20px;
            font-weight: bold;
            color: #FF5722;
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
        }}
        .footer {{
            font-size: 14px;
            color: #777777;
            margin-top: 20px;
            text-align: left;
        }}
        .footer a {{
            color: #4CAF50;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Dear Student,</h2>
        <p>Thank you for registering with us. To complete your signup process, please use the following One-Time Password (OTP) for verification:</p>
        <p class="otp">{otp}</p>
        <p>This OTP is valid for 5 minutes. Please do not share it with anyone for security reasons.</p>
        <p>If you did not request this registration, please ignore this email. For any assistance, feel free to contact our support team.</p>
        <div class="footer">
            <p>Best regards,</p>
            <p><strong>Mentee Tracker Team</strong><br>Support Team</p>
        </div>
    </div>
</body>
</html>
"""

    # Send OTP in the background
    try:
        background_tasks.add_task(send_email, data.student_email, email_subject, email_body)
    except Exception as e:
        redis_client.delete(f"otp:{data.student_usn}")  # Remove OTP if email sending fails
        raise HTTPException(status_code=500, detail="Failed to send OTP. Please try again.")

    return {"message": "OTP sent to your email. Please verify to complete registration."}


@router.post("/student/{student_usn}/otp")
def validate_otp(student_usn: str, data: OTPValidationSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Validates OTP and completes student signup.
    """
    # Fetch OTP data from Redis
    otp_data_json = redis_client.get(f"otp:{student_usn}")
    if not otp_data_json:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    otp_data = json.loads(otp_data_json)
    
    if otp_data["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Incorrect OTP")

    # Remove OTP after successful validation
    redis_client.delete(f"otp:{student_usn}")

    # Save student to DB
    new_student = Student(student_usn=student_usn, student_email=otp_data["email"], student_password=otp_data["password"])
    db.add(new_student)
    db.commit()

    # Send a welcome email after successful registration
    # Professional welcome email message in HTML format
    subject = "Welcome to Mentee Tracker!"
    message = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 90%;
            margin: 0 auto;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        h2 {{
            color: #4CAF50;
            font-size: 24px;
        }}
        p {{
            font-size: 16px;
            color: #333333;
            line-height: 1.6;
        }}
        .highlight {{
            font-weight: bold;
            color: #FF5722;
        }}
        .footer {{
            font-size: 14px;
            color: #777777;
            margin-top: 20px;
            text-align: left;
        }}
        .footer a {{
            color: #4CAF50;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Dear {student_usn},</h2>
        <p>Congratulations on taking the first step towards your growth journey! We are pleased to inform you that your registration with Mentee Tracker has been successfully completed.</p>
        <p>Here are your login details:</p>
        <ul>
            <li><strong class="highlight">Username (USN):</strong> {student_usn}</li>
            <li><strong class="highlight">Password :</strong> The one's you signed up now in Mentee Tracker.</li>
        </ul>
        <p>With Mentee Tracker, you can seamlessly connect with mentors, track your progress, and achieve your academic and professional goals efficiently.</p>
        <p>If you have any questions or need assistance, feel free to reach out to our support team.</p>
        <p>Welcome aboard! We look forward to being a part of your success.</p>
        <div class="footer">
            <p>Best regards,</p>
            <p><strong>Mentee Tracker Team</strong><br>Support Team</p>
        </div>
    </div>
</body>
</html>
"""

    background_tasks.add_task(send_email, otp_data["email"], subject, message)

    return {"message": f"{student_usn} registered successfully. You can now log in."}
