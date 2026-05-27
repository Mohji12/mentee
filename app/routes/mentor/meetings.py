from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.students import Student
from app.db.models.meetings import Meetings
from app.db.models.mentors import Mentor
from app.db.database import get_db
from app.schemas.meetings import MeetingScheduleRequest, ProgressNotesRequest, MeetingResponseRequest, MeetingResponse
from app.services.email_services import send_email
from app.services.google_meet_service import GoogleMeetService
from datetime import datetime, timedelta
import uuid
from typing import List
from collections import defaultdict

router = APIRouter()

@router.post("/schedule_meeting")
def schedule_meeting(mentor_id: str, meeting: MeetingScheduleRequest, db: Session = Depends(get_db)):
    """
    Schedule a meeting between a mentor and one or more students.
    Supports online (Google Meet) or offline (venue) mode.
    """
    try:
        # Frontend sends IST time directly, store it as-is (no timezone conversion needed)
        meeting_datetime = datetime.strptime(meeting.meeting_date, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'yyyy-mm-ddThh:mm'.")

    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    if not isinstance(meeting.student_usns, list) or len(meeting.student_usns) == 0:
        raise HTTPException(status_code=400, detail="At least one student USN must be provided.")

    meeting_mode = (meeting.meeting_mode or "offline").lower()
    if meeting_mode not in ("online", "offline"):
        raise HTTPException(status_code=400, detail="meeting_mode must be 'online' or 'offline'.")

    if meeting_mode == "offline":
        if not meeting.venue or not str(meeting.venue).strip():
            raise HTTPException(status_code=400, detail="Venue is required for offline meetings.")
        venue = meeting.venue.strip()
        google_meet_link = None
    else:
        venue = "Online"
        if meeting.google_meet_link and str(meeting.google_meet_link).strip():
            google_meet_link = meeting.google_meet_link.strip()
        else:
            meet_details = GoogleMeetService.create_working_google_meet_link()
            google_meet_link = meet_details.get("meeting_link")

    meeting_entries = []
    email_errors = []

    for student_usn in meeting.student_usns:
        student = db.query(Student).filter(Student.student_usn == student_usn).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"No student found with USN {student_usn}")

        meeting_entry = Meetings(
            id=str(uuid.uuid4()),
            mentor_id=mentor_id,
            student_usn=student_usn,
            meeting_date=meeting_datetime,
            venue=venue,
            meeting_mode=meeting_mode,
            google_meet_link=google_meet_link,
            progress_notes=None,
            status="approved",
        )
        meeting_entries.append(meeting_entry)

        # Email each student
        try:
            subject = "Your Meeting with Mentor has been Scheduled"
            mode_line = "Mode: Online" if meeting_mode == "online" else f"Venue: {venue}"
            link_line = f"\n🔗 Join: {google_meet_link}\n" if meeting_mode == "online" and google_meet_link else ""
            body = (
                f"Dear {student.student_name},\n\n"
                f"Your meeting with {mentor.mentor_name} is scheduled:\n"
                f"📅 Date & Time: {meeting_datetime.strftime('%Y-%m-%d %H:%M')}\n"
                f"📌 {mode_line}{link_line}\n\n"
                f"Best regards,\nYour Mentorship Program"
            )
            send_email(student.student_email, subject, body)
        except Exception as e:
            email_errors.append(f"Failed to send email to {student.student_email}: {str(e)}")

    db.add_all(meeting_entries)
    db.commit()

    # Send confirmation email to mentor (both sides)
    try:
        subject_mentor = "Meetings Scheduled – Confirmation"
        mode_line = "Mode: Online" if meeting_mode == "online" else f"Venue: {venue}"
        link_html = ""
        if meeting_mode == "online" and google_meet_link:
            link_html = f'<p><strong>Join meeting:</strong> <a href="{google_meet_link}" style="color: #007bff;">{google_meet_link}</a></p>'
        body_mentor = f"""
<p>Dear <strong>{mentor.mentor_name}</strong>,</p>
<p>You have scheduled meetings with the following students:</p>
<p><strong>Students:</strong> {", ".join(meeting.student_usns)}</p>
<p>📅 <strong>Date & Time:</strong> {meeting_datetime.strftime('%Y-%m-%d %H:%M')}<br/>
📌 <strong>{mode_line}</strong></p>
{link_html}
<p>Best regards,<br/>Your Mentorship Program</p>
"""
        send_email(mentor.mentor_email, subject_mentor, body_mentor)
    except Exception as e:
        email_errors.append(f"Failed to send confirmation to mentor: {str(e)}")

    response_data = {
        "message": "Meetings scheduled successfully",
        "data": {
            "mentor_id": mentor_id,
            "meeting_date": meeting_datetime.strftime('%Y-%m-%d %H:%M'),
            "venue": venue,
            "meeting_mode": meeting_mode,
            "google_meet_link": google_meet_link,
            "students": meeting.student_usns,
        },
    }
    if email_errors:
        response_data["email_errors"] = email_errors

    return response_data


