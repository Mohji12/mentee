from pydantic import BaseModel, Field
from typing import Dict, Literal
from datetime import datetime


class IBPFormSubmit(BaseModel):
    """Schema for submitting IBP form responses"""
    responses: Dict[int, Literal[1, 2, 3, 4, 5]] = Field(
        ...,
        description="Dictionary mapping question numbers (1-36) to answers (1-5: Rarely to Always)"
    )


class IBPQuestionResponse(BaseModel):
    """Schema for a single question in API response"""
    question_number: int
    text: str
    options: Dict[str, str]  # {"1": "Rarely", "2": "Occasionally", ...}


class IBPFormResponse(BaseModel):
    """Schema for form data response"""
    questions: list[IBPQuestionResponse]
    is_locked: bool
    submitted_at: datetime | None = None
    responses: Dict[str, int] | None = None  # Responses when form is locked (keys as strings for JSON compatibility)


class IBPLockStatus(BaseModel):
    """Schema for lock status response"""
    is_locked: bool
    submitted_at: datetime | None = None
    message: str
