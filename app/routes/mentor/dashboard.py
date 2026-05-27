from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Optional
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.meetings import Meetings
from app.db.models.activities_tracking import ActivitiesTracking
from app.db.models.activity_submissions import ActivitySubmissions
from app.db.models.attendance import Attendance
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.swot import SWOT
from app.db.models.MCA_assignments import MentorshipAssessment
from app.db.models.pf16_responses import PF16Response
from app.db.models.ibp_responses import IBPResponse
from app.db.models.counseling import CounselingSession

router = APIRouter()


@router.get("/dashboard/alerts")
def get_dashboard_alerts(mentor_id: str, db: Session = Depends(get_db)):
    """Get alerts for the mentor dashboard - upcoming meetings, overdue submissions, pending appointments."""
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    alerts = []
    
    # Get assigned students
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    student_usns = [s.student_usn for s in assigned_students]
    
    if not student_usns:
        return {"alerts": [], "summary": {"total": 0, "urgent": 0, "warning": 0, "info": 0}}
    
    # 1. Upcoming meetings today
    try:
        meetings_today = db.query(Meetings).filter(
            Meetings.mentor_id == mentor_id,
            Meetings.meeting_date >= today_start,
            Meetings.meeting_date <= today_end,
            Meetings.status.in_(["scheduled", "confirmed"])
        ).all()
        
        for meeting in meetings_today:
            alerts.append({
                "type": "meeting_today",
                "priority": "info",
                "title": "Meeting Today",
                "message": f"Meeting with {meeting.student_usn} at {meeting.meeting_date.strftime('%I:%M %p') if meeting.meeting_date else 'TBD'}",
                "student_usn": meeting.student_usn,
                "action_url": f"/mentor/{mentor_id}/meetings"
            })
    except Exception:
        pass
    
    # 2. Pending appointment requests
    try:
        pending_appointments = db.query(Meetings).filter(
            Meetings.mentor_id == mentor_id,
            Meetings.status == "pending"
        ).count()
        
        if pending_appointments > 0:
            alerts.append({
                "type": "pending_appointments",
                "priority": "warning",
                "title": "Pending Appointments",
                "message": f"{pending_appointments} appointment request(s) awaiting your approval",
                "count": pending_appointments,
                "action_url": f"/mentor/{mentor_id}/appointments"
            })
    except Exception:
        pass
    
    # 3. Students with incomplete mandatory forms
    try:
        for student in assigned_students:
            missing_forms = []
            
            # Check psychometric form
            psychometric = db.query(PsychometricResponse).filter(
                PsychometricResponse.student_usn == student.student_usn
            ).first()
            if not psychometric:
                missing_forms.append("Psychometric")
            
            if missing_forms and len(missing_forms) > 0:
                alerts.append({
                    "type": "missing_forms",
                    "priority": "warning",
                    "title": "Missing Forms",
                    "message": f"{student.student_name or student.student_usn} hasn't completed: {', '.join(missing_forms)}",
                    "student_usn": student.student_usn,
                    "student_name": student.student_name,
                    "forms": missing_forms,
                    "action_url": f"/mentor/{mentor_id}/assigned_students"
                })
    except Exception:
        pass
    
    # 4. Students with no profile
    try:
        students_no_profile = [s for s in assigned_students if not s.student_name]
        if students_no_profile:
            alerts.append({
                "type": "no_profile",
                "priority": "urgent",
                "title": "Incomplete Profiles",
                "message": f"{len(students_no_profile)} student(s) haven't created their profile yet",
                "count": len(students_no_profile),
                "students": [s.student_usn for s in students_no_profile[:5]],
                "action_url": f"/mentor/{mentor_id}/assigned_students"
            })
    except Exception:
        pass
    
    # Calculate summary
    summary = {
        "total": len(alerts),
        "urgent": len([a for a in alerts if a.get("priority") == "urgent"]),
        "warning": len([a for a in alerts if a.get("priority") == "warning"]),
        "info": len([a for a in alerts if a.get("priority") == "info"])
    }
    
    return {"alerts": alerts[:10], "summary": summary}