@router.put("/{meeting_id}/log_meeting")
def log_meeting(mentor_id: str, meeting_id: str, progress: ProgressNotesRequest, db: Session = Depends(get_db)):
    # Fetch the meeting from the database
    meeting = db.query(Meetings).filter(Meetings.id == meeting_id, Meetings.mentor_id == mentor_id).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail=f"No meeting found with ID {meeting_id} for mentor {mentor_id}")

    # Update the progress notes after the meeting
    meeting.progress_notes = progress.progress_notes

    # Commit the changes to the database
    db.commit()

    # Send an email to the student about the meeting update
    student = db.query(Student).filter(Student.student_usn == meeting.student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"No student found with USN {meeting.student_usn}")
    
    subject = "Meeting Progress Updated"
    body = f"Dear {student.student_name},\n\nThe progress notes for your meeting with mentor {mentor_id} have been updated. Please review the details in the system.\n\nBest regards,\nYour Mentor"
    send_email(student.student_email, subject, body)

    return {"message": "Meeting progress logged and email sent"}


@router.get("/meetings")
def get_mentor_meetings(mentor_id: str, db: Session = Depends(get_db)):
    meetings = db.query(Meetings).filter(Meetings.mentor_id == mentor_id).all()
    meeting_list = []
    for meeting in meetings:
        student = db.query(Student).filter(Student.student_usn == meeting.student_usn).first()
        meeting_list.append({
            "meeting_id": meeting.id,
            "student_usn": meeting.student_usn,
            "student_name": student.student_name if student else None,
            "meeting_date": meeting.meeting_date,
            "venue": meeting.venue,
            "meeting_mode": getattr(meeting, "meeting_mode", None) or "offline",
            "google_meet_link": getattr(meeting, "google_meet_link", None),
            "status": meeting.status,
            "progress_notes": meeting.progress_notes,
        })
    return {"mentor_id": mentor_id, "meetings": meeting_list}

