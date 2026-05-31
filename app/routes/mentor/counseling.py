from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.db.database import get_db
from app.db.models.counseling import CounselingSession, CounselingAvailability, SessionIssuesResolution, CounselingIssueResolutionFeedback, CounselingReminder
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.schemas.counseling import (
    CounselingSessionResponse,
    CounselingSessionUpdate,
    CounselingAvailabilityCreate,
    CounselingAvailabilityResponse,
    CounselingStats,
    FeedbackResponse,
    IssueResolutionResponse,
    IssuesResolutionUpdate,
    IssueResolutionFeedbackRow,
    IssueResolutionFeedbackUpdate,
    OutcomeUpdate,
    FollowupSchedule,
    FollowupDueResponse,
)
from app.core.dependencies import get_current_mentor
from app.services.email_services import send_email
from app.services.s3bucket import s3_client, get_document_url
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json
import io

router = APIRouter()


def _file_url(value) -> Optional[str]:
    if not value:
        return None
    return get_document_url(value)


def _student_feedback_file_url(session) -> Optional[str]:
    return _file_url(getattr(session, "student_feedback_file", None))


def _mentor_feedback_file_url(session) -> Optional[str]:
    return _file_url(getattr(session, "mentor_feedback_file", None))


def _student_issues_proof_file_url(session) -> Optional[str]:
    return _file_url(getattr(session, "student_issues_proof_file", None))


def _mentor_resolution_proof_file_url(session) -> Optional[str]:
    return _file_url(getattr(session, "mentor_resolution_proof_file", None))


def _issue_resolution_feedback_proof_file_url(session) -> Optional[str]:
    return _file_url(getattr(session, "issue_resolution_feedback_proof_file", None))


def _get_issue_resolution_feedback(db, counseling_id: str) -> list:
    """Return 3 rows for session card table: issue_raised, details_of_resolution, resolution."""
    order = ["issue_raised", "details_of_resolution", "resolution"]
    rows = db.query(CounselingIssueResolutionFeedback).filter(
        CounselingIssueResolutionFeedback.counseling_id == counseling_id
    ).all()
    by_type = {r.row_type: r for r in rows}
    return [
        IssueResolutionFeedbackRow(
            row_type=rt,
            description=getattr(by_type.get(rt), "description", None) or None,
            feedback_date=getattr(by_type.get(rt), "feedback_date", None),
            status=getattr(by_type.get(rt), "status", None),
        )
        for rt in order
    ]


MENTOR_FEEDBACK_ALLOWED_EXTENSIONS = {"pdf"}  # PDF only for mentor proof
MAX_FEEDBACK_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.get("/counseling/sessions", response_model=List[CounselingSessionResponse])
async def get_mentor_counseling_sessions(
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    is_urgent: Optional[bool] = Query(None, description="Filter by urgency"),
    limit: int = Query(10, description="Number of sessions to return"),
    offset: int = Query(0, description="Number of sessions to skip")
):
    """
    Get all counseling sessions for the current mentor
    """
    mentor_id = current_mentor.get("mentor_id")
    
    query = db.query(CounselingSession).filter(CounselingSession.mentor_id == mentor_id)
    
    if status:
        query = query.filter(CounselingSession.status == status)
    
    if is_urgent is not None:
        query = query.filter(CounselingSession.is_urgent == is_urgent)
    
    sessions = query.order_by(desc(CounselingSession.session_date)).offset(offset).limit(limit).all()
    
    result = []
    for session in sessions:
        # Get student details
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        
        result.append(CounselingSessionResponse(
            id=session.id,
            counseling_id=session.counseling_id,
            student_usn=session.student_usn,
            mentor_id=session.mentor_id,
            session_date=session.session_date,
            venue=session.venue,
            reason=session.reason,
            status=session.status,
            google_meet_link=session.google_meet_link,
            meeting_id=session.meeting_id,
            notes=session.notes,
            feedback=session.feedback,
            is_urgent=session.is_urgent,
            created_at=session.created_at,
            updated_at=session.updated_at,
            student_feedback=session.student_feedback,
            student_rating=session.student_rating,
            student_feedback_date=session.student_feedback_date,
            student_feedback_file_url=_student_feedback_file_url(session),
            mentor_feedback=session.mentor_feedback,
            mentor_rating=session.mentor_rating,
            mentor_feedback_date=session.mentor_feedback_date,
            mentor_feedback_file_url=_mentor_feedback_file_url(session),
            student_issues_proof_file_url=_student_issues_proof_file_url(session),
            mentor_resolution_proof_file_url=_mentor_resolution_proof_file_url(session),
            issue_resolution_feedback=_get_issue_resolution_feedback(db, session.counseling_id),
            issue_resolution_feedback_proof_file_url=_issue_resolution_feedback_proof_file_url(session),
            student_name=student.student_name if student else None,
            student_email=student.student_email if student else None,
            student_phoneno=student.student_phoneno if student else None
        ))

    return result

