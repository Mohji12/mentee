from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_student
from app.db.database import get_db
from app.db.models.MCA_assignments import MentorshipAssessment
from app.db.models.academic_performance import AcademicPerformance, AcademicPerformanceMarksheet, StudentSecondaryMarksheet
from app.db.models.activities_tracking import ActivitiesTracking
from app.db.models.alumni_sessions import AlumniSession, AlumniSessionAttendance
from app.db.models.attendance import Attendance
from app.db.models.counseling import CounselingSession
from app.db.models.employability import EmployabilityAssessment
from app.db.models.experience_learning import ExperienceLearning
from app.db.models.expert_sessions import ExpertSession, ExpertSessionAttendance
from app.db.models.ibp_responses import IBPResponse
from app.db.models.internal_marks import InternalMarksEntry
from app.db.models.meetings import Meetings
from app.db.models.mentors import Mentor
from app.db.models.notifications import Notification
from app.db.models.pf16_responses import PF16Response
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.students import Student
from app.schemas.dashboard import (
    DashboardAcademicPerformanceDetail,
    DashboardAcademicRecords,
    DashboardAcademicSemesterScore,
    DashboardActivityItem,
    DashboardActivities,
    DashboardAcademics,
    DashboardAlumniSessions,
    DashboardAttendance,
    DashboardAttendanceMonth,
    DashboardAttendanceTrendPoint,
    DashboardCounseling,
    DashboardEmployability,
    DashboardExpertSessions,
    DashboardExperiential,
    DashboardExperientialItem,
    DashboardForms,
    DashboardMeetingItem,
    DashboardMeetingListItem,
    DashboardMeetings,
    DashboardNotificationItem,
    DashboardNotifications,
    DashboardProfile,
    DashboardPsychometricWidget,
    DashboardSemesterProgress,
    DashboardSummary,
    DashboardSummaryCard,
    DashboardUpcomingEvent,
)

router = APIRouter()

_GRADE_POINTS = {
    "o": 10,
    "a+": 9,
    "a": 8,
    "b+": 7,
    "b": 6,
    "c": 5,
    "d": 4,
    "f": 0,
}


def _max_semesters_for_program(program: str | None) -> int:
    if program and str(program).strip().lower().startswith("bsc"):
        return 3
    return 4


def _grade_to_points(grade: str | None) -> float | None:
    if not grade:
        return None
    g = str(grade).strip().lower()
    if g in _GRADE_POINTS:
        return float(_GRADE_POINTS[g])
    try:
        val = float(g.replace("%", ""))
        if val <= 10:
            return val
        return val / 10.0
    except ValueError:
        return None


