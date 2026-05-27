from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AcademicPerformanceRow(BaseModel):
    course: str = Field(..., description="Course name")
    grade: str = Field("", description="Grade obtained")
    overall_attendance: str = Field("", description="Overall attendance")


class AcademicPerformanceRowWithId(BaseModel):
    """Row in API response, includes id for update/delete."""
    id: int
    course: str = ""
    grade: str = ""
    overall_attendance: str = ""
    is_locked: bool = False  # Row-level lock: if True, cannot edit/delete

    class Config:
        from_attributes = True


class AcademicPerformanceAddRow(BaseModel):
    """Payload to add a single row (save by row)."""
    semester: int = Field(..., ge=1, le=8)
    course: str = Field(..., min_length=1)
    grade: str = Field("", description="Grade obtained")
    overall_attendance: str = Field("", description="Overall attendance")


class AcademicPerformanceUpdateRow(BaseModel):
    """Payload to update a single row."""
    course: str = Field(..., min_length=1)
    grade: str = ""
    overall_attendance: str = ""


class AcademicPerformanceSemesterPayload(BaseModel):
    semester: int = Field(..., ge=1, le=8, description="Semester number (1-3 BSc, 1-4 MSc)")
    rows: List[AcademicPerformanceRow] = Field(..., description="Course rows for this semester")


class AcademicPerformanceSubmit(BaseModel):
    semesters: List[AcademicPerformanceSemesterPayload] = Field(..., description="Data per semester")


class AcademicPerformanceMarksheetResponse(BaseModel):
    """Marksheet information for a semester."""
    semester: int
    marksheet_url: Optional[str] = None  # S3 key
    marksheet_view_url: Optional[str] = None  # Presigned URL for viewing
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SecondaryMarksheetInfo(BaseModel):
    """10th or 12th standard marksheet info."""
    standard: int  # 10 or 12
    marksheet_url: Optional[str] = None
    marksheet_view_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None


class AcademicPerformanceSemesterResponse(BaseModel):
    semester: int
    rows: List[AcademicPerformanceRowWithId]
    marksheet: Optional[AcademicPerformanceMarksheetResponse] = None

    class Config:
        from_attributes = True


class AcademicPerformanceResponse(BaseModel):
    submitted_at: Optional[datetime] = None
    max_semesters: int = Field(..., description="3 for BSc, 4 for MSc")
    can_fill_semester: bool = Field(False, description="True when both 10th and 12th marksheets are uploaded")
    secondary_marksheets: Optional[dict] = Field(default_factory=dict, description="Keys: 10, 12 with marksheet info")
    semesters: List[AcademicPerformanceSemesterResponse] = Field(default_factory=list)
