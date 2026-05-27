from pydantic import BaseModel

class AdminProfile(BaseModel):
    admin_id: str
    admin_name: str
    admin_department: str
    admin_campus: str
    admin_email: str
    admin_phoneno: str

    class Config:
        from_attributes = True