@router.get("/counseling/sessions/{counseling_id}", response_model=CounselingSessionResponse)
async def get_counseling_session_details(
    counseling_id: str,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific counseling session
    """
    mentor_id = current_mentor.get("mentor_id")
    
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    # Get student details
    student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
    
    return CounselingSessionResponse(
        id=session.id,
        counseling_id=session.counseling_id,
        student_usn=session.student_usn,
        mentor_id=session.mentor_id,
        session_date=session.session_date,
        venue=session.venue,
        reason=session.reason,
        status=session.status,
        google_meet_link=session.google_meet_link,
        meeting_id=session.meeting_id,
        notes=session.notes,
        feedback=session.feedback,
        is_urgent=session.is_urgent,
        created_at=session.created_at,
        updated_at=session.updated_at,
        referred_to_name=getattr(session, "referred_to_name", None),
        referred_to_contact=getattr(session, "referred_to_contact", None),
        referred_at=getattr(session, "referred_at", None),
        student_feedback=session.student_feedback,
        student_rating=session.student_rating,
        student_feedback_date=session.student_feedback_date,
        student_feedback_file_url=_student_feedback_file_url(session),
        mentor_feedback=session.mentor_feedback,
        mentor_rating=session.mentor_rating,
        mentor_feedback_date=session.mentor_feedback_date,
        mentor_feedback_file_url=_mentor_feedback_file_url(session),
        student_issues_proof_file_url=_student_issues_proof_file_url(session),
        student_name=student.student_name if student else None,
        student_email=student.student_email if student else None,
        student_phoneno=student.student_phoneno if student else None
    )

@router.put("/counseling/sessions/{counseling_id}", response_model=CounselingSessionResponse)
async def update_counseling_session(
    counseling_id: str,
    update_data: CounselingSessionUpdate,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Update a counseling session (mentor can update status, notes, feedback)
    """
    mentor_id = current_mentor.get("mentor_id")
    
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    # Update fields
    if update_data.session_date:
        session.session_date = update_data.session_date
    
    if update_data.venue:
        session.venue = update_data.venue
    
    if update_data.reason:
        session.reason = update_data.reason
    
    if update_data.status:
        status_value = update_data.status.value if hasattr(update_data.status, "value") else str(update_data.status)
        if status_value == "referred":
            if not update_data.referred_to_name or not str(update_data.referred_to_name).strip():
                raise HTTPException(status_code=400, detail="referred_to_name is required when referring a student")
            session.referred_to_name = update_data.referred_to_name.strip()
            session.referred_to_contact = update_data.referred_to_contact.strip() if update_data.referred_to_contact else None
            session.referred_at = datetime.utcnow()
        session.status = status_value
    
    if update_data.notes:
        session.notes = update_data.notes
    
    if update_data.feedback:
        session.feedback = update_data.feedback
    
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    # Get student details
    student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
    mentor_name = current_mentor.get("mentor_name", "Your mentor")
    
    # Send email to student when referred to specialist
    if update_data.status:
        status_value = update_data.status.value if hasattr(update_data.status, "value") else str(update_data.status)
        if status_value == "referred" and student and student.student_email:
            try:
                ref_name = getattr(session, "referred_to_name", None) or update_data.referred_to_name
                ref_contact = getattr(session, "referred_to_contact", None) or update_data.referred_to_contact
                email_subject = f"Student Support – Referral by {mentor_name}"
                email_body = f"""
                <h2 style="color: #2c3e50; margin-bottom: 20px;">Student Support – Referral</h2>
                <p>Dear {student.student_name if student else 'Student'},</p>
                <p>For your Student Support session <strong>{session.counseling_id}</strong>, <strong>{mentor_name}</strong> has referred you to the following person for this session:</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Referred to:</strong> {ref_name}</p>
                    {f'<p><strong>Contact:</strong> {ref_contact}</p>' if ref_contact else ''}
                </div>
                <p>Please reach out to them to schedule or complete your session.</p>
                <p>Best regards,<br><strong>Mentee Tracker Team</strong></p>
                """
                send_email(student.student_email, email_subject, email_body)
                print(f"Referral email sent to {student.student_email}")
            except Exception as e:
                print(f"Failed to send referral email: {e}")
    
    # Send email notification to student if status changed (non-referred)
    if update_data.status and update_data.status != "scheduled":
        status_value = update_data.status.value if hasattr(update_data.status, "value") else str(update_data.status)
        if status_value != "referred":
            try:
                # Format session date for email
                formatted_date = session.session_date.strftime("%B %d, %Y at %I:%M %p")
                
                # Create email content based on status
                if status_value == "completed":
                    email_subject = f"Counseling Session Completed - {session.counseling_id}"
                    status_color = "#28a745"
                    status_text = "Completed"
                elif status_value == "cancelled":
                    email_subject = f"Counseling Session Cancelled - {session.counseling_id}"
                    status_color = "#dc3545"
                    status_text = "Cancelled"
                elif status_value == "rescheduled":
                    email_subject = f"Counseling Session Rescheduled - {session.counseling_id}"
                    status_color = "#ffc107"
                    status_text = "Rescheduled"
                else:
                    email_subject = f"Counseling Session Updated - {session.counseling_id}"
                    status_color = "#17a2b8"
                    status_text = status_value.title()
                
                email_body = f"""
            <h2 style="color: #2c3e50; margin-bottom: 20px;">Counseling Session Update</h2>
            
            <p>Dear {student.student_name if student else 'Student'},</p>
            
            <p>Your counseling session has been updated. Here are the current details:</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Session Details</h3>
                <p><strong>Session ID:</strong> {session.counseling_id}</p>
                <p><strong>Date & Time:</strong> {formatted_date}</p>
                <p><strong>Venue:</strong> {session.venue}</p>
                <p><strong>Reason:</strong> {session.reason}</p>
                <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{status_text}</span></p>
                {f'<p><strong>Priority:</strong> <span style="color: #dc3545; font-weight: bold;">URGENT</span></p>' if session.is_urgent else ''}
            </div>
            
            {f'''
            <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Mentor Information</h3>
                <p><strong>Mentor:</strong> {current_mentor.get("mentor_name", "Not Available")}</p>
                <p><strong>Email:</strong> {current_mentor.get("mentor_email", "Not Available")}</p>
            </div>
            ''' if current_mentor else ''}
            
            {f'''
            <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h3 style="color: #856404; margin-top: 0;">Google Meet Link</h3>
                <p><strong>Meeting Link:</strong> <a href="{session.google_meet_link}" style="color: #007bff;">{session.google_meet_link}</a></p>
                <p><strong>Meeting ID:</strong> {session.meeting_id}</p>
            </div>
            ''' if session.google_meet_link else ''}
            
            {f'''
            <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="color: #155724; margin-top: 0;">Mentor Notes</h3>
                <p>{session.notes}</p>
            </div>
            ''' if session.notes else ''}
            
            {f'''
            <div style="background: #cce5ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #007bff;">
                <h3 style="color: #004085; margin-top: 0;">Mentor Feedback</h3>
                <p>{session.feedback}</p>
            </div>
            ''' if session.feedback else ''}
            
            <div style="background: #d1ecf1; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #0c5460; margin-top: 0;">Next Steps</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    f'<li>Your session has been marked as {status_text.lower()}</li>'
                    <li>If you have any questions, please contact your mentor directly</li>
                    <li>For future sessions, you can request new counseling appointments through the system</li>
                </ul>
            </div>
            
            <p>If you have any questions or concerns, please contact your mentor or the administration.</p>
            
            <p>Best regards,<br>
            <strong>Mentee Tracker Team</strong></p>
            """
                
                # Send email
                if student and student.student_email:
                    send_email(student.student_email, email_subject, email_body)
                    print(f"Email sent successfully to {student.student_email} for counseling session {session.counseling_id} status update")
            except Exception as e:
                print(f"Failed to send email to {student.student_email if student else 'unknown'}: {e}")
    
    return CounselingSessionResponse(
        id=session.id,
        counseling_id=session.counseling_id,
        student_usn=session.student_usn,
        mentor_id=session.mentor_id,
        session_date=session.session_date,
        venue=session.venue,
        reason=session.reason,
        status=session.status,
        google_meet_link=session.google_meet_link,
        meeting_id=session.meeting_id,
        notes=session.notes,
        feedback=session.feedback,
        is_urgent=session.is_urgent,
        created_at=session.created_at,
        updated_at=session.updated_at,
        referred_to_name=getattr(session, "referred_to_name", None),
        referred_to_contact=getattr(session, "referred_to_contact", None),
        referred_at=getattr(session, "referred_at", None),
        student_feedback=session.student_feedback,
        student_rating=session.student_rating,
        student_feedback_date=session.student_feedback_date,
        student_feedback_file_url=_student_feedback_file_url(session),
        mentor_feedback=session.mentor_feedback,
        mentor_rating=session.mentor_rating,
        mentor_feedback_date=session.mentor_feedback_date,
        mentor_feedback_file_url=_mentor_feedback_file_url(session),
        student_issues_proof_file_url=_student_issues_proof_file_url(session),
        mentor_resolution_proof_file_url=_mentor_resolution_proof_file_url(session),
        issue_resolution_feedback=_get_issue_resolution_feedback(db, session.counseling_id),
        issue_resolution_feedback_proof_file_url=_issue_resolution_feedback_proof_file_url(session),
        student_name=student.student_name if student else None,
        student_email=student.student_email if student else None,
        student_phoneno=student.student_phoneno if student else None
    )

@router.get("/counseling/upcoming", response_model=List[CounselingSessionResponse])
async def get_upcoming_sessions(
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
    days_ahead: int = Query(7, description="Number of days ahead to look for sessions")
):
    """
    Get upcoming counseling sessions for the mentor
    """
    mentor_id = current_mentor.get("mentor_id")
    end_date = datetime.utcnow() + timedelta(days=days_ahead)
    
    # Get current time for comparison
    now = datetime.utcnow()
    
    sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.mentor_id == mentor_id,
            CounselingSession.status == "scheduled",
            CounselingSession.session_date >= now,
            CounselingSession.session_date <= end_date
        )
    ).order_by(CounselingSession.session_date).all()
    
    result = []
    for session in sessions:
        # Get student details
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        
        result.append(CounselingSessionResponse(
            id=session.id,
            counseling_id=session.counseling_id,
            student_usn=session.student_usn,
            mentor_id=session.mentor_id,
            session_date=session.session_date,
            venue=session.venue,
            reason=session.reason,
            status=session.status,
            google_meet_link=session.google_meet_link,
            meeting_id=session.meeting_id,
            notes=session.notes,
            feedback=session.feedback,
            is_urgent=session.is_urgent,
            created_at=session.created_at,
            updated_at=session.updated_at,
            referred_to_name=getattr(session, "referred_to_name", None),
            referred_to_contact=getattr(session, "referred_to_contact", None),
            referred_at=getattr(session, "referred_at", None),
            student_feedback=session.student_feedback,
            student_rating=session.student_rating,
            student_feedback_date=session.student_feedback_date,
            student_feedback_file_url=_student_feedback_file_url(session),
            mentor_feedback=session.mentor_feedback,
            mentor_rating=session.mentor_rating,
            mentor_feedback_date=session.mentor_feedback_date,
            mentor_feedback_file_url=_mentor_feedback_file_url(session),
            student_issues_proof_file_url=_student_issues_proof_file_url(session),
            mentor_resolution_proof_file_url=_mentor_resolution_proof_file_url(session),
            issue_resolution_feedback=_get_issue_resolution_feedback(db, session.counseling_id),
            issue_resolution_feedback_proof_file_url=_issue_resolution_feedback_proof_file_url(session),
            student_name=student.student_name if student else None,
            student_email=student.student_email if student else None,
            student_phoneno=student.student_phoneno if student else None
        ))

    return result