def _performance_level_from_score(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Very Good"
    if score >= 50:
        return "Good"
    return "Needs Improvement"


def _attendance_pct(present: int, late: int, total: int) -> float | None:
    if total <= 0:
        return None
    return round(((present + late) / total) * 100, 2)


def _build_attendance_stats(db: Session, student_usn: str) -> tuple[dict, list[DashboardAttendanceMonth], list[DashboardAttendanceTrendPoint], datetime | None]:
    rows = (
        db.query(Attendance.status, Attendance.marked_at)
        .filter(Attendance.student_usn == student_usn.strip())
        .all()
    )
    present = absent = late = 0
    monthly: dict[str, dict[str, int]] = defaultdict(lambda: {"present": 0, "absent": 0, "late": 0})
    last_updated = None
    for status, marked_at in rows:
        st = (status or "").lower()
        if st == "present":
            present += 1
        elif st == "absent":
            absent += 1
        elif st == "late":
            late += 1
        if marked_at:
            if last_updated is None or marked_at > last_updated:
                last_updated = marked_at
            key = marked_at.strftime("%Y-%m")
            if st == "present":
                monthly[key]["present"] += 1
            elif st == "absent":
                monthly[key]["absent"] += 1
            elif st == "late":
                monthly[key]["late"] += 1

    total = len(rows)
    overall_pct = _attendance_pct(present, late, total)
    monthly_breakdown: list[DashboardAttendanceMonth] = []
    trend: list[DashboardAttendanceTrendPoint] = []
    for month in sorted(monthly.keys())[-6:]:
        m = monthly[month]
        t = m["present"] + m["absent"] + m["late"]
        pct = _attendance_pct(m["present"], m["late"], t)
        monthly_breakdown.append(
            DashboardAttendanceMonth(
                month=month,
                present=m["present"],
                absent=m["absent"],
                late=m["late"],
                percentage=pct,
            )
        )
        trend.append(DashboardAttendanceTrendPoint(label=month, percentage=pct))

    stats = {
        "total_records": total,
        "present_count": present,
        "absent_count": absent,
        "late_count": late,
        "attendance_percentage": overall_pct,
        "overall_attendance_percentage": overall_pct,
        "semester_attendance_percentage": overall_pct,
    }
    return stats, monthly_breakdown, trend, last_updated


@router.get(
    "/dashboard-summary",
    response_model=DashboardSummary,
    summary="Student dashboard analytics",
    description="Returns profile, attendance, activities, meetings, employability, academic performance, notifications, and upcoming events in one response.",
)
def get_dashboard_summary(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")

    usn = student_usn.strip()
    student = db.query(Student).filter(Student.student_usn == usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    mentor_name = None
    if student.assigned_mentor:
        mentor = db.query(Mentor).filter(Mentor.mentor_id == student.assigned_mentor).first()
        if mentor:
            mentor_name = mentor.mentor_name

    att_stats, monthly_breakdown, att_trend, att_last_updated = _build_attendance_stats(db, usn)

    max_semesters = _max_semesters_for_program(student.student_program)
    semesters_filled = (
        db.query(AcademicPerformance.semester)
        .filter(AcademicPerformance.student_usn == usn)
        .distinct()
        .count()
        or 0
    )
    secondary_count = (
        db.query(func.count(StudentSecondaryMarksheet.standard))
        .filter(StudentSecondaryMarksheet.student_usn == usn)
        .distinct()
        .scalar()
        or 0
    )
    has_secondary_marksheets = secondary_count >= 2

    psychometric_row = (
        db.query(PsychometricResponse)
        .filter(PsychometricResponse.student_usn == usn)
        .order_by(PsychometricResponse.submitted_at.desc())
        .first()
    )
    psychometric_completed = psychometric_row is not None
    swot_completed = db.query(Report.id).filter(Report.student_usn == usn).first() is not None

    last_mca = (
        db.query(MentorshipAssessment.submitted_at)
        .filter(MentorshipAssessment.student_usn == usn)
        .order_by(MentorshipAssessment.submitted_at.desc())
        .first()
    )
    mca_locked = False
    if last_mca and last_mca[0]:
        lock_end = last_mca[0] + timedelta(days=60)
        mca_locked = datetime.utcnow() < lock_end

    pf16_locked = db.query(PF16Response.id).filter(PF16Response.student_usn == usn).first() is not None
    ibp_locked = db.query(IBPResponse.id).filter(IBPResponse.student_usn == usn).first() is not None

    activity_counts = (
        db.query(
            func.count(ActivitiesTracking.id),
            func.sum(case((func.lower(ActivitiesTracking.status) == "approved", 1), else_=0)),
            func.sum(case((func.lower(ActivitiesTracking.status) == "rejected", 1), else_=0)),
        )
        .filter(ActivitiesTracking.student_usn == usn)
        .first()
    )
    total_activities = int(activity_counts[0] or 0)
    approved = int(activity_counts[1] or 0)
    rejected = int(activity_counts[2] or 0)
    pending = max(total_activities - approved - rejected, 0)
    activity_completion_pct = round((approved / total_activities) * 100, 2) if total_activities else None

    latest_activities = (
        db.query(ActivitiesTracking)
        .filter(ActivitiesTracking.student_usn == usn)
        .order_by(
            (ActivitiesTracking.deadline.is_(None)).asc(),
            ActivitiesTracking.deadline.desc(),
            ActivitiesTracking.id.desc(),
        )
        .limit(3)
        .all()
    )
    activity_last_updated = None
    if latest_activities:
        for a in latest_activities:
            if a.deadline and (activity_last_updated is None or a.deadline > activity_last_updated):
                activity_last_updated = a.deadline

    now = datetime.utcnow()
    meetings_all = db.query(Meetings).filter(Meetings.student_usn == usn).all()
    total_meetings = len(meetings_all)
    upcoming_meetings = pending_meetings = completed_meetings = missed_meetings = 0
    latest_meeting = None
    upcoming_list: list[DashboardMeetingListItem] = []
    mentor_cache: dict[str, str | None] = {}

    for m in sorted(meetings_all, key=lambda x: x.meeting_date or now):
        mid = m.mentor_id
        if mid not in mentor_cache:
            ment = db.query(Mentor).filter(Mentor.mentor_id == mid).first()
            mentor_cache[mid] = ment.mentor_name if ment else None
        mdate = m.meeting_date
        status_l = (m.status or "").lower()
        att_l = (m.attendance or "").lower() if m.attendance else ""
        if mdate and mdate >= now:
            upcoming_meetings += 1
            if len(upcoming_list) < 5:
                upcoming_list.append(
                    DashboardMeetingListItem(
                        meeting_id=m.id,
                        meeting_date=mdate,
                        status=m.status,
                        meeting_mode=getattr(m, "meeting_mode", None),
                        venue=m.venue,
                        mentor_name=mentor_cache.get(mid),
                        google_meet_link=getattr(m, "google_meet_link", None),
                    )
                )
        elif mdate and mdate < now:
            if status_l in ("completed", "done") or att_l in ("present", "attended"):
                completed_meetings += 1
            elif att_l in ("absent", "missed") or status_l in ("missed", "cancelled"):
                missed_meetings += 1
            else:
                completed_meetings += 1
        if status_l == "pending":
            pending_meetings += 1
        if latest_meeting is None or (mdate and (latest_meeting.meeting_date is None or mdate > latest_meeting.meeting_date)):
            latest_meeting = m

    meeting_last_updated = latest_meeting.meeting_date if latest_meeting else None

    counseling_counts = (
        db.query(
            func.count(CounselingSession.id),
            func.sum(
                case(
                    (
                        (CounselingSession.status == "scheduled") & (CounselingSession.session_date > now),
                        1,
                    ),
                    else_=0,
                )
            ),
            func.sum(
                case(
                    (
                        (CounselingSession.is_urgent == True)  # noqa: E712
                        & (CounselingSession.status == "scheduled"),
                        1,
                    ),
                    else_=0,
                )
            ),
        )
        .filter(CounselingSession.student_usn == usn)
        .first()
    )
    total_sessions = int(counseling_counts[0] or 0)
    upcoming_sessions = int(counseling_counts[1] or 0)
    urgent_sessions = int(counseling_counts[2] or 0)

    exp_total = (
        db.query(func.count(ExperienceLearning.id))
        .filter(ExperienceLearning.student_usn == usn)
        .scalar()
        or 0
    )
    exp_latest = (
        db.query(ExperienceLearning)
        .filter(ExperienceLearning.student_usn == usn)
        .order_by(ExperienceLearning.created_at.desc())
        .limit(3)
        .all()
    )

    employability_rows = (
        db.query(EmployabilityAssessment)
        .filter(EmployabilityAssessment.student_usn == usn)
        .order_by(EmployabilityAssessment.assessed_at.desc())
        .limit(2)
        .all()
    )
    latest_emp = employability_rows[0] if employability_rows else None
    prev_emp = employability_rows[1] if len(employability_rows) > 1 else None
    emp_improvement = None
    if latest_emp and prev_emp:
        emp_improvement = latest_emp.score - prev_emp.score

    alumni_att = (
        db.query(AlumniSessionAttendance, AlumniSession)
        .join(AlumniSession, AlumniSession.id == AlumniSessionAttendance.session_id)
        .filter(AlumniSessionAttendance.student_usn == usn)
        .all()
    )
    alumni_attended = sum(1 for a, _ in alumni_att if (a.status or "").lower() == "attended")
    alumni_missed = sum(1 for a, _ in alumni_att if (a.status or "").lower() == "missed")
    alumni_upcoming = (
        db.query(func.count(AlumniSession.id))
        .filter(AlumniSession.session_date >= now)
        .scalar()
        or 0
    )
    alumni_total = alumni_attended + alumni_missed + alumni_upcoming

    expert_att = (
        db.query(ExpertSessionAttendance, ExpertSession)
        .join(ExpertSession, ExpertSession.id == ExpertSessionAttendance.session_id)
        .filter(ExpertSessionAttendance.student_usn == usn)
        .all()
    )
    expert_attended = sum(1 for a, _ in expert_att if (a.status or "").lower() == "attended")
    industry_total = (
        db.query(func.count(ExpertSession.id))
        .filter(func.lower(ExpertSession.expert_type) == "industry")
        .scalar()
        or 0
    )
    foreign_total = (
        db.query(func.count(ExpertSession.id))
        .filter(func.lower(ExpertSession.expert_type) == "foreign")
        .scalar()
        or 0
    )
    expert_upcoming = (
        db.query(func.count(ExpertSession.id))
        .filter(ExpertSession.session_date >= now)
        .scalar()
        or 0
    )
    expert_completed = sum(1 for _, s in expert_att if s.session_date and s.session_date < now)

    acad_rows = (
        db.query(AcademicPerformance)
        .filter(AcademicPerformance.student_usn == usn)
        .all()
    )
    sem_scores: dict[int, list[float]] = defaultdict(list)
    acad_last_updated = None
    for row in acad_rows:
        pts = _grade_to_points(row.grade)
        if pts is not None:
            sem_scores[row.semester].append(pts)
        if row.created_at and (acad_last_updated is None or row.created_at > acad_last_updated):
            acad_last_updated = row.created_at

    semester_score_models: list[DashboardAcademicSemesterScore] = []
    perf_trend: list[DashboardAttendanceTrendPoint] = []
    all_pts: list[float] = []
    for sem in sorted(sem_scores.keys()):
        vals = sem_scores[sem]
        avg = round(sum(vals) / len(vals), 2) if vals else None
        if avg is not None:
            all_pts.extend(vals)
            perf_trend.append(
                DashboardAttendanceTrendPoint(label=f"Sem {sem}", percentage=round(avg * 10, 2))
            )
        semester_score_models.append(
            DashboardAcademicSemesterScore(semester=sem, average_grade_score=avg, course_count=len(vals))
        )

    overall_pct = round(sum(all_pts) / len(all_pts) * 10, 2) if all_pts else None

    # Academic records document stats
    secondary_docs = (
        db.query(StudentSecondaryMarksheet)
        .filter(StudentSecondaryMarksheet.student_usn == usn)
        .all()
    )
    semester_docs = (
        db.query(AcademicPerformanceMarksheet)
        .filter(AcademicPerformanceMarksheet.student_usn == usn)
        .all()
    )
    sec_by = {m.standard for m in secondary_docs}
    sem_by = {m.semester for m in semester_docs}
    ar_total = len(secondary_docs) + len(semester_docs)
    ar_missing = (0 if 10 in sec_by else 1) + (0 if 12 in sec_by else 1)
    for s in range(1, max_semesters + 1):
        if s not in sem_by:
            ar_missing += 1
    ar_pending = ar_verified = ar_rejected = ar_reupload = 0
    for d in list(secondary_docs) + list(semester_docs):
        st = (d.verification_status or "pending").lower()
        if st == "verified":
            ar_verified += 1
        elif st == "rejected":
            ar_rejected += 1
        elif st == "reupload_required":
            ar_reupload += 1
        else:
            ar_pending += 1

    internal_count = (
        db.query(func.count(InternalMarksEntry.id))
        .filter(InternalMarksEntry.student_usn == usn)
        .scalar()
        or 0
    )
    internal_summary = f"{internal_count} internal mark entries" if internal_count else None

    current_sem = student.semester or 1
    sem_completion = round((current_sem / max_semesters) * 100, 2) if max_semesters else None
    remaining = max(max_semesters - current_sem, 0)
    remaining_label = f"{remaining} semester(s) remaining" if remaining else "Final semester"

    notif_rows = (
        db.query(Notification)
        .filter(Notification.student_usn == usn)
        .order_by(Notification.is_read.asc(), Notification.created_at.desc())
        .limit(10)
        .all()
    )
    unread_count = (
        db.query(func.count(Notification.id))
        .filter(Notification.student_usn == usn, Notification.is_read == False)  # noqa: E712
        .scalar()
        or 0
    )

    upcoming_events: list[DashboardUpcomingEvent] = []
    for item in upcoming_list:
        upcoming_events.append(
            DashboardUpcomingEvent(
                event_type="meeting",
                title=f"Mentoring session ({item.mentor_name or 'Mentor'})",
                event_date=item.meeting_date,
                status=item.status,
                link=f"/student/{usn}/scheduled_meetings",
            )
        )
    for a in latest_activities:
        if a.deadline and a.deadline >= now:
            upcoming_events.append(
                DashboardUpcomingEvent(
                    event_type="activity",
                    title=a.activities or "Activity",
                    event_date=a.deadline,
                    status=a.status,
                    link=f"/student/{usn}/activities",
                )
            )
    future_alumni = (
        db.query(AlumniSession)
        .filter(AlumniSession.session_date >= now)
        .order_by(AlumniSession.session_date.asc())
        .limit(5)
        .all()
    )
    for s in future_alumni:
        upcoming_events.append(
            DashboardUpcomingEvent(
                event_type="alumni_session",
                title=s.session_title,
                event_date=s.session_date,
                status="scheduled",
                link=f"/student/{usn}/dashboard",
            )
        )
    future_expert = (
        db.query(ExpertSession)
        .filter(ExpertSession.session_date >= now)
        .order_by(ExpertSession.session_date.asc())
        .limit(5)
        .all()
    )
    for s in future_expert:
        upcoming_events.append(
            DashboardUpcomingEvent(
                event_type="expert_session",
                title=s.session_title,
                event_date=s.session_date,
                status=s.expert_type,
                link=f"/student/{usn}/dashboard",
            )
        )
    upcoming_events.sort(key=lambda e: e.event_date)

    psychometric_status = "Completed" if psychometric_completed else "Pending"
    psych_last = psychometric_row.submitted_at if psychometric_row else None

    summary_cards = [
        DashboardSummaryCard(
            key="attendance",
            title="Attendance Percentage",
            current_value=f"{att_stats['attendance_percentage']}%" if att_stats["attendance_percentage"] is not None else "—",
            status="On track" if (att_stats["attendance_percentage"] or 0) >= 75 else "Needs attention",
            last_updated=att_last_updated,
        ),
        DashboardSummaryCard(
            key="employability",
            title="Employability Score",
            current_value=str(latest_emp.score) if latest_emp else "—",
            status=latest_emp.performance_level if latest_emp else "Not assessed",
            last_updated=latest_emp.assessed_at if latest_emp else None,
        ),
        DashboardSummaryCard(
            key="semester",
            title="Current Semester",
            current_value=str(current_sem),
            status=remaining_label,
            last_updated=datetime.utcnow(),
        ),
        DashboardSummaryCard(
            key="activities_completed",
            title="Completed Activities",
            current_value=str(approved),
            status=f"{pending} pending",
            last_updated=activity_last_updated,
        ),
        DashboardSummaryCard(
            key="activities_pending",
            title="Pending Activities",
            current_value=str(pending),
            status="Action required" if pending else "Clear",
            last_updated=activity_last_updated,
        ),
        DashboardSummaryCard(
            key="mentoring_sessions",
            title="Total Mentoring Sessions",
            current_value=str(total_meetings),
            status=f"{upcoming_meetings} upcoming",
            last_updated=meeting_last_updated,
        ),
        DashboardSummaryCard(
            key="alumni_sessions",
            title="Alumni Sessions Attended",
            current_value=str(alumni_attended),
            status=f"{alumni_missed} missed",
            last_updated=datetime.utcnow(),
        ),
        DashboardSummaryCard(
            key="expert_sessions",
            title="Expert Sessions Attended",
            current_value=str(expert_attended),
            status=f"{expert_upcoming} upcoming",
            last_updated=datetime.utcnow(),
        ),
        DashboardSummaryCard(
            key="psychometric",
            title="Psychometric Assessment",
            current_value=psychometric_status,
            status="Complete" if psychometric_completed else "Incomplete",
            last_updated=psych_last,
        ),
        DashboardSummaryCard(
            key="academics",
            title="Academic Performance",
            current_value=f"{overall_pct}%" if overall_pct is not None else "—",
            status=f"{semesters_filled}/{max_semesters} semesters",
            last_updated=acad_last_updated,
        ),
    ]

    return DashboardSummary(
        profile=DashboardProfile(
            student_usn=student.student_usn,
            student_name=student.student_name,
            student_program=student.student_program,
            semester=student.semester,
            profile_photo_url=student.profile_photo_url,
            assigned_mentor_name=mentor_name,
        ),
        summary_cards=summary_cards,
        attendance=DashboardAttendance(
            total_records=att_stats["total_records"],
            present_count=att_stats["present_count"],
            absent_count=att_stats["absent_count"],
            late_count=att_stats["late_count"],
            attendance_percentage=att_stats["attendance_percentage"],
            monthly_breakdown=monthly_breakdown,
            semester_attendance_percentage=att_stats["semester_attendance_percentage"],
            overall_attendance_percentage=att_stats["overall_attendance_percentage"],
            trend=att_trend,
            last_updated=att_last_updated,
        ),
        semester_progress=DashboardSemesterProgress(
            current_semester=student.semester,
            max_semesters=max_semesters,
            completion_percentage=sem_completion,
            remaining_duration_label=remaining_label,
            last_updated=datetime.utcnow(),
        ),
        academics=DashboardAcademics(
            max_semesters=max_semesters,
            semesters_filled=semesters_filled,
            has_secondary_marksheets=has_secondary_marksheets,
        ),
        academic_performance=DashboardAcademicPerformanceDetail(
            overall_percentage=overall_pct,
            gpa_cgpa=None,
            internal_marks_summary=internal_summary,
            semester_scores=semester_score_models,
            performance_trend=perf_trend,
            last_updated=acad_last_updated,
        ),
        academic_records=DashboardAcademicRecords(
            total_uploaded=ar_total,
            missing_count=ar_missing,
            pending_verification=ar_pending,
            verified=ar_verified,
            rejected=ar_rejected,
            reupload_required=ar_reupload,
        ),
        forms=DashboardForms(
            psychometric_completed=psychometric_completed,
            swot_completed=swot_completed,
            mca_locked=mca_locked,
            pf16_locked=pf16_locked,
            ibp_locked=ibp_locked,
        ),
        psychometric=DashboardPsychometricWidget(
            status=psychometric_status,
            last_assessment_date=psych_last,
            score_label="Submitted" if psychometric_completed else None,
            next_assessment_date=None,
            last_updated=psych_last,
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
            completion_percentage=activity_completion_pct,
            last_updated=activity_last_updated,
        ),
        employability=DashboardEmployability(
            latest_score=latest_emp.score if latest_emp else None,
            previous_score=prev_emp.score if prev_emp else None,
            score_improvement=emp_improvement,
            performance_level=latest_emp.performance_level if latest_emp else None,
            last_updated=latest_emp.assessed_at if latest_emp else None,
        ),
        meetings=DashboardMeetings(
            total=total_meetings,
            upcoming=upcoming_meetings,
            pending=pending_meetings,
            completed=completed_meetings,
            missed=missed_meetings,
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
            upcoming_list=upcoming_list,
            last_updated=meeting_last_updated,
        ),
        alumni_sessions=DashboardAlumniSessions(
            total=alumni_total,
            attended=alumni_attended,
            missed=alumni_missed,
            upcoming=alumni_upcoming,
            last_updated=datetime.utcnow(),
        ),
        expert_sessions=DashboardExpertSessions(
            industry_total=industry_total,
            foreign_total=foreign_total,
            attended=expert_attended,
            upcoming=expert_upcoming,
            completed=expert_completed,
            last_updated=datetime.utcnow(),
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
        notifications=DashboardNotifications(
            items=[
                DashboardNotificationItem(
                    id=n.id,
                    title=n.title,
                    message=n.message,
                    category=n.category,
                    is_read=n.is_read,
                    created_at=n.created_at,
                    link=n.link,
                )
                for n in notif_rows
            ],
            unread_count=unread_count,
        ),
        upcoming_events=upcoming_events[:15],
    )


@router.patch(
    "/notifications/{notification_id}/read",
    summary="Mark notification as read",
)
def mark_notification_read(
    student_usn: str,
    notification_id: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    row = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.student_usn == student_usn.strip())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Notification not found")
    row.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}


@router.patch(
    "/notifications/read-all",
    summary="Mark all notifications as read",
)
def mark_all_notifications_read(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    db.query(Notification).filter(
        Notification.student_usn == student_usn.strip(),
        Notification.is_read == False,  # noqa: E712
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
