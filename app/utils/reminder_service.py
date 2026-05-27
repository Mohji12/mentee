"""
Reminder / notification service: compute pending platform tasks per mentee and send
email reminders to mentees and digest emails to mentors.
"""
import logging
import os
from collections import defaultdict
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.activities import Activities
from app.db.models.MCA_assignments import MentorshipAssessment
from app.db.models.counseling import CounselingSession, CounselingReminder
from app.services.email_services import send_email
from datetime import datetime, timedelta
from sqlalchemy import and_

logger = logging.getLogger(__name__)

# Default app URL for login link in emails (override via env)
DEFAULT_APP_URL = os.getenv("MENTEE_TRACKER_APP_URL", "https://jgi.menteetracker.com")


def get_pending_items_for_student(db: Session, student_usn: str) -> List[str]:
    """
    Return list of human-readable pending task labels for this student.
    Uses same completion logic as leader/department/HOD stats.
    """
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        return []
    if not student.assigned_mentor:
        return ["Get assigned a mentor"]

    pending: List[str] = []

    # Profile: name, email, phone, program, semester (linkedin optional in stats)
    if not all([
        student.student_name,
        student.student_email,
        student.student_phoneno,
        student.student_program,
        student.semester is not None,
    ]):
        pending.append("Complete your profile")

    if db.query(PsychometricResponse).filter(PsychometricResponse.student_usn == student_usn.strip()).first() is None:
        pending.append("Fill psychometric form")

    if db.query(Report).filter(Report.student_usn == student_usn.strip()).first() is None:
        pending.append("Generate SWOT report")

    if db.query(Activities).filter(Activities.student_usn == student_usn.strip()).first() is None:
        pending.append("Log at least one activity")

    if db.query(MentorshipAssessment).filter(MentorshipAssessment.student_usn == student_usn.strip()).first() is None:
        pending.append("Fill MCA form")

    return pending


def get_students_with_pending_items(db: Session) -> List[dict]:
    """
    Return list of students who have an assigned mentor and at least one pending item.
    Each item: student_usn, student_email, student_name, mentor_id, mentor_email, mentor_name, pending_items.
    """
    students_with_mentor = (
        db.query(Student, Mentor.mentor_id, Mentor.mentor_email, Mentor.mentor_name)
        .join(Mentor, Student.assigned_mentor == Mentor.mentor_id)
        .filter(Student.assigned_mentor.isnot(None))
        .all()
    )
    result = []
    for row in students_with_mentor:
        student, mentor_id, mentor_email, mentor_name = row
        pending = get_pending_items_for_student(db, student.student_usn)
        if not pending:
            continue
        if not student.student_email or "@" not in str(student.student_email):
            continue
        result.append({
            "student_usn": student.student_usn,
            "student_email": student.student_email,
            "student_name": student.student_name or student.student_usn,
            "mentor_id": mentor_id,
            "mentor_email": mentor_email or "",
            "mentor_name": mentor_name or mentor_id,
            "pending_items": pending,
        })
    return result


def send_mentee_reminder_email(
    to_email: str,
    student_name: str,
    pending_items: List[str],
    app_url: str = DEFAULT_APP_URL,
) -> bool:
    """Send one reminder email to a mentee listing their pending items."""
    subject = "Mentee Tracker – Pending items to complete"
    name = student_name or "Mentee"
    items_html = "".join(f"<li>{item}</li>" for item in pending_items)
    body = f"""
    <p>Hello {name},</p>
    <p>You have the following pending items on the Mentee Tracker platform:</p>
    <ul>{items_html}</ul>
    <p>Please log in and complete them at your earliest convenience.</p>
    <p><a href="{app_url}" style="color: #2563eb;">Log in to Mentee Tracker</a></p>
    <p>Best regards,<br>Mentee Tracker Team</p>
    """
    try:
        return send_email(to_email, subject, body)
    except Exception as e:
        logger.exception("Failed to send mentee reminder email to %s: %s", to_email, e)
        return False


