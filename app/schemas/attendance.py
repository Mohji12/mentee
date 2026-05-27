from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AttendanceSessionCreate(BaseModel):
    session_name: Optional[str] = None
    duration_minutes: int = 30  # Default 30 minutes validity
    location: Optional[str] = None
    
    class Config:
        from_attributes = True

class AttendanceSessionResponse(BaseModel):
    session_id: str
    mentor_id: str
    session_name: Optional[str]
    qr_code_data: str
    created_at: datetime
    expires_at: datetime
    is_active: bool
    location: Optional[str]
    
    class Config:
        from_attributes = True

class QRCodeScanRequest(BaseModel):
    session_id: str
    student_usn: str
    
    class Config:
        from_attributes = True

class AttendanceMarkRequest(BaseModel):
    session_id: str
    status: str = "present"  # present, absent, late
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class AttendanceResponse(BaseModel):
    id: int
    session_id: str
    student_usn: str
    mentor_id: str
    marked_at: datetime
    status: str
    notes: Optional[str]
    
    class Config:
        from_attributes = True

class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: str
    student_usn: str
    student_name: Optional[str]
    mentor_id: str
    marked_at: datetime
    status: str
    notes: Optional[str]
    session_name: Optional[str]
    
    class Config:
        from_attributes = True

class ManualAttendanceMarkRequest(BaseModel):
    session_id: str
    student_usn: str
    status: str = "present"
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class ManualAttendanceBulkRequest(BaseModel):
    session_id: str
    students: List[dict]  # List of {student_usn, status, notes}
    
    class Config:
        from_attributes = True




