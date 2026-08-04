from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DashboardProfile(BaseModel):
    student_usn: str
    student_name: Optional[str] = None
    student_program: Optional[str] = None
    semester: Optional[int] = None
    profile_photo_url: Optional[str] = None
    assigned_mentor_name: Optional[str] = None


class DashboardAttendanceMonth(BaseModel):
    month: str
    present: int = 0
    absent: int = 0
    late: int = 0
    percentage: Optional[float] = None


class DashboardAttendanceTrendPoint(BaseModel):
    label: str
    percentage: Optional[float] = None


class DashboardAttendance(BaseModel):
    total_records: int
    present_count: int
    absent_count: int
    late_count: int
    attendance_percentage: Optional[float] = None
    monthly_breakdown: List[DashboardAttendanceMonth] = Field(default_factory=list)
    semester_attendance_percentage: Optional[float] = None
    overall_attendance_percentage: Optional[float] = None
    trend: List[DashboardAttendanceTrendPoint] = Field(default_factory=list)
    last_updated: Optional[datetime] = None


class DashboardAcademics(BaseModel):
    max_semesters: int
    semesters_filled: int
    has_secondary_marksheets: bool


class DashboardAcademicSemesterScore(BaseModel):
    semester: int
    average_grade_score: Optional[float] = None
    course_count: int = 0


class DashboardAcademicPerformanceDetail(BaseModel):
    overall_percentage: Optional[float] = None
    gpa_cgpa: Optional[str] = None
    internal_marks_summary: Optional[str] = None
    semester_scores: List[DashboardAcademicSemesterScore] = Field(default_factory=list)
    performance_trend: List[DashboardAttendanceTrendPoint] = Field(default_factory=list)
    last_updated: Optional[datetime] = None


class DashboardAcademicRecords(BaseModel):
    total_uploaded: int = 0
    missing_count: int = 0
    pending_verification: int = 0
    verified: int = 0
    rejected: int = 0
    reupload_required: int = 0


class DashboardSemesterProgress(BaseModel):
    current_semester: Optional[int] = None
    max_semesters: int = 4
    completion_percentage: Optional[float] = None
    remaining_duration_label: Optional[str] = None
    last_updated: Optional[datetime] = None


class DashboardForms(BaseModel):
    psychometric_completed: bool
    swot_completed: bool
    mca_locked: bool
    pf16_locked: bool
    ibp_locked: bool


class DashboardPsychometricWidget(BaseModel):
    status: str
    last_assessment_date: Optional[datetime] = None
    score_label: Optional[str] = None
    next_assessment_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None


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
    completion_percentage: Optional[float] = None
    last_updated: Optional[datetime] = None


class DashboardMeetingListItem(BaseModel):
    meeting_id: str
    meeting_date: datetime
    status: Optional[str] = None
    meeting_mode: Optional[str] = None
    venue: Optional[str] = None
    mentor_name: Optional[str] = None
    google_meet_link: Optional[str] = None


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
    completed: int = 0
    missed: int = 0
    latest: Optional[DashboardMeetingItem] = None
    upcoming_list: List[DashboardMeetingListItem] = Field(default_factory=list)
    last_updated: Optional[datetime] = None


class DashboardEmployability(BaseModel):
    latest_score: Optional[int] = None
    previous_score: Optional[int] = None
    score_improvement: Optional[int] = None
    performance_level: Optional[str] = None
    last_updated: Optional[datetime] = None


class DashboardAlumniSessions(BaseModel):
    total: int = 0
    attended: int = 0
    missed: int = 0
    upcoming: int = 0
    last_updated: Optional[datetime] = None


class DashboardExpertSessions(BaseModel):
    industry_total: int = 0
    foreign_total: int = 0
    attended: int = 0
    upcoming: int = 0
    completed: int = 0
    last_updated: Optional[datetime] = None


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


class DashboardNotificationItem(BaseModel):
    id: int
    title: str
    message: str
    category: str
    is_read: bool
    created_at: datetime
    link: Optional[str] = None


class DashboardNotifications(BaseModel):
    items: List[DashboardNotificationItem] = Field(default_factory=list)
    unread_count: int = 0


class DashboardUpcomingEvent(BaseModel):
    event_type: str
    title: str
    event_date: datetime
    status: Optional[str] = None
    link: Optional[str] = None


class DashboardSummaryCard(BaseModel):
    key: str
    title: str
    current_value: str
    status: str
    last_updated: Optional[datetime] = None


class DashboardSummary(BaseModel):
    profile: DashboardProfile
    summary_cards: List[DashboardSummaryCard] = Field(default_factory=list)
    attendance: DashboardAttendance
    semester_progress: DashboardSemesterProgress
    academics: DashboardAcademics
    academic_performance: DashboardAcademicPerformanceDetail
    academic_records: DashboardAcademicRecords = Field(default_factory=DashboardAcademicRecords)
    forms: DashboardForms
    psychometric: DashboardPsychometricWidget
    activities: DashboardActivities
    employability: DashboardEmployability
    meetings: DashboardMeetings
    alumni_sessions: DashboardAlumniSessions
    expert_sessions: DashboardExpertSessions
    counseling: DashboardCounseling
    experiential: DashboardExperiential
    notifications: DashboardNotifications
    upcoming_events: List[DashboardUpcomingEvent] = Field(default_factory=list)
