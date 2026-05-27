from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DashboardProfile(BaseModel):
    student_usn: str
    student_name: Optional[str] = None
    student_program: Optional[str] = None
    semester: Optional[int] = None


class DashboardAttendance(BaseModel):
    total_records: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: Optional[float] = None


class DashboardAcademics(BaseModel):
    max_semesters: int
    semesters_filled: int
    has_secondary_marksheets: bool


class DashboardForms(BaseModel):
    psychometric_completed: bool
    swot_completed: bool
    mca_locked: bool
    pf16_locked: bool
    ibp_locked: bool


class DashboardActivityItem(BaseModel):
    id: str
    activity: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None


class DashboardActivities(BaseModel):
    total: int
    approved: int
    pending: int
    rejected: int
    latest: List[DashboardActivityItem]


class DashboardMeetingItem(BaseModel):
    meeting_id: str
    meeting_date: datetime
    status: Optional[str] = None
    meeting_mode: Optional[str] = None
    venue: Optional[str] = None


class DashboardMeetings(BaseModel):
    total: int
    upcoming: int
    pending: int
    latest: Optional[DashboardMeetingItem] = None


class DashboardCounseling(BaseModel):
    total_sessions: int
    upcoming_sessions: int
    urgent_sessions: int


class DashboardExperientialItem(BaseModel):
    id: int
    title: Optional[str] = None
    created_at: Optional[datetime] = None


class DashboardExperiential(BaseModel):
    total: int
    latest: List[DashboardExperientialItem]


class DashboardSummary(BaseModel):
    profile: DashboardProfile
    attendance: DashboardAttendance
    academics: DashboardAcademics
    forms: DashboardForms
    activities: DashboardActivities
    meetings: DashboardMeetings
    counseling: DashboardCounseling
    experiential: DashboardExperiential

