from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VerificationStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"
    reupload_required = "reupload_required"


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
    is_locked: bool = False

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
    """Marksheet information for a semester (enriched with verification metadata)."""
    semester: int
    marksheet_url: Optional[str] = None
    marksheet_view_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    sgpa: Optional[str] = None
    cgpa: Optional[str] = None
    percentage: Optional[str] = None
    total_credits: Optional[str] = None
    backlogs: Optional[str] = None
    result_status: Optional[str] = None
    academic_year: Optional[str] = None
    verification_status: Optional[str] = "pending"
    remarks: Optional[str] = None
    uploaded_by: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SecondaryMarksheetInfo(BaseModel):
    """10th or 12th standard marksheet info (enriched)."""
    standard: int
    document_type: Optional[str] = None
    marksheet_url: Optional[str] = None
    marksheet_view_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    board_university: Optional[str] = None
    institution_name: Optional[str] = None
    year_of_passing: Optional[str] = None
    percentage_cgpa: Optional[str] = None
    verification_status: Optional[str] = "pending"
    remarks: Optional[str] = None
    uploaded_by: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AcademicPerformanceSemesterResponse(BaseModel):
    semester: int
    rows: List[AcademicPerformanceRowWithId]
    marksheet: Optional[AcademicPerformanceMarksheetResponse] = None

    class Config:
        from_attributes = True


class AcademicDocumentsSummary(BaseModel):
    total_uploaded: int = 0
    missing_count: int = 0
    pending_verification: int = 0
    verified: int = 0
    rejected: int = 0
    reupload_required: int = 0


class AcademicPerformanceResponse(BaseModel):
    submitted_at: Optional[datetime] = None
    max_semesters: int = Field(..., description="3 for BSc, 4 for MSc")
    can_fill_semester: bool = Field(False, description="True when both 10th and 12th marksheets are uploaded")
    secondary_marksheets: Optional[Dict[Any, SecondaryMarksheetInfo]] = Field(default_factory=dict)
    semesters: List[AcademicPerformanceSemesterResponse] = Field(default_factory=list)
    documents_summary: Optional[AcademicDocumentsSummary] = None


class SecondaryMarksheetMetadataUpdate(BaseModel):
    board_university: Optional[str] = None
    institution_name: Optional[str] = None
    year_of_passing: Optional[str] = None
    percentage_cgpa: Optional[str] = None


class SemesterMarksheetMetadataUpdate(BaseModel):
    sgpa: Optional[str] = None
    cgpa: Optional[str] = None
    percentage: Optional[str] = None
    total_credits: Optional[str] = None
    backlogs: Optional[str] = None
    result_status: Optional[str] = None
    academic_year: Optional[str] = None


class AcademicRecordVerifyRequest(BaseModel):
    action: str = Field(..., description="verify | reject | request_reupload")
    remarks: Optional[str] = None


class AcademicDocumentListItem(BaseModel):
    student_usn: str
    student_name: Optional[str] = None
    document_kind: str  # secondary | semester
    standard: Optional[int] = None
    semester: Optional[int] = None
    document_type: Optional[str] = None
    verification_status: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    marksheet_view_url: Optional[str] = None
    remarks: Optional[str] = None
    institution_name: Optional[str] = None
    board_university: Optional[str] = None
    academic_year: Optional[str] = None