@router.get("/pending_meetings", response_model=List[MeetingResponse])
def get_pending_meetings(mentor_id: str, db: Session = Depends(get_db)):    
    pending_meetings = (
        db.query(Meetings)
        .filter(
            Meetings.mentor_id == mentor_id,
            Meetings.status == "pending"  # Filter meetings with status "pending"
            )
            .order_by(Meetings.meeting_date.asc())
            .all()
        )

    meetings_dict = defaultdict(lambda: {
        "id": None,
        "meeting_date": None,
        "progress_notes": None,
        "status": None,
        "venue": None,
        "meeting_mode": None,
        "google_meet_link": None,
        "duration": None,
        "mentor_id": None,
        "student_usn": [],
        "student_names": [],
        "created_at": None,
        "agenda": None,
    })

    for meeting in pending_meetings:
        meeting_id = meeting.id
        if meetings_dict[meeting_id]["id"] is None:
            meetings_dict[meeting_id].update({
                "id": meeting.id,
                "meeting_date": meeting.meeting_date,
                "progress_notes": meeting.progress_notes,
                "status": meeting.status,
                "venue": meeting.venue,
                "meeting_mode": getattr(meeting, "meeting_mode", None) or "offline",
                "google_meet_link": getattr(meeting, "google_meet_link", None),
                "duration": meeting.duration,
                "mentor_id": meeting.mentor_id,
                "created_at": meeting.created_at,
                "agenda": meeting.agenda,
            })
        meetings_dict[meeting_id]["student_usn"].append(meeting.student_usn)
        student = db.query(Student).filter(Student.student_usn == meeting.student_usn).first()
        meetings_dict[meeting_id]["student_names"].append(student.student_name if student else None)

    return list(meetings_dict.values())

@router.put("/{meeting_id}/respond_meeting")
def respond_meeting(mentor_id: str, meeting_id: str, response: MeetingResponseRequest, db: Session = Depends(get_db)):
    """
    Mentor can approve or reject a scheduled meeting. For approved online meetings, generates Google Meet link.
    """
    meeting = db.query(Meetings).filter(Meetings.id == meeting_id, Meetings.mentor_id == mentor_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail=f"No meeting found with ID {meeting_id} for mentor {mentor_id}")
    
    status = response.status.lower()
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'approved' or 'rejected'.")

    meeting_mode = getattr(meeting, "meeting_mode", None) or "offline"
    if status == "approved" and meeting_mode == "online":
        meet_details = GoogleMeetService.create_working_google_meet_link()
        meeting.google_meet_link = meet_details.get("meeting_link")

    meeting.status = status
    db.commit()
    
    student = db.query(Student).filter(Student.student_usn == meeting.student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"No student found with USN {meeting.student_usn}")
    
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    date_str = meeting.meeting_date.strftime("%Y-%m-%d %H:%M") if meeting.meeting_date else ""
    venue_or_location = (meeting.venue or "Online").strip()
    meet_link = getattr(meeting, "google_meet_link", None)

    if status == "approved":
        link_html = ""
        if meet_link:
            link_html = f'<p><strong>Join meeting:</strong> <a href="{meet_link}" style="color: #007bff;">{meet_link}</a></p>'
        details_html = f"""
<p><strong>Meeting Details:</strong></p>
<p>📅 Date & Time: {date_str}<br/>📌 Mode: {"Online" if meeting_mode == "online" else "Offline"}<br/>📍 Location: {venue_or_location}</p>
{link_html}
"""
        subject_student = "Meeting Request Approved"
        body_student = f"""
<p>Dear <strong>{student.student_name}</strong>,</p>
<p>Your meeting request with <strong>{mentor.mentor_name}</strong> has been <strong>approved</strong>.</p>
<hr style="border: 0; height: 1px; background: #ddd;">
{details_html}
<p>Best regards,<br/>Your Mentorship Program</p>
"""
        send_email(student.student_email, subject_student, body_student)

        subject_mentor = "Meeting Approved – Confirmation"
        body_mentor = f"""
<p>Dear <strong>{mentor.mentor_name}</strong>,</p>
<p>You have approved the meeting request from <strong>{student.student_name}</strong>.</p>
<hr style="border: 0; height: 1px; background: #ddd;">
{details_html}
<p>Best regards,<br/>Your Mentorship Program</p>
"""
        send_email(mentor.mentor_email, subject_mentor, body_mentor)
    else:
        subject = "Meeting Request Update"
        body = (
            f"Dear {student.student_name},\n\n"
            f"Your meeting request with mentor {mentor.mentor_name} has been rejected.\n\n"
            f"Best regards,\nYour Mentorship Program"
        )
        send_email(student.student_email, subject, body)
    
    return {"message": f"Meeting {status} successfully"}
