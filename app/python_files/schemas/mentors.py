from pydantic import BaseModel, EmailStr

class MentorSchema(BaseModel):
    mentor_id: str
    mentor_name: str
    mentor_department: str
    mentor_email: EmailStr  # Valid email
    mentor_phoneno: str
    mentor_password: str
    mentor_confirm_password: str  # Make sure to confirm password on the front end

    class Config:
        from_attributes = True
