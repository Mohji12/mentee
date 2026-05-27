from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.students import Student
from app.db.models.meetings import Meetings
from app.db.models.mentors import Mentor
from app.db.database import get_db
from app.schemas.meetings import MeetingScheduleRequest, ProgressNotesRequest, MeetingResponseRequest, MeetingResponse
from app.services.email_services import send_email
from datetime import datetime, timedelta
import uuid
from typing import List
from collections import defaultdict

router = APIRouter()

@router.post("/schedule_meeting")
def schedule_meeting(mentor_id: str, meeting: MeetingScheduleRequest, db: Session = Depends(get_db)):
    """
    Schedule a meeting between a mentor and one or more students.
    """

    try:
        # Parse input datetime exactly as entered
        meeting_datetime = datetime.strptime(meeting.meeting_date, "%Y-%m-%dT%H:%M")

        # ✅ Add 5 hours 30 minutes before storing
        meeting_datetime = meeting_datetime + timedelta(hours=5, minutes=30)
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'yyyy-mm-ddThh:mm'.")

    # Check if mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    # Ensure student_usns is a list and not empty
    if not isinstance(meeting.student_usns, list) or len(meeting.student_usns) == 0:
        raise HTTPException(status_code=400, detail="At least one student USN must be provided.")

    meeting_entries = []
    email_errors = []

    for student_usn in meeting.student_usns:
        student = db.query(Student).filter(Student.student_usn == student_usn).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"No student found with USN {student_usn}")

        # Create a unique meeting ID for each student
        meeting_entry = Meetings(
            id=str(uuid.uuid4()),
            mentor_id=mentor_id,
            student_usn=student_usn,
            meeting_date=meeting_datetime,  # ✅ Store the adjusted time
            venue=meeting.venue,
            progress_notes=None,
        )
        meeting_entries.append(meeting_entry)

        # Send email notification
        try:
            subject = "Your Meeting with Mentor has been Scheduled"
            body = (
                f"Dear {student.student_name},\n\n"
                f"Your meeting with {mentor.mentor_name} is scheduled:\n"
                f"📅 Date & Time: {meeting_datetime.strftime('%Y-%m-%d %H:%M')}\n"
                f"📍 Venue: {meeting.venue}\n\n"
                f"Best regards,\nYour Mentorship Program"
            )
            send_email(student.student_email, subject, body)
        except Exception as e:
            email_errors.append(f"Failed to send email to {student.student_email}: {str(e)}")

    # Bulk insert all meetings
    db.add_all(meeting_entries)
    db.commit()

    # ✅ Response (Display stored time exactly)
    response_data = {
        "message": "Meetings scheduled successfully",
        "data": {
            "mentor_id": mentor_id,
            "meeting_date": meeting_datetime.strftime('%Y-%m-%d %H:%M'),  # Show stored time
            "venue": meeting.venue,
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
    # Fetch meetings for the mentor
    meetings = db.query(Meetings).filter(Meetings.mentor_id == mentor_id).all()

    # Convert meetings to a list of dictionaries
    meeting_list = [
        {
            "meeting_id": meeting.id,
            "student_usn": meeting.student_usn,
            "meeting_date": meeting.meeting_date,
            "venue": meeting.venue,
            "status":meeting.status,
            "progress_notes": meeting.progress_notes,
        }
        for meeting in meetings
    ]

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
        "duration": None,
        "mentor_id": None,
        "student_usn": [],
        "created_at": None,
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
                "duration": meeting.duration,
                "mentor_id": meeting.mentor_id,
                "created_at": meeting.created_at,
                "agenda": meeting.agenda,
            })
        meetings_dict[meeting_id]["student_usn"].append(meeting.student_usn)

    return list(meetings_dict.values())

@router.put("/{meeting_id}/respond_meeting")
def respond_meeting(mentor_id: str, meeting_id: str, response: MeetingResponseRequest, db: Session = Depends(get_db)):
    """
    Mentor can approve or reject a scheduled meeting.
    """
    meeting = db.query(Meetings).filter(Meetings.id == meeting_id, Meetings.mentor_id == mentor_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail=f"No meeting found with ID {meeting_id} for mentor {mentor_id}")
    
    status = response.status.lower()
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'approved' or 'rejected'.")

    meeting.status = status
    db.commit()
    
    student = db.query(Student).filter(Student.student_usn == meeting.student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"No student found with USN {meeting.student_usn}")
    
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")
    
    subject = "Meeting Request Update"
    body = (
        f"Dear {student.student_name},\n\n"
        f"Your meeting request with mentor {mentor.mentor_name} has been {status}.\n\n"
        f"Best regards,\nYour Mentorship Program"
    )
    send_email(student.student_email, subject, body)
    
    return {"message": f"Meeting {status} successfully"}