def send_mentor_digest_email(
    to_email: str,
    mentor_name: str,
    mentees_list: List[Tuple[str, str, List[str]]],
    app_url: str = DEFAULT_APP_URL,
) -> bool:
    """
    Send one digest email to a mentor. mentees_list: list of (mentee_name, mentee_usn, pending_items).
    """
    if not mentees_list:
        return True
    subject = "Mentee Tracker – Your mentees' pending items"
    name = mentor_name or "Mentor"
    blocks = []
    for mentee_name, mentee_usn, pending_items in mentees_list:
        items_str = ", ".join(pending_items)
        blocks.append(f"<p><strong>{mentee_name}</strong> ({mentee_usn}): {items_str}</p>")
    blocks_html = "\n".join(blocks)
    body = f"""
    <p>Hello {name},</p>
    <p>The following mentees have pending items on the platform:</p>
    {blocks_html}
    <p><a href="{app_url}" style="color: #2563eb;">Log in to Mentee Tracker</a></p>
    <p>Best regards,<br>Mentee Tracker Team</p>
    """
    try:
        return send_email(to_email, subject, body)
    except Exception as e:
        logger.exception("Failed to send mentor digest email to %s: %s", to_email, e)
        return False


def run_reminder_job(app_url: str = DEFAULT_APP_URL) -> None:
    """
    Load all students with pending items, send mentee reminder emails and mentor digest emails.
    Uses a single DB session; swallows per-email errors so one failure does not stop the rest.
    """
    from app.db.database import get_db

    db = next(get_db())
    try:
        rows = get_students_with_pending_items(db)
        # Send one email per mentee
        for r in rows:
            if r["student_email"] and "@" in r["student_email"]:
                try:
                    send_mentee_reminder_email(
                        r["student_email"],
                        r["student_name"],
                        r["pending_items"],
                        app_url=app_url,
                    )
                except Exception as e:
                    logger.exception("Reminder email failed for %s: %s", r["student_usn"], e)

        # Group by mentor and send one digest per mentor
        by_mentor = defaultdict(list)
        for r in rows:
            if r["mentor_email"] and "@" in r["mentor_email"]:
                by_mentor[(r["mentor_id"], r["mentor_email"], r["mentor_name"])].append(
                    (r["student_name"], r["student_usn"], r["pending_items"]))
        for (mentor_id, mentor_email, mentor_name), mentees_list in by_mentor.items():
            try:
                send_mentor_digest_email(mentor_email, mentor_name, mentees_list, app_url=app_url)
            except Exception as e:
                logger.exception("Mentor digest email failed for %s: %s", mentor_id, e)

        logger.info("Reminder job completed: %d mentees with pending items processed", len(rows))
    except Exception as e:
        logger.exception("Reminder job failed: %s", e)
    finally:
        db.close()


# ============ COUNSELING SESSION REMINDERS ============

def create_upcoming_session_reminders(db: Session) -> int:
    """
    Create reminders for counseling sessions happening in the next 24 hours.
    Returns the count of reminders created.
    """
    now = datetime.utcnow()
    tomorrow = now + timedelta(hours=24)
    
    upcoming_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.status == "scheduled",
            CounselingSession.session_date >= now,
            CounselingSession.session_date <= tomorrow
        )
    ).all()
    
    created_count = 0
    for session in upcoming_sessions:
        existing = db.query(CounselingReminder).filter(
            and_(
                CounselingReminder.session_id == session.counseling_id,
                CounselingReminder.reminder_type == "upcoming_session",
                CounselingReminder.scheduled_for >= now - timedelta(hours=24)
            )
        ).first()
        
        if existing:
            continue
        
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
        
        session_time = session.session_date.strftime("%B %d, %Y at %I:%M %p")
        
        mentor_reminder = CounselingReminder(
            session_id=session.counseling_id,
            recipient_id=session.mentor_id,
            recipient_type="mentor",
            reminder_type="upcoming_session",
            title=f"Upcoming Session with {student.student_name if student else session.student_usn}",
            message=f"You have a counseling session scheduled for {session_time} at {session.venue}.",
            scheduled_for=now,
            status="sent"
        )
        db.add(mentor_reminder)
        
        student_reminder = CounselingReminder(
            session_id=session.counseling_id,
            recipient_id=session.student_usn,
            recipient_type="student",
            reminder_type="upcoming_session",
            title=f"Upcoming Session with {mentor.mentor_name if mentor else 'your mentor'}",
            message=f"You have a counseling session scheduled for {session_time} at {session.venue}.",
            scheduled_for=now,
            status="sent"
        )
        db.add(student_reminder)
        created_count += 2
    
    db.commit()
    return created_count


