from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ExperienceLearningCreate(BaseModel):
    title: str
    detailed_explanation: str

    class Config:
        from_attributes = True


class ExperienceLearningUpdate(BaseModel):
    title: Optional[str] = None
    detailed_explanation: Optional[str] = None

    class Config:
        from_attributes = True


class ExperienceLearningResponse(BaseModel):
    id: int
    student_usn: Optional[str] = None
    mentor_id: Optional[str] = None
    title: str
    detailed_explanation: str
    proof_file_path: Optional[str] = None
    proof_url: Optional[str] = None  # Will be populated by route
    created_at: datetime
    updated_at: datetime
    student_name: Optional[str] = None  # For mentor view to display student name

    class Config:
        from_attributes = True
