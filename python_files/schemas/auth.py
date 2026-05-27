from pydantic import BaseModel

class LoginSchema(BaseModel):
    id: str  # Mentor ID or Student USN (based on role)
    password: str  # Password provided by the user

    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models

class LoginResponseSchema(BaseModel):
    message: str  # Success message
    role: str  # Role of the user (mentor or student)
    access_token: str  # JWT token
    jti: str  # JWT ID to uniquely identify the session
    
    class Config:
        from_attributes = True  # This allows Pydantic to work with SQLAlchemy models

class LogoutRequestSchema(BaseModel):
    jti: str  # JWT ID for the session to be invalidated
    ms_ids: str  # The user identifier (optional for reference)

    class Config:
        from_attributes = True



class OTPValidationSchema(BaseModel):
    otp: str

class StudentSignupSchema(BaseModel):
    student_usn: str
    student_email: str
    student_password: str
    student_confirm_password: str

    class Config:
        from_attributes = True
