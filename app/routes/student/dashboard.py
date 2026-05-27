from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_student
from app.db.database import get_db
from app.db.models.MCA_assignments import MentorshipAssessment
from app.db.models.academic_performance import AcademicPerformance, StudentSecondaryMarksheet
from app.db.models.activities_tracking import ActivitiesTracking
from app.db.models.attendance import Attendance
from app.db.models.counseling import CounselingSession
from app.db.models.experience_learning import ExperienceLearning
from app.db.models.ibp_responses import IBPResponse
from app.db.models.meetings import Meetings
from app.db.models.pf16_responses import PF16Response
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.students import Student
from app.schemas.dashboard import (
    DashboardActivityItem,
    DashboardActivities,
    DashboardAcademics,
    DashboardAttendance,
    DashboardCounseling,
    DashboardExperiential,
    DashboardExperientialItem,
    DashboardForms,
    DashboardMeetingItem,
    DashboardMeetings,
    DashboardProfile,
    DashboardSummary,
)


router = APIRouter()


def _max_semesters_for_program(program: str | None) -> int:
    if program and str(program).strip().lower().startswith("bsc"):
        return 3
    return 4


@router.get("/dashboard-summary", response_model=DashboardSummary)
def get_dashboard_summary(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")

    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Attendance
    total_records = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.student_usn == student_usn)
        .scalar()
        or 0
    )
    present_count = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.student_usn == student_usn, func.lower(Attendance.status) == "present")
        .scalar()
        or 0
    )
    absent_count = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.student_usn == student_usn, func.lower(Attendance.status) == "absent")
        .scalar()
        or 0
    )
    late_count = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.student_usn == student_usn, func.lower(Attendance.status) == "late")
        .scalar()
        or 0
    )
    attendance_percentage = None
    if total_records > 0:
        attendance_percentage = round(((present_count + late_count) / total_records) * 100, 2)

    # Academics
    max_semesters = _max_semesters_for_program(student.student_program)
    semesters_filled = (
        db.query(AcademicPerformance.semester)
        .filter(AcademicPerformance.student_usn == student_usn.strip())
        .distinct()
        .count()
        or 0
    )
    secondary_count = (
        db.query(func.count(StudentSecondaryMarksheet.standard))
        .filter(StudentSecondaryMarksheet.student_usn == student_usn.strip())
        .distinct()
        .scalar()
        or 0
    )
    has_secondary_marksheets = secondary_count >= 2

    # Forms completion/lock
    psychometric_completed = (
        db.query(PsychometricResponse.id)
        .filter(PsychometricResponse.student_usn == student_usn.strip())
        .first()
        is not None
    )
    swot_completed = db.query(Report.id).filter(Report.student_usn == student_usn.strip()).first() is not None

    last_mca = (
        db.query(MentorshipAssessment.submitted_at)
        .filter(MentorshipAssessment.student_usn == student_usn.strip())
        .order_by(MentorshipAssessment.submitted_at.desc())
        .first()
    )
    mca_locked = False
    if last_mca and last_mca[0]:
        lock_end = last_mca[0] + timedelta(days=60)
        mca_locked = datetime.utcnow() < lock_end

    pf16_locked = (
        db.query(PF16Response.id)
        .filter(PF16Response.student_usn == student_usn.strip())
        .first()
        is not None
    )
    ibp_locked = (
        db.query(IBPResponse.id)
        .filter(IBPResponse.student_usn == student_usn.strip())
        .first()
        is not None
    )

    # Activities (tracking)
    activities_q = db.query(ActivitiesTracking).filter(ActivitiesTracking.student_usn == student_usn.strip())
    total_activities = activities_q.count() or 0
    approved = (
        db.query(func.count(ActivitiesTracking.id))
        .filter(ActivitiesTracking.student_usn == student_usn.strip(), func.lower(ActivitiesTracking.status) == "approved")
        .scalar()
        or 0
    )
    rejected = (
        db.query(func.count(ActivitiesTracking.id))
        .filter(ActivitiesTracking.student_usn == student_usn.strip(), func.lower(ActivitiesTracking.status) == "rejected")
        .scalar()
        or 0
    )
    pending = max(total_activities - approved - rejected, 0)

    latest_activities = (
        db.query(ActivitiesTracking)
        .filter(ActivitiesTracking.student_usn == student_usn.strip())
        # MySQL doesn't support NULLS LAST; approximate by ordering by
        # whether deadline is NULL first, then by deadline desc and id desc.
        .order_by(
            (ActivitiesTracking.deadline.is_(None)).asc(),
            ActivitiesTracking.deadline.desc(),
            ActivitiesTracking.id.desc(),
        )
        .limit(3)
        .all()
    )

    # Meetings
    now = datetime.utcnow()
    meetings_q = db.query(Meetings).filter(Meetings.student_usn == student_usn.strip())
    total_meetings = meetings_q.count() or 0
    upcoming_meetings = (
        db.query(func.count(Meetings.srno))
        .filter(Meetings.student_usn == student_usn.strip(), Meetings.meeting_date >= now)
        .scalar()
        or 0
    )
    pending_meetings = (
        db.query(func.count(Meetings.srno))
        .filter(Meetings.student_usn == student_usn.strip(), func.lower(Meetings.status) == "pending")
        .scalar()
        or 0
    )
    latest_meeting = (
        db.query(Meetings)
        .filter(Meetings.student_usn == student_usn.strip())
        .order_by(Meetings.meeting_date.desc())
        .first()
    )

    # Counseling
    total_sessions = (
        db.query(func.count(CounselingSession.id))
        .filter(CounselingSession.student_usn == student_usn.strip())
        .scalar()
        or 0
    )
    upcoming_sessions = (
        db.query(func.count(CounselingSession.id))
        .filter(
            CounselingSession.student_usn == student_usn.strip(),
            CounselingSession.status == "scheduled",
            CounselingSession.session_date > now,
        )
        .scalar()
        or 0
    )
    urgent_sessions = (
        db.query(func.count(CounselingSession.id))
        .filter(
            CounselingSession.student_usn == student_usn.strip(),
            CounselingSession.is_urgent == True,  # noqa: E712
            CounselingSession.status == "scheduled",
        )
        .scalar()
        or 0
    )

    # Experiential learning
    exp_total = (
        db.query(func.count(ExperienceLearning.id))
        .filter(ExperienceLearning.student_usn == student_usn.strip())
        .scalar()
        or 0
    )
    exp_latest = (
        db.query(ExperienceLearning)
        .filter(ExperienceLearning.student_usn == student_usn.strip())
        .order_by(ExperienceLearning.created_at.desc())
        .limit(3)
        .all()
    )

    return DashboardSummary(
        profile=DashboardProfile(
            student_usn=student.student_usn,
            student_name=student.student_name,
            student_program=student.student_program,
            semester=student.semester,
        ),
        attendance=DashboardAttendance(
            total_records=total_records,
            present_count=present_count,
            absent_count=absent_count,
            late_count=late_count,
            attendance_percentage=attendance_percentage,
        ),
        academics=DashboardAcademics(
            max_semesters=max_semesters,
            semesters_filled=semesters_filled,
            has_secondary_marksheets=has_secondary_marksheets,
        ),
        forms=DashboardForms(
            psychometric_completed=psychometric_completed,
            swot_completed=swot_completed,
            mca_locked=mca_locked,
            pf16_locked=pf16_locked,
            ibp_locked=ibp_locked,
        ),
        activities=DashboardActivities(
            total=total_activities,
            approved=approved,
            pending=pending,
            rejected=rejected,
            latest=[
                DashboardActivityItem(
                    id=a.id,
                    activity=a.activities,
                    status=a.status,
                    deadline=a.deadline,
                )
                for a in latest_activities
            ],
        ),
        meetings=DashboardMeetings(
            total=total_meetings,
            upcoming=upcoming_meetings,
            pending=pending_meetings,
            latest=(
                DashboardMeetingItem(
                    meeting_id=latest_meeting.id,
                    meeting_date=latest_meeting.meeting_date,
                    status=latest_meeting.status,
                    meeting_mode=getattr(latest_meeting, "meeting_mode", None),
                    venue=latest_meeting.venue,
                )
                if latest_meeting
                else None
            ),
        ),
        counseling=DashboardCounseling(
            total_sessions=total_sessions,
            upcoming_sessions=upcoming_sessions,
            urgent_sessions=urgent_sessions,
        ),
        experiential=DashboardExperiential(
            total=exp_total,
            latest=[
                DashboardExperientialItem(
                    id=e.id,
                    title=e.title,
                    created_at=e.created_at,
                )
                for e in exp_latest
            ],
        ),
    )

