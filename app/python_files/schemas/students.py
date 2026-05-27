from pydantic import BaseModel
from typing import Optional

class StudentProfileSchema(BaseModel):
    student_name: str
    student_program: str
    student_batch: str
    student_phoneno: str  # Added this field
    assigned_mentor: Optional[str] = None
    linkedin: str

    class Config:
        from_attributes = True

class StudentEditSchema(BaseModel):
    student_name: str
    linkedin: str

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
