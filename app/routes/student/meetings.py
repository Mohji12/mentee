from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.db.models.meetings import Meetings
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from datetime import timedelta, datetime
from app.schemas.meetings import MeetingApptRequest
from app.services.email_services import send_email
import uuid

router = APIRouter()

@router.get("/meetings")
def get_student_meetings(student_usn: str, db: Session = Depends(get_db)):
    meetings = db.query(Meetings).filter(Meetings.student_usn == student_usn).all()
    meeting_list = [
        {
            "meeting_id": meeting.id,
            "mentor_id": meeting.mentor_id,
            "meeting_date": meeting.meeting_date,
            "venue": meeting.venue,
            "progress_notes": meeting.progress_notes,
            "status": meeting.status,
            "meeting_mode": getattr(meeting, "meeting_mode", None) or "offline",
            "google_meet_link": getattr(meeting, "google_meet_link", None),
        }
        for meeting in meetings
    ]

    return {"student_usn": student_usn, "meetings": meeting_list}

@router.post("/request_meeting")
def request_meeting(student_usn: str, meeting: MeetingApptRequest, db: Session = Depends(get_db)):
    """
    Schedule a meeting requested by a student with their assigned mentor.
    """
    meeting_mode = (meeting.meeting_mode or "offline").lower()
    if meeting_mode not in ("online", "offline"):
        raise HTTPException(status_code=400, detail="meeting_mode must be 'online' or 'offline'.")

    if meeting_mode == "offline":
        if not meeting.venue or not str(meeting.venue).strip():
            raise HTTPException(status_code=400, detail="Venue (location) is required for offline meetings.")
        venue = meeting.venue.strip()
    else:
        venue = "Online"

    try:
        # Frontend sends IST time directly, store it as-is (no timezone conversion needed)
        meeting_datetime = datetime.strptime(meeting.meeting_date, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'yyyy-mm-ddTHH:MM'.")

    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"No student found with USN {student_usn}")

    mentor_id = student.assigned_mentor
    if not mentor_id:
        raise HTTPException(status_code=400, detail="No assigned mentor for this student")

    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    meeting_entry = Meetings(
        id=str(uuid.uuid4()),
        mentor_id=mentor_id,
        student_usn=student_usn,
        meeting_date=meeting_datetime,
        venue=venue,
        meeting_mode=meeting_mode,
        progress_notes=None,
        status="pending",
    )
    db.add(meeting_entry)
    db.commit()

    mode_label = "Online" if meeting_mode == "online" else "Offline"
    location_line = f"📍 <strong>Location:</strong> {venue}<br/>" if meeting_mode == "offline" else ""

    subject = "New Meeting Request from a Student"
    body = f"""
<p>Dear <strong>{mentor.mentor_name}</strong>,</p>

<p>Student <strong>{student.student_name}</strong> has requested a meeting with you. Below are the details of the request:</p>

<hr style="border: 0; height: 1px; background: #ddd;">

<p><strong>Meeting Details:</strong></p>

<p>
    📅 <strong>Date & Time:</strong> {meeting_datetime.strftime('%Y-%m-%d %H:%M')}<br/>
    📌 <strong>Mode:</strong> {mode_label}<br/>
    {location_line}
</p>

<p>Please log in to your mentor portal to approve or reject this request.</p>

<hr style="border: 0; height: 1px; background: #ddd;">
"""

    send_email(mentor.mentor_email, subject, body)

    return {"message": "Meeting request sent to mentor", "meeting_id": meeting_entry.id}

@router.get("/scheduled_pending_meetings")
def get_scheduled_pending_meetings(student_usn: str, db: Session = Depends(get_db)):
    valid_statuses = ["pending", "approved", "rejected"]

    meetings = (
        db.query(Meetings)
        .filter(Meetings.student_usn == student_usn, Meetings.status.in_(valid_statuses))
        .order_by(desc(Meetings.meeting_date))
        .all()
    )

    meeting_list = [
        {
            "meeting_id": meeting.id,
            "mentor_id": meeting.mentor_id,
            "meeting_date": meeting.meeting_date,
            "venue": meeting.venue,
            "progress_notes": meeting.progress_notes,
            "status": meeting.status,
            "meeting_mode": getattr(meeting, "meeting_mode", None) or "offline",
            "google_meet_link": getattr(meeting, "google_meet_link", None),
        }
        for meeting in meetings
    ]

    return {"student_usn": student_usn, "meetings": meeting_list}