def create_followup_due_reminders(db: Session) -> int:
    """
    Create reminders for follow-ups that are due within the next 3 days.
    Returns the count of reminders created.
    """
    today = datetime.utcnow().date()
    three_days_ahead = today + timedelta(days=3)
    
    followup_due_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.outcome_status == "needs_followup",
            CounselingSession.followup_scheduled == False,
            CounselingSession.followup_date.isnot(None),
            CounselingSession.followup_date >= today,
            CounselingSession.followup_date <= three_days_ahead
        )
    ).all()
    
    created_count = 0
    now = datetime.utcnow()
    
    for session in followup_due_sessions:
        existing = db.query(CounselingReminder).filter(
            and_(
                CounselingReminder.session_id == session.counseling_id,
                CounselingReminder.reminder_type == "followup_due",
                CounselingReminder.scheduled_for >= now - timedelta(days=1)
            )
        ).first()
        
        if existing:
            continue
        
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        followup_date_str = session.followup_date.strftime("%B %d, %Y")
        days_until = (session.followup_date - today).days
        
        reminder = CounselingReminder(
            session_id=session.counseling_id,
            recipient_id=session.mentor_id,
            recipient_type="mentor",
            reminder_type="followup_due",
            title=f"Follow-up Due: {student.student_name if student else session.student_usn}",
            message=f"A follow-up session for {student.student_name if student else session.student_usn} is due on {followup_date_str} ({days_until} day{'s' if days_until != 1 else ''} away). Please schedule the follow-up session.",
            scheduled_for=now,
            status="sent"
        )
        db.add(reminder)
        created_count += 1
    
    db.commit()
    return created_count


def create_overdue_followup_reminders(db: Session) -> int:
    """
    Create reminders for overdue follow-ups.
    Returns the count of reminders created.
    """
    today = datetime.utcnow().date()
    
    overdue_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.outcome_status == "needs_followup",
            CounselingSession.followup_scheduled == False,
            CounselingSession.followup_date.isnot(None),
            CounselingSession.followup_date < today
        )
    ).all()
    
    created_count = 0
    now = datetime.utcnow()
    
    for session in overdue_sessions:
        existing = db.query(CounselingReminder).filter(
            and_(
                CounselingReminder.session_id == session.counseling_id,
                CounselingReminder.reminder_type == "overdue_followup",
                CounselingReminder.scheduled_for >= now - timedelta(days=1)
            )
        ).first()
        
        if existing:
            continue
        
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        days_overdue = (today - session.followup_date).days
        
        reminder = CounselingReminder(
            session_id=session.counseling_id,
            recipient_id=session.mentor_id,
            recipient_type="mentor",
            reminder_type="overdue_followup",
            title=f"⚠️ Overdue Follow-up: {student.student_name if student else session.student_usn}",
            message=f"A follow-up session for {student.student_name if student else session.student_usn} is {days_overdue} day{'s' if days_overdue != 1 else ''} overdue. Please schedule the follow-up session urgently.",
            scheduled_for=now,
            status="sent"
        )
        db.add(reminder)
        created_count += 1
    
    db.commit()
    return created_count


def run_counseling_reminder_job() -> None:
    """
    Generate and process all counseling-related reminders.
    """
    from app.db.database import get_db
    
    db = next(get_db())
    try:
        upcoming_count = create_upcoming_session_reminders(db)
        followup_count = create_followup_due_reminders(db)
        overdue_count = create_overdue_followup_reminders(db)
        
        logger.info(
            "Counseling reminder job completed: %d upcoming, %d followup due, %d overdue reminders created",
            upcoming_count, followup_count, overdue_count
        )
    except Exception as e:
        logger.exception("Counseling reminder job failed: %s", e)
    finally:
        db.close()
