from pydantic import BaseModel
from typing import Optional
from datetime import date

class StudentProfileSchema(BaseModel):
    student_name: str
    student_program: str
    student_batch: str
    student_phoneno: str  # Added this field
    assigned_mentor: str  # Made required - all fields are compulsory
    linkedin: str
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    parent_guardian_contact: Optional[str] = None
    mother_contact: Optional[str] = None
    father_contact: Optional[str] = None

    class Config:
        from_attributes = True

class StudentEditSchema(BaseModel):
    student_name: Optional[str] = None
    student_phoneno: Optional[str] = None
    semester: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None
    parent_guardian_contact: Optional[str] = None
    mother_contact: Optional[str] = None
    father_contact: Optional[str] = None
    linkedin: Optional[str] = None

    class Config:
        from_attributes = True

class StudentSchema(BaseModel):
    student_usn: str
    student_name: str
    student_email: str
    student_phoneno: str
    student_program: str
    semester: int
    student_batch: str
    assigned_mentor: Optional[str] = None
    student_password: str
    student_confirm_password: str
    linkedin: str


    class Config:
        from_attributes = True


class SendEmailRequest(BaseModel):
    student_usn: str
    subject: str
    message: str