@router.get("/dashboard/activity-feed")
def get_activity_feed(mentor_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """Get recent activity feed for the mentor dashboard."""
    activities = []
    
    # Get assigned students
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    student_usns = [s.student_usn for s in assigned_students]
    student_names = {s.student_usn: s.student_name or s.student_usn for s in assigned_students}
    
    if not student_usns:
        return {"activities": []}
    
    # 1. Recent meeting completions
    try:
        recent_meetings = db.query(Meetings).filter(
            Meetings.mentor_id == mentor_id,
            Meetings.status == "completed"
        ).order_by(desc(Meetings.meeting_date)).limit(5).all()
        
        for meeting in recent_meetings:
            if meeting.meeting_date:
                activities.append({
                    "type": "meeting_completed",
                    "icon": "calendar-check",
                    "title": "Meeting Completed",
                    "description": f"Meeting with {student_names.get(meeting.student_usn, meeting.student_usn)}",
                    "student_usn": meeting.student_usn,
                    "timestamp": meeting.meeting_date.isoformat() if meeting.meeting_date else None,
                    "time_ago": get_time_ago(meeting.meeting_date) if meeting.meeting_date else "Unknown"
                })
    except Exception:
        pass
    
    # 2. Recent psychometric form submissions
    try:
        recent_psychometric = db.query(PsychometricResponse).filter(
            PsychometricResponse.student_usn.in_(student_usns)
        ).order_by(desc(PsychometricResponse.submitted_at)).limit(5).all()
        
        for resp in recent_psychometric:
            if resp.submitted_at:
                activities.append({
                    "type": "form_submitted",
                    "icon": "clipboard-list",
                    "title": "Psychometric Form Submitted",
                    "description": f"{student_names.get(resp.student_usn, resp.student_usn)} completed psychometric form",
                    "student_usn": resp.student_usn,
                    "timestamp": resp.submitted_at.isoformat() if resp.submitted_at else None,
                    "time_ago": get_time_ago(resp.submitted_at) if resp.submitted_at else "Unknown"
                })
    except Exception:
        pass
    
    # 3. Recent activity submissions
    try:
        recent_submissions = db.query(ActivitySubmissions).filter(
            ActivitySubmissions.student_usn.in_(student_usns)
        ).order_by(desc(ActivitySubmissions.submitted_at)).limit(5).all()
        
        for sub in recent_submissions:
            if sub.submitted_at:
                activities.append({
                    "type": "activity_submitted",
                    "icon": "tasks",
                    "title": "Activity Submitted",
                    "description": f"{student_names.get(sub.student_usn, sub.student_usn)} submitted an activity",
                    "student_usn": sub.student_usn,
                    "timestamp": sub.submitted_at.isoformat() if sub.submitted_at else None,
                    "time_ago": get_time_ago(sub.submitted_at) if sub.submitted_at else "Unknown"
                })
    except Exception:
        pass
    
    # 4. Recent SWOT generations - SWOT model doesn't have timestamp, skip for now
    
    # Sort all activities by timestamp and limit
    activities_with_ts = [a for a in activities if a.get("timestamp")]
    activities_with_ts.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {"activities": activities_with_ts[:limit]}


@router.get("/dashboard/at-risk-students")
def get_at_risk_students(mentor_id: str, db: Session = Depends(get_db)):
    """Get students who need attention - low attendance, incomplete forms, inactive.
    Optimized with batch queries to avoid N+1 problem."""
    
    # Get assigned students
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    
    if not assigned_students:
        return {"at_risk_students": [], "total_count": 0}
    
    student_usns = [s.student_usn for s in assigned_students]
    
    # Batch query all related data at once (instead of per-student queries)
    psychometric_usns = set()
    swot_usns = set()
    mca_usns = set()
    attendance_data = {}
    
    try:
        psychometric_results = db.query(PsychometricResponse.student_usn).filter(
            PsychometricResponse.student_usn.in_(student_usns)
        ).all()
        psychometric_usns = {r[0] for r in psychometric_results}
    except Exception:
        pass
    
    try:
        swot_results = db.query(SWOT.student_usn).filter(
            SWOT.student_usn.in_(student_usns)
        ).all()
        swot_usns = {r[0] for r in swot_results}
    except Exception:
        pass
    
    try:
        mca_results = db.query(MentorshipAssessment.student_usn).filter(
            MentorshipAssessment.student_usn.in_(student_usns)
        ).all()
        mca_usns = {r[0] for r in mca_results}
    except Exception:
        pass
    
    try:
        attendance_records = db.query(
            Attendance.student_usn, 
            Attendance.status
        ).filter(Attendance.student_usn.in_(student_usns)).all()
        
        for usn, status in attendance_records:
            if usn not in attendance_data:
                attendance_data[usn] = {"total": 0, "present": 0}
            attendance_data[usn]["total"] += 1
            if status == "present":
                attendance_data[usn]["present"] += 1
    except Exception:
        pass
    
    # Process students using the batch-loaded data
    at_risk = []
    for student in assigned_students:
        issues = []
        usn = student.student_usn
        
        # Check for incomplete profile
        if not student.student_name:
            issues.append({
                "type": "no_profile",
                "severity": "high",
                "message": "No profile created"
            })
        
        # Check for missing psychometric form
        if usn not in psychometric_usns:
            issues.append({
                "type": "missing_psychometric",
                "severity": "medium",
                "message": "Psychometric form not filled"
            })
        
        # Check for missing SWOT
        if usn not in swot_usns:
            issues.append({
                "type": "missing_swot",
                "severity": "medium",
                "message": "SWOT not generated"
            })
        
        # Check attendance
        if usn in attendance_data:
            data = attendance_data[usn]
            if data["total"] > 0:
                attendance_pct = (data["present"] / data["total"] * 100)
                if attendance_pct < 75:
                    issues.append({
                        "type": "low_attendance",
                        "severity": "high",
                        "message": f"Low attendance: {attendance_pct:.0f}%",
                        "percentage": attendance_pct
                    })
        
        # Check for MCA form
        if usn not in mca_usns:
            issues.append({
                "type": "missing_mca",
                "severity": "low",
                "message": "MCA form not filled"
            })
        
        if issues:
            high_count = len([i for i in issues if i["severity"] == "high"])
            medium_count = len([i for i in issues if i["severity"] == "medium"])
            
            if high_count >= 2:
                risk_level = "critical"
            elif high_count >= 1:
                risk_level = "high"
            elif medium_count >= 2:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            at_risk.append({
                "student_usn": student.student_usn,
                "student_name": student.student_name or "No Name",
                "risk_level": risk_level,
                "issues": issues,
                "issue_count": len(issues)
            })
    
    # Sort by risk level
    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    at_risk.sort(key=lambda x: risk_order.get(x["risk_level"], 4))
    
    return {
        "at_risk_students": at_risk[:10],
        "total_count": len(at_risk)
    }


@router.get("/dashboard/attendance-trend")
def get_attendance_trend(mentor_id: str, weeks: int = 6, db: Session = Depends(get_db)):
    """Get weekly attendance trend data for charts."""
    # Get assigned students
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    student_usns = [s.student_usn for s in assigned_students]
    
    if not student_usns:
        return {"trend": [], "labels": []}
    
    today = datetime.now().date()
    trend_data = []
    labels = []
    
    for i in range(weeks - 1, -1, -1):
        week_end = today - timedelta(days=i * 7)
        week_start = week_end - timedelta(days=6)
        
        labels.append(week_start.strftime("%b %d"))
        
        try:
            # Count attendance for this week
            week_start_dt = datetime.combine(week_start, datetime.min.time())
            week_end_dt = datetime.combine(week_end, datetime.max.time())
            week_records = db.query(Attendance).filter(
                Attendance.student_usn.in_(student_usns),
                Attendance.marked_at >= week_start_dt,
                Attendance.marked_at <= week_end_dt
            ).all()
            
            present_count = len([r for r in week_records if r.status == "present"])
            total_count = len(week_records)
            
            trend_data.append({
                "week": week_start.strftime("%Y-%m-%d"),
                "present": present_count,
                "total": total_count,
                "percentage": round((present_count / total_count * 100) if total_count > 0 else 0, 1)
            })
        except Exception:
            trend_data.append({
                "week": week_start.strftime("%Y-%m-%d"),
                "present": 0,
                "total": 0,
                "percentage": 0
            })
    
    return {
        "trend": trend_data,
        "labels": labels
    }


@router.get("/dashboard/calendar-events")
def get_calendar_events(mentor_id: str, db: Session = Depends(get_db)):
    """Get meetings for calendar widget - current week and next week."""
    today = datetime.now().date()
    # Start from Sunday (weekday() returns 0 for Monday, so add 1 and mod 7 to get days since Sunday)
    days_since_sunday = (today.weekday() + 1) % 7
    start_of_week = today - timedelta(days=days_since_sunday)
    end_of_next_week = start_of_week + timedelta(days=13)
    
    # Get assigned students for names
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    student_names = {s.student_usn: s.student_name or s.student_usn for s in assigned_students}
    
    events = []
    
    try:
        start_dt = datetime.combine(start_of_week, datetime.min.time())
        end_dt = datetime.combine(end_of_next_week, datetime.max.time())
        
        print(f"Calendar events query: mentor={mentor_id}, start={start_dt}, end={end_dt}")
        
        meetings = db.query(Meetings).filter(
            Meetings.mentor_id == mentor_id,
            Meetings.meeting_date >= start_dt,
            Meetings.meeting_date <= end_dt
        ).order_by(Meetings.meeting_date).all()
        
        print(f"Found {len(meetings)} meetings for calendar")
        
        for meeting in meetings:
            if meeting.meeting_date:
                events.append({
                    "id": meeting.id if hasattr(meeting, 'id') else None,
                    "title": f"Meeting: {student_names.get(meeting.student_usn, meeting.student_usn)}",
                    "student_usn": meeting.student_usn,
                    "student_name": student_names.get(meeting.student_usn, meeting.student_usn),
                    "date": meeting.meeting_date.date().isoformat(),
                    "time": meeting.meeting_date.strftime("%I:%M %p"),
                    "datetime": meeting.meeting_date.isoformat(),
                    "status": meeting.status or "scheduled",
                    "is_today": meeting.meeting_date.date() == today
                })
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
    
    return {
        "events": events,
        "week_start": start_of_week.isoformat(),
        "week_end": end_of_next_week.isoformat()
    }


@router.get("/dashboard/form-completion-stats")
def get_form_completion_stats(mentor_id: str, db: Session = Depends(get_db)):
    """Get form completion statistics for pie/donut chart.
    Optimized with batch queries to avoid N+1 problem."""
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    total_students = len(assigned_students)
    
    if total_students == 0:
        return {
            "total_students": 0,
            "forms": {}
        }
    
    student_usns = [s.student_usn for s in assigned_students]
    
    # Count profiles with names
    profile_count = len([s for s in assigned_students if s.student_name])
    
    # Batch queries - get counts directly from database
    psychometric_count = 0
    swot_count = 0
    mca_count = 0
    pf16_count = 0
    ibp_count = 0
    
    try:
        psychometric_count = db.query(func.count(func.distinct(PsychometricResponse.student_usn))).filter(
            PsychometricResponse.student_usn.in_(student_usns)
        ).scalar() or 0
    except Exception:
        pass
    
    try:
        swot_count = db.query(func.count(func.distinct(SWOT.student_usn))).filter(
            SWOT.student_usn.in_(student_usns)
        ).scalar() or 0
    except Exception:
        pass
    
    try:
        mca_count = db.query(func.count(func.distinct(MentorshipAssessment.student_usn))).filter(
            MentorshipAssessment.student_usn.in_(student_usns)
        ).scalar() or 0
    except Exception:
        pass
    
    try:
        pf16_count = db.query(func.count(func.distinct(PF16Response.student_usn))).filter(
            PF16Response.student_usn.in_(student_usns)
        ).scalar() or 0
    except Exception:
        pass
    
    try:
        ibp_count = db.query(func.count(func.distinct(IBPResponse.student_usn))).filter(
            IBPResponse.student_usn.in_(student_usns)
        ).scalar() or 0
    except Exception:
        pass
    
    return {
        "total_students": total_students,
        "forms": {
            "Profile": {"completed": profile_count, "pending": total_students - profile_count},
            "Psychometric": {"completed": psychometric_count, "pending": total_students - psychometric_count},
            "SWOT": {"completed": swot_count, "pending": total_students - swot_count},
            "MCA": {"completed": mca_count, "pending": total_students - mca_count},
            "16PF": {"completed": pf16_count, "pending": total_students - pf16_count},
            "IBP": {"completed": ibp_count, "pending": total_students - ibp_count}
        }
    }


def get_time_ago(dt):
    """Helper function to get human-readable time ago string."""
    if not dt:
        return "Unknown"
    
    now = datetime.now()
    if dt.tzinfo:
        now = datetime.now(dt.tzinfo)
    
    diff = now - dt
    
    if diff.days > 30:
        return f"{diff.days // 30} month(s) ago"
    elif diff.days > 0:
        return f"{diff.days} day(s) ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hour(s) ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minute(s) ago"
    else:
        return "Just now"
