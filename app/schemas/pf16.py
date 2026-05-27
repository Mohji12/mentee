from pydantic import BaseModel, Field
from typing import Dict, Literal
from datetime import datetime


class PF16FormSubmit(BaseModel):
    """Schema for submitting 16PF form responses"""
    responses: Dict[int, Literal["a", "b", "c"]] = Field(
        ...,
        description="Dictionary mapping question numbers (1-185) to answers (a, b, or c)"
    )


class PF16QuestionResponse(BaseModel):
    """Schema for a single question in API response"""
    question_number: int
    text: str
    options: Dict[str, str]  # {"a": "...", "b": "...", "c": "..."}


class PF16FormResponse(BaseModel):
    """Schema for form data response"""
    questions: list[PF16QuestionResponse]
    is_locked: bool
    submitted_at: datetime | None = None
    responses: Dict[str, str] | None = None  # Responses when form is locked (keys as strings for JSON compatibility)


class PF16LockStatus(BaseModel):
    """Schema for lock status response"""
    is_locked: bool
    submitted_at: datetime | None = None
    message: str