@router.get("/counseling/stats", response_model=CounselingStats)
async def get_mentor_counseling_stats(
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Get counseling statistics for the current mentor
    """
    mentor_id = current_mentor.get("mentor_id")
    
    total_sessions = db.query(CounselingSession).filter(CounselingSession.mentor_id == mentor_id).count()
    scheduled_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.mentor_id == mentor_id,
            CounselingSession.status == "scheduled"
        )
    ).count()
    completed_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.mentor_id == mentor_id,
            CounselingSession.status == "completed"
        )
    ).count()
    cancelled_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.mentor_id == mentor_id,
            CounselingSession.status == "cancelled"
        )
    ).count()
    
    # Get current time for comparison
    now = datetime.utcnow()
    
    # Upcoming sessions (scheduled and in the future)
    upcoming_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.mentor_id == mentor_id,
            CounselingSession.status == "scheduled",
            CounselingSession.session_date > now
        )
    ).count()
    
    urgent_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.mentor_id == mentor_id,
            CounselingSession.is_urgent == True,
            CounselingSession.status == "scheduled"
        )
    ).count()
    
    return CounselingStats(
        total_sessions=total_sessions,
        scheduled_sessions=scheduled_sessions,
        completed_sessions=completed_sessions,
        cancelled_sessions=cancelled_sessions,
        upcoming_sessions=upcoming_sessions,
        urgent_sessions=urgent_sessions
    )

@router.post("/counseling/availability", response_model=CounselingAvailabilityResponse)
async def set_availability(
    availability_data: CounselingAvailabilityCreate,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Set mentor availability for counseling sessions
    """
    mentor_id = current_mentor.get("mentor_id")
    
    # Check if availability already exists for this day
    existing = db.query(CounselingAvailability).filter(
        and_(
            CounselingAvailability.mentor_id == mentor_id,
            CounselingAvailability.day_of_week == availability_data.day_of_week
        )
    ).first()
    
    if existing:
        # Update existing availability
        existing.start_time = availability_data.start_time
        existing.end_time = availability_data.end_time
        existing.is_available = availability_data.is_available
        existing.available_from = availability_data.available_from
        existing.available_until = availability_data.available_until
        existing.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new availability
        availability = CounselingAvailability(
            mentor_id=mentor_id,
            day_of_week=availability_data.day_of_week,
            start_time=availability_data.start_time,
            end_time=availability_data.end_time,
            is_available=availability_data.is_available,
            available_from=availability_data.available_from,
            available_until=availability_data.available_until
        )
        
        db.add(availability)
        db.commit()
        db.refresh(availability)
        return availability

@router.get("/counseling/availability", response_model=List[CounselingAvailabilityResponse])
async def get_availability(
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Get mentor availability
    """
    mentor_id = current_mentor.get("mentor_id")
    
    availability = db.query(CounselingAvailability).filter(
        CounselingAvailability.mentor_id == mentor_id
    ).all()
    
    return availability

@router.post("/counseling/sessions/{counseling_id}/feedback", response_model=FeedbackResponse)
async def submit_mentor_feedback(
    counseling_id: str,
    feedback: str = Form(..., description="Mentor feedback text"),
    rating: int = Form(..., ge=1, le=5, description="Rating 1-5"),
    file: Optional[UploadFile] = File(None, description="Optional proof file (PDF)"),
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a completed or referred counseling session (mentor). Optional PDF proof.
    """
    mentor_id = current_mentor.get("mentor_id")

    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")

    # Allow mentor feedback for completed or referred sessions
    if session.status not in ("completed", "referred"):
        raise HTTPException(
            status_code=400,
            detail="Feedback can only be submitted for referred or completed sessions",
        )

    if session.mentor_feedback:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this session")

    session.mentor_feedback = feedback.strip()
    session.mentor_rating = rating
    session.mentor_feedback_date = datetime.utcnow()

    if file and file.filename and file.filename.strip():
        ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
        if ext not in MENTOR_FEEDBACK_ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only PDF format is allowed for mentor feedback proof."
            )
        content = await file.read()
        if len(content) > MAX_FEEDBACK_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size must be under 10 MB")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        proof_key = f"counseling-feedback/mentor/{mentor_id}/{counseling_id}_{timestamp}.{ext}"
        try:
            import io
            file_url = s3_client.upload_fileobj(
                io.BytesIO(content),
                None,
                proof_key,
                ExtraArgs={"ContentType": file.content_type or "application/pdf"}
            )
            session.mentor_feedback_file = file_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    db.commit()
    db.refresh(session)

    try:
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()

        if student and student.student_email:
            email_subject = f"Mentor Feedback Received - {counseling_id}"
            email_body = f"""
            <h2 style="color: #2c3e50; margin-bottom: 20px;">Mentor Feedback Received</h2>
            <p>Dear {student.student_name if student else 'Student'},</p>
            <p>Your mentor has provided feedback for your counseling session:</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Session Details</h3>
                <p><strong>Session ID:</strong> {counseling_id}</p>
                <p><strong>Mentor:</strong> {mentor.mentor_name if mentor else 'Unknown'}</p>
                <p><strong>Date:</strong> {session.session_date.strftime("%B %d, %Y at %I:%M %p")}</p>
                <p><strong>Rating:</strong> {'⭐' * rating} ({rating}/5)</p>
            </div>
            <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Mentor Feedback</h3>
                <p style="font-style: italic;">"{feedback}"</p>
            </div>
            <p>We hope this feedback helps you in your academic journey!</p>
            <p>Best regards,<br><strong>Mentee Tracker Team</strong></p>
            """
            send_email(student.student_email, email_subject, email_body)
            print(f"Feedback notification email sent to student {student.student_email}")
    except Exception as e:
        print(f"Failed to send feedback notification email: {e}")

    return FeedbackResponse(
        success=True,
        message="Feedback submitted successfully",
        feedback_id=counseling_id
    )

@router.get("/counseling/sessions/{counseling_id}/feedback")
async def get_session_feedback_mentor(
    counseling_id: str,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Get feedback for a specific counseling session (mentor view)
    """
    mentor_id = current_mentor.get("mentor_id")
    
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    return {
        "counseling_id": session.counseling_id,
        "student_feedback": session.student_feedback,
        "student_rating": session.student_rating,
        "student_feedback_date": session.student_feedback_date,
        "student_feedback_file_url": _student_feedback_file_url(session),
        "mentor_feedback": session.mentor_feedback,
        "mentor_rating": session.mentor_rating,
        "mentor_feedback_date": session.mentor_feedback_date,
        "mentor_feedback_file_url": _mentor_feedback_file_url(session),
        "student_issues_proof_file_url": _student_issues_proof_file_url(session),
        "mentor_resolution_proof_file_url": _mentor_resolution_proof_file_url(session),
        "can_submit_feedback": session.status in ("completed", "referred") and not session.mentor_feedback,
    }


@router.get("/counseling/sessions/{counseling_id}/issues-resolution", response_model=List[IssueResolutionResponse])
async def get_session_issues_resolution_mentor(
    counseling_id: str,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Get Details of Issues Raised & Resolved for a session (mentor view).
    """
    mentor_id = current_mentor.get("mentor_id")
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    rows = db.query(SessionIssuesResolution).filter(SessionIssuesResolution.counseling_id == counseling_id).order_by(SessionIssuesResolution.serial_no).all()
    return [
        IssueResolutionResponse(
            id=r.id,
            counseling_id=r.counseling_id,
            serial_no=r.serial_no,
            issues_raised=r.issues_raised,
            date_issue_raised=r.date_issue_raised,
            resolution_details=r.resolution_details,
            date_resolution_provided=r.date_resolution_provided,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.put("/counseling/sessions/{counseling_id}/issues-resolution", response_model=List[IssueResolutionResponse])
async def update_session_issues_resolution_mentor(
    counseling_id: str,
    rows: str = Form(..., description="JSON array of resolution updates per row"),
    file: Optional[UploadFile] = File(None, description="Optional resolution proof file (PDF)"),
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Update resolution details and date for Issues Raised rows (mentor only). Optional resolution proof upload.
    """
    mentor_id = current_mentor.get("mentor_id")
    try:
        data = IssuesResolutionUpdate(rows=json.loads(rows))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid rows JSON: {str(e)}")
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    for row in data.rows:
        rec = db.query(SessionIssuesResolution).filter(
            SessionIssuesResolution.id == row.id,
            SessionIssuesResolution.counseling_id == counseling_id
        ).first()
        if rec:
            if row.resolution_details is not None:
                rec.resolution_details = row.resolution_details
            if row.date_resolution_provided is not None:
                rec.date_resolution_provided = row.date_resolution_provided
    if file and file.filename and file.filename.strip():
        ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
        if ext not in MENTOR_FEEDBACK_ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Only PDF format is allowed for resolution proof.")
        content = await file.read()
        if len(content) > MAX_FEEDBACK_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Resolution proof file must be under 10 MB")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        proof_key = f"counseling-resolution-proof/mentor/{mentor_id}/{counseling_id}_{timestamp}.{ext}"
        try:
            file_url = s3_client.upload_fileobj(
                io.BytesIO(content),
                None,
                proof_key,
                ExtraArgs={"ContentType": file.content_type or "application/pdf"}
            )
            session.mentor_resolution_proof_file = file_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload resolution proof: {str(e)}")
    db.commit()
    db.refresh(session)
    rows_out = db.query(SessionIssuesResolution).filter(SessionIssuesResolution.counseling_id == counseling_id).order_by(SessionIssuesResolution.serial_no).all()
    return [
        IssueResolutionResponse(
            id=r.id,
            counseling_id=r.counseling_id,
            serial_no=r.serial_no,
            issues_raised=r.issues_raised,
            date_issue_raised=r.date_issue_raised,
            resolution_details=r.resolution_details,
            date_resolution_provided=r.date_resolution_provided,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows_out
    ]


@router.put("/counseling/sessions/{counseling_id}/issue-resolution-feedback", response_model=List[IssueResolutionFeedbackRow])
async def update_issue_resolution_feedback(
    counseling_id: str,
    rows: str = Form(..., description="JSON array of 3 rows: issue_raised, details_of_resolution, resolution"),
    file: Optional[UploadFile] = File(None, description="Optional proof file (PDF) for this feedback"),
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Update the 3-row tabular feedback (Issue Raised by Mentor, Details of Resolution, Resolution) for the session card.
    Optional proof file (PDF) can be uploaded.
    """
    mentor_id = current_mentor.get("mentor_id")
    try:
        data = IssueResolutionFeedbackUpdate(rows=json.loads(rows))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid rows JSON: {str(e)}")
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    allowed_types = {"issue_raised", "details_of_resolution", "resolution"}
    for row in data.rows:
        if row.row_type not in allowed_types:
            continue
        rec = db.query(CounselingIssueResolutionFeedback).filter(
            CounselingIssueResolutionFeedback.counseling_id == counseling_id,
            CounselingIssueResolutionFeedback.row_type == row.row_type
        ).first()
        if rec:
            rec.description = row.description
            rec.feedback_date = row.feedback_date
            rec.status = row.status if row.status in ("WIP", "Close") else None
        else:
            db.add(CounselingIssueResolutionFeedback(
                counseling_id=counseling_id,
                row_type=row.row_type,
                description=row.description,
                feedback_date=row.feedback_date,
                status=row.status if row.status in ("WIP", "Close") else None,
            ))
    if file and file.filename and file.filename.strip():
        ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
        if ext not in MENTOR_FEEDBACK_ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Only PDF format is allowed for proof.")
        content = await file.read()
        if len(content) > MAX_FEEDBACK_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Proof file must be under 10 MB")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        proof_key = f"counseling-issue-resolution-feedback-proof/mentor/{mentor_id}/{counseling_id}_{timestamp}.{ext}"
        try:
            file_url = s3_client.upload_fileobj(
                io.BytesIO(content),
                None,
                proof_key,
                ExtraArgs={"ContentType": file.content_type or "application/pdf"}
            )
            session.issue_resolution_feedback_proof_file = file_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload proof: {str(e)}")
    db.commit()
    return _get_issue_resolution_feedback(db, counseling_id)


# ============ OUTCOME AND FOLLOW-UP TRACKING ENDPOINTS ============

def _generate_followup_counseling_id(db: Session) -> str:
    """Generate a unique counseling ID for follow-up sessions."""
    import random
    import string
    while True:
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        counseling_id = f"FU-{random_suffix}"
        existing = db.query(CounselingSession).filter(CounselingSession.counseling_id == counseling_id).first()
        if not existing:
            return counseling_id


@router.put("/counseling/sessions/{counseling_id}/outcome")
async def set_session_outcome(
    counseling_id: str,
    outcome_data: OutcomeUpdate,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Set outcome status and notes for a completed counseling session.
    """
    mentor_id = current_mentor.get("mentor_id")
    
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Outcome can only be set for completed sessions")
    
    valid_outcomes = ["fully_resolved", "partially_resolved", "unresolved", "needs_followup"]
    if outcome_data.outcome_status not in valid_outcomes:
        raise HTTPException(status_code=400, detail=f"Invalid outcome status. Must be one of: {valid_outcomes}")
    
    session.outcome_status = outcome_data.outcome_status
    session.outcome_notes = outcome_data.outcome_notes
    
    if outcome_data.followup_date:
        session.followup_date = outcome_data.followup_date
        session.followup_scheduled = False
    
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    
    student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
    
    if student and student.student_email and outcome_data.outcome_status == "needs_followup":
        try:
            mentor_name = current_mentor.get("mentor_name", "Your mentor")
            email_subject = f"Student Support Session Outcome - Follow-up Recommended"
            followup_text = f"A follow-up session has been recommended for {outcome_data.followup_date.strftime('%B %d, %Y')}." if outcome_data.followup_date else "A follow-up session may be scheduled soon."
            email_body = f"""
            <h2 style="color: #2c3e50; margin-bottom: 20px;">Student Support Session Outcome</h2>
            <p>Dear {student.student_name},</p>
            <p>Your mentor <strong>{mentor_name}</strong> has reviewed your counseling session <strong>{counseling_id}</strong> and provided the following outcome:</p>
            <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <p><strong>Status:</strong> Needs Follow-up</p>
                {f'<p><strong>Notes:</strong> {outcome_data.outcome_notes}</p>' if outcome_data.outcome_notes else ''}
            </div>
            <p>{followup_text}</p>
            <p>Best regards,<br><strong>Mentee Tracker Team</strong></p>
            """
            send_email(student.student_email, email_subject, email_body)
        except Exception as e:
            print(f"Failed to send outcome email: {e}")
    
    return {
        "success": True,
        "message": "Outcome set successfully",
        "counseling_id": counseling_id,
        "outcome_status": session.outcome_status,
        "followup_date": session.followup_date
    }


@router.post("/counseling/sessions/{counseling_id}/schedule-followup", response_model=CounselingSessionResponse)
async def schedule_followup_session(
    counseling_id: str,
    followup_data: FollowupSchedule,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Schedule a follow-up session linked to the original counseling session.
    """
    mentor_id = current_mentor.get("mentor_id")
    
    parent_session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    
    if not parent_session:
        raise HTTPException(status_code=404, detail="Parent counseling session not found")
    
    if parent_session.status != "completed":
        raise HTTPException(status_code=400, detail="Follow-up can only be scheduled for completed sessions")
    
    new_counseling_id = _generate_followup_counseling_id(db)
    reason = followup_data.reason or f"Follow-up for session {counseling_id}: {parent_session.reason}"
    
    followup_session = CounselingSession(
        counseling_id=new_counseling_id,
        student_usn=parent_session.student_usn,
        mentor_id=mentor_id,
        session_date=followup_data.session_date,
        venue=followup_data.venue,
        reason=reason,
        status="scheduled",
        is_urgent=followup_data.is_urgent,
        parent_session_id=counseling_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(followup_session)
    
    parent_session.followup_scheduled = True
    parent_session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(followup_session)
    
    student = db.query(Student).filter(Student.student_usn == parent_session.student_usn).first()
    
    if student and student.student_email:
        try:
            mentor_name = current_mentor.get("mentor_name", "Your mentor")
            formatted_date = followup_data.session_date.strftime("%B %d, %Y at %I:%M %p")
            email_subject = f"Follow-up Session Scheduled - {new_counseling_id}"
            email_body = f"""
            <h2 style="color: #2c3e50; margin-bottom: 20px;">Follow-up Session Scheduled</h2>
            <p>Dear {student.student_name},</p>
            <p>A follow-up session has been scheduled for you by <strong>{mentor_name}</strong>.</p>
            <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h3 style="color: #155724; margin-top: 0;">Session Details</h3>
                <p><strong>Session ID:</strong> {new_counseling_id}</p>
                <p><strong>Date & Time:</strong> {formatted_date}</p>
                <p><strong>Venue:</strong> {followup_data.venue}</p>
                <p><strong>Original Session:</strong> {counseling_id}</p>
                {f'<p><strong>Priority:</strong> <span style="color: #dc3545; font-weight: bold;">URGENT</span></p>' if followup_data.is_urgent else ''}
            </div>
            <p>Please make sure to attend this follow-up session.</p>
            <p>Best regards,<br><strong>Mentee Tracker Team</strong></p>
            """
            send_email(student.student_email, email_subject, email_body)
        except Exception as e:
            print(f"Failed to send follow-up notification: {e}")
    
    return CounselingSessionResponse(
        id=followup_session.id,
        counseling_id=followup_session.counseling_id,
        student_usn=followup_session.student_usn,
        mentor_id=followup_session.mentor_id,
        session_date=followup_session.session_date,
        venue=followup_session.venue,
        reason=followup_session.reason,
        status=followup_session.status,
        google_meet_link=followup_session.google_meet_link,
        meeting_id=followup_session.meeting_id,
        notes=followup_session.notes,
        feedback=followup_session.feedback,
        is_urgent=followup_session.is_urgent,
        created_at=followup_session.created_at,
        updated_at=followup_session.updated_at,
        outcome_status=followup_session.outcome_status,
        outcome_notes=followup_session.outcome_notes,
        followup_date=followup_session.followup_date,
        followup_scheduled=followup_session.followup_scheduled,
        parent_session_id=followup_session.parent_session_id,
        student_name=student.student_name if student else None,
        student_email=student.student_email if student else None,
        student_phoneno=student.student_phoneno if student else None
    )


@router.get("/counseling/followups-due", response_model=List[FollowupDueResponse])
async def get_followups_due(
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
    include_overdue: bool = Query(True, description="Include overdue follow-ups"),
    days_ahead: int = Query(14, description="Days ahead to look for upcoming follow-ups")
):
    """
    Get sessions that need follow-up attention (due or overdue).
    """
    mentor_id = current_mentor.get("mentor_id")
    today = datetime.utcnow().date()
    future_date = today + timedelta(days=days_ahead)
    
    query = db.query(CounselingSession).filter(
        and_(
            CounselingSession.mentor_id == mentor_id,
            CounselingSession.status == "completed",
            CounselingSession.outcome_status == "needs_followup",
            CounselingSession.followup_scheduled == False,
            CounselingSession.followup_date.isnot(None)
        )
    )
    
    if include_overdue:
        query = query.filter(CounselingSession.followup_date <= future_date)
    else:
        query = query.filter(
            and_(
                CounselingSession.followup_date >= today,
                CounselingSession.followup_date <= future_date
            )
        )
    
    sessions = query.order_by(CounselingSession.followup_date).all()
    
    result = []
    for session in sessions:
        student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
        days_until = (session.followup_date - today).days
        
        result.append(FollowupDueResponse(
            counseling_id=session.counseling_id,
            student_usn=session.student_usn,
            student_name=student.student_name if student else None,
            session_date=session.session_date,
            followup_date=session.followup_date,
            outcome_status=session.outcome_status,
            outcome_notes=session.outcome_notes,
            days_until_followup=days_until,
            is_overdue=days_until < 0
        ))
    
    return result


@router.get("/counseling/students/{student_usn}/session-chain")
async def get_student_session_chain(
    student_usn: str,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Get the linked session chain for a student (original sessions and their follow-ups).
    """
    mentor_id = current_mentor.get("mentor_id")
    
    all_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.student_usn == student_usn,
            CounselingSession.mentor_id == mentor_id
        )
    ).order_by(CounselingSession.created_at).all()
    
    if not all_sessions:
        return {"chains": [], "total_sessions": 0}
    
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    
    session_map = {s.counseling_id: s for s in all_sessions}
    root_sessions = [s for s in all_sessions if not s.parent_session_id]
    
    def build_chain(session):
        chain = [{
            "counseling_id": session.counseling_id,
            "session_date": session.session_date,
            "status": session.status,
            "reason": session.reason,
            "venue": session.venue,
            "is_urgent": session.is_urgent,
            "outcome_status": session.outcome_status,
            "outcome_notes": session.outcome_notes,
            "followup_date": session.followup_date,
            "followup_scheduled": session.followup_scheduled,
            "is_followup": bool(session.parent_session_id),
            "parent_session_id": session.parent_session_id,
            "created_at": session.created_at
        }]
        
        followups = [s for s in all_sessions if s.parent_session_id == session.counseling_id]
        for followup in sorted(followups, key=lambda x: x.created_at):
            chain.extend(build_chain(followup))
        
        return chain
    
    chains = []
    for root in root_sessions:
        chain = build_chain(root)
        chains.append({
            "original_session_id": root.counseling_id,
            "sessions": chain,
            "total_in_chain": len(chain)
        })
    
    return {
        "student_usn": student_usn,
        "student_name": student.student_name if student else None,
        "chains": chains,
        "total_sessions": len(all_sessions)
    }


@router.get("/counseling/analytics")
async def get_counseling_analytics(
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
    months: int = Query(6, description="Number of months to analyze")
):
    """
    Get counseling analytics for the current mentor.
    """
    mentor_id = current_mentor.get("mentor_id")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=months * 30)
    
    all_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.mentor_id == mentor_id,
            CounselingSession.created_at >= start_date
        )
    ).all()
    
    total = len(all_sessions)
    completed = len([s for s in all_sessions if s.status == 'completed'])
    scheduled = len([s for s in all_sessions if s.status == 'scheduled'])
    cancelled = len([s for s in all_sessions if s.status == 'cancelled'])
    referred = len([s for s in all_sessions if s.status == 'referred'])
    
    sessions_by_month = defaultdict(int)
    for session in all_sessions:
        month_key = session.created_at.strftime('%Y-%m')
        sessions_by_month[month_key] += 1
    
    sorted_months = sorted(sessions_by_month.keys())
    sessions_trend = [{"month": m, "count": sessions_by_month[m]} for m in sorted_months]
    
    outcome_counts = defaultdict(int)
    for session in all_sessions:
        if session.outcome_status:
            outcome_counts[session.outcome_status] += 1
        elif session.status == 'completed':
            outcome_counts['not_set'] += 1
    
    outcome_distribution = [
        {"status": k, "count": v} for k, v in outcome_counts.items()
    ]
    
    completed_sessions = [s for s in all_sessions if s.status == 'completed']
    total_resolution_time = 0
    sessions_with_feedback = 0
    for session in completed_sessions:
        if session.updated_at and session.created_at:
            resolution_days = (session.updated_at - session.created_at).days
            total_resolution_time += resolution_days
            sessions_with_feedback += 1
    
    avg_resolution_time = round(total_resolution_time / sessions_with_feedback, 1) if sessions_with_feedback > 0 else 0
    
    repeat_students = defaultdict(int)
    for session in all_sessions:
        repeat_students[session.student_usn] += 1
    
    students_with_multiple = len([usn for usn, count in repeat_students.items() if count > 1])
    
    followup_sessions = [s for s in all_sessions if s.parent_session_id]
    followup_rate = round(len(followup_sessions) / total * 100, 1) if total > 0 else 0
    
    urgent_count = len([s for s in all_sessions if s.is_urgent])
    
    ratings = [s.mentor_rating for s in all_sessions if s.mentor_rating]
    avg_mentor_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
    
    student_ratings = [s.student_rating for s in all_sessions if s.student_rating]
    avg_student_rating = round(sum(student_ratings) / len(student_ratings), 1) if student_ratings else 0
    
    return {
        "summary": {
            "total_sessions": total,
            "completed": completed,
            "scheduled": scheduled,
            "cancelled": cancelled,
            "referred": referred,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
            "urgent_sessions": urgent_count,
            "followup_sessions": len(followup_sessions),
            "followup_rate": followup_rate,
            "students_with_multiple_sessions": students_with_multiple,
            "unique_students": len(repeat_students)
        },
        "trends": {
            "sessions_by_month": sessions_trend
        },
        "outcomes": {
            "distribution": outcome_distribution,
            "avg_resolution_time_days": avg_resolution_time
        },
        "ratings": {
            "avg_mentor_rating": avg_mentor_rating,
            "avg_student_rating": avg_student_rating,
            "total_rated_sessions": len(ratings)
        },
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "months_analyzed": months
        }
    }


# ============ NOTIFICATION/REMINDER ENDPOINTS ============

@router.get("/counseling/notifications")
async def get_notifications(
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    limit: int = Query(20, description="Number of notifications to return")
):
    """
    Get notifications for the current mentor.
    """
    mentor_id = current_mentor.get("mentor_id")
    
    query = db.query(CounselingReminder).filter(
        and_(
            CounselingReminder.recipient_id == mentor_id,
            CounselingReminder.recipient_type == "mentor",
            CounselingReminder.status.in_(["sent", "pending"])
        )
    )
    
    if unread_only:
        query = query.filter(CounselingReminder.read_at.is_(None))
    
    notifications = query.order_by(desc(CounselingReminder.scheduled_for)).limit(limit).all()
    
    unread_count = db.query(CounselingReminder).filter(
        and_(
            CounselingReminder.recipient_id == mentor_id,
            CounselingReminder.recipient_type == "mentor",
            CounselingReminder.status.in_(["sent", "pending"]),
            CounselingReminder.read_at.is_(None)
        )
    ).count()
    
    result = []
    for notif in notifications:
        result.append({
            "id": notif.id,
            "session_id": notif.session_id,
            "reminder_type": notif.reminder_type,
            "title": notif.title,
            "message": notif.message,
            "scheduled_for": notif.scheduled_for,
            "sent_at": notif.sent_at,
            "read_at": notif.read_at,
            "status": notif.status,
            "is_read": notif.read_at is not None,
            "created_at": notif.created_at
        })
    
    return {
        "notifications": result,
        "unread_count": unread_count,
        "total": len(result)
    }


@router.put("/counseling/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read.
    """
    mentor_id = current_mentor.get("mentor_id")
    
    notification = db.query(CounselingReminder).filter(
        and_(
            CounselingReminder.id == notification_id,
            CounselingReminder.recipient_id == mentor_id
        )
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.read_at = datetime.utcnow()
    notification.status = "read"
    db.commit()
    
    return {"success": True, "message": "Notification marked as read"}


@router.put("/counseling/notifications/read-all")
async def mark_all_notifications_read(
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for the current mentor.
    """
    mentor_id = current_mentor.get("mentor_id")
    
    db.query(CounselingReminder).filter(
        and_(
            CounselingReminder.recipient_id == mentor_id,
            CounselingReminder.recipient_type == "mentor",
            CounselingReminder.read_at.is_(None)
        )
    ).update({
        "read_at": datetime.utcnow(),
        "status": "read"
    }, synchronize_session=False)
    
    db.commit()
    
    return {"success": True, "message": "All notifications marked as read"}
