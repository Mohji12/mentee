from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.db.database import get_db
from app.db.models.counseling import CounselingSession, CounselingAvailability, SessionIssuesResolution, CounselingIssueResolutionFeedback
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.schemas.counseling import (
    CounselingSessionCreate,
    CounselingSessionResponse,
    CounselingSessionUpdate,
    CounselingStats,
    FeedbackResponse,
    IssuesResolutionSubmit,
    IssueResolutionResponse,
)
from app.services.google_meet_service import GoogleMeetService
from app.services.email_services import send_email
from app.services.s3bucket import s3_client, S3_BUCKET_NAME
from app.core.dependencies import get_current_student
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import uuid

router = APIRouter()


def _student_feedback_file_url(session) -> Optional[str]:
    if not getattr(session, "student_feedback_file", None):
        return None
    return f"https://{S3_BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{session.student_feedback_file}"


def _mentor_feedback_file_url(session) -> Optional[str]:
    if not getattr(session, "mentor_feedback_file", None):
        return None
    return f"https://{S3_BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{session.mentor_feedback_file}"


def _student_issues_proof_file_url(session) -> Optional[str]:
    if not getattr(session, "student_issues_proof_file", None):
        return None
    return f"https://{S3_BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{session.student_issues_proof_file}"


def _mentor_resolution_proof_file_url(session) -> Optional[str]:
    if not getattr(session, "mentor_resolution_proof_file", None):
        return None
    return f"https://{S3_BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{session.mentor_resolution_proof_file}"


def _issue_resolution_feedback_proof_file_url(session) -> Optional[str]:
    if not getattr(session, "issue_resolution_feedback_proof_file", None):
        return None
    return f"https://{S3_BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{session.issue_resolution_feedback_proof_file}"


def _get_issue_resolution_feedback(db: Session, counseling_id: str) -> List:
    from app.schemas.counseling import IssueResolutionFeedbackRow
    order = ["issue_raised", "details_of_resolution", "resolution"]
    rows = db.query(CounselingIssueResolutionFeedback).filter(
        CounselingIssueResolutionFeedback.counseling_id == counseling_id
    ).all()
    by_type = {r.row_type: r for r in rows}
    out = []
    for row_type in order:
        r = by_type.get(row_type)
        out.append(IssueResolutionFeedbackRow(
            row_type=row_type,
            description=r.description if r else None,
            feedback_date=r.feedback_date if r else None,
            status=r.status if r else None,
        ))
    return out


@router.post("/counseling/request", response_model=CounselingSessionResponse)
async def request_counseling_session(
    counseling_data: CounselingSessionCreate,
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Request a new counseling session with assigned mentor
    """
    student_usn = current_student.get("student_usn")
    
    # Get student details
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if not student.assigned_mentor:
        raise HTTPException(status_code=400, detail="No mentor assigned to this student")
    
    # Debug: Log the received session_date
    print(f"Received session_date: {counseling_data.session_date}")
    print(f"Session_date type: {type(counseling_data.session_date)}")
    print(f"Session_date tzinfo: {counseling_data.session_date.tzinfo}")
    
    # Normalize datetime to UTC for consistent comparison (always convert to true UTC)
    session_date_utc = counseling_data.session_date
    if session_date_utc.tzinfo is not None:
        session_date_utc = session_date_utc.astimezone(timezone.utc).replace(tzinfo=None)
    
    # Validate session date is in the future
    if not GoogleMeetService.validate_meeting_time(session_date_utc):
        raise HTTPException(status_code=400, detail="Session date must be in the future")
    
    # Generate counseling ID
    counseling_id = GoogleMeetService.generate_counseling_id()
    
    # Create Google Meet link
    meet_details = GoogleMeetService.create_working_google_meet_link()
    
    # Set default venue if not provided (since Google Meet link is created, default to "Online")
    venue = counseling_data.venue if counseling_data.venue else "Online"
    
    # Create counseling session
    counseling_session = CounselingSession(
        counseling_id=counseling_id,
        student_usn=student_usn,
        mentor_id=student.assigned_mentor,
        session_date=session_date_utc,
        venue=venue,
        reason=counseling_data.reason,
        google_meet_link=meet_details["meeting_link"],
        meeting_id=meet_details["meeting_id"],
        is_urgent=counseling_data.is_urgent,
        status="scheduled"
    )
    
    db.add(counseling_session)
    db.commit()
    db.refresh(counseling_session)
    
    # Get mentor details for response
    mentor = db.query(Mentor).filter(Mentor.mentor_id == student.assigned_mentor).first()
    
    # Send email notification to student
    try:
        # Format session date for email
        formatted_date = session_date_utc.strftime("%B %d, %Y at %I:%M %p")
        
        # Create email content
        email_subject = f"Counseling Session Scheduled - {counseling_id}"
        
        email_body = f"""
        <h2 style="color: #2c3e50; margin-bottom: 20px;">Counseling Session Confirmation</h2>
        
        <p>Dear {student.student_name},</p>
        
        <p>Your counseling session has been successfully scheduled. Here are the details:</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #2c3e50; margin-top: 0;">Session Details</h3>
            <p><strong>Session ID:</strong> {counseling_id}</p>
            <p><strong>Date & Time:</strong> {formatted_date}</p>
            <p><strong>Reason:</strong> {counseling_data.reason}</p>
            <p><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">Scheduled</span></p>
            {f'<p><strong>Priority:</strong> <span style="color: #dc3545; font-weight: bold;">URGENT</span></p>' if counseling_data.is_urgent else ''}
        </div>
        
        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #2c3e50; margin-top: 0;">Mentor Information</h3>
            <p><strong>Mentor:</strong> {mentor.mentor_name if mentor else 'Not Available'}</p>
            <p><strong>Email:</strong> {mentor.mentor_email if mentor else 'Not Available'}</p>
            <p><strong>Phone:</strong> {mentor.mentor_phoneno if mentor else 'Not Available'}</p>
        </div>
        
        {f'''
        <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
            <h3 style="color: #856404; margin-top: 0;">Google Meet Link</h3>
            <p><strong>Meeting Link:</strong> <a href="{counseling_session.google_meet_link}" style="color: #007bff;">{counseling_session.google_meet_link}</a></p>
            <p><strong>Meeting ID:</strong> {counseling_session.meeting_id}</p>
            <p style="font-size: 14px; color: #6c757d; margin-bottom: 0;"><em>Note: This is a generated link. If the meeting doesn't exist, please contact your mentor.</em></p>
        </div>
        ''' if counseling_session.google_meet_link else ''}
        
        <div style="background: #d1ecf1; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #0c5460; margin-top: 0;">Important Notes</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li>Please arrive on time for your counseling session</li>
                <li>If you need to reschedule or cancel, please contact your mentor directly</li>
                <li>Bring any relevant documents or materials related to your concern</li>
                <li>For urgent matters, contact your mentor immediately</li>
            </ul>
        </div>
        
        <p>If you have any questions or need to make changes to your session, please contact your mentor or the administration.</p>
        
        <p>Best regards,<br>
        <strong>Mentee Tracker Team</strong></p>
        """
        
        # Send email
        send_email(student.student_email, email_subject, email_body)
        print(f"Email sent successfully to {student.student_email} for counseling session {counseling_id}")
        
    except Exception as e:
        print(f"Failed to send email to {student.student_email}: {e}")
        # Don't raise exception here as the counseling session was already created successfully

    # Send email to mentor about new student support request
    try:
        if mentor and mentor.mentor_email:
            formatted_date = session_date_utc.strftime("%B %d, %Y at %I:%M %p")
            mentor_subject = f"New Student Support Request – {counseling_id}"
            mentor_body = f"""
            <h2 style="color: #2c3e50; margin-bottom: 20px;">New Student Support Request</h2>
            <p>A student has requested a Student Support session. Please review and take action in the Mentee Tracker Student Support dashboard.</p>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Request Details</h3>
                <p><strong>Session ID:</strong> {counseling_id}</p>
                <p><strong>Student Name:</strong> {student.student_name or 'N/A'}</p>
                <p><strong>Student USN:</strong> {student_usn}</p>
                <p><strong>Requested Date & Time:</strong> {formatted_date}</p>
                <p><strong>Venue:</strong> {venue}</p>
                <p><strong>Reason:</strong> {counseling_data.reason}</p>
                {f'<p><strong>Priority:</strong> <span style="color: #dc3545; font-weight: bold;">URGENT</span></p>' if counseling_data.is_urgent else ''}
            </div>
            <p>You can conduct the session or refer the student to a specialist from the Student Support dashboard.</p>
            <p>Best regards,<br><strong>Mentee Tracker Team</strong></p>
            """
            send_email(mentor.mentor_email, mentor_subject, mentor_body)
            print(f"Email sent to mentor {mentor.mentor_email} for new request {counseling_id}")
    except Exception as e:
        print(f"Failed to send email to mentor: {e}")
    
    return CounselingSessionResponse(
        id=counseling_session.id,
        counseling_id=counseling_session.counseling_id,
        student_usn=counseling_session.student_usn,
        mentor_id=counseling_session.mentor_id,
        session_date=counseling_session.session_date,
        venue=counseling_session.venue,
        reason=counseling_session.reason,
        status=counseling_session.status,
        google_meet_link=counseling_session.google_meet_link,
        meeting_id=counseling_session.meeting_id,
        notes=counseling_session.notes,
        feedback=counseling_session.feedback,
        is_urgent=counseling_session.is_urgent,
        created_at=counseling_session.created_at,
        updated_at=counseling_session.updated_at,
        referred_to_name=getattr(counseling_session, "referred_to_name", None),
        referred_to_contact=getattr(counseling_session, "referred_to_contact", None),
        referred_at=getattr(counseling_session, "referred_at", None),
        student_feedback=getattr(counseling_session, "student_feedback", None),
        student_rating=getattr(counseling_session, "student_rating", None),
        student_feedback_date=getattr(counseling_session, "student_feedback_date", None),
        student_feedback_file_url=_student_feedback_file_url(counseling_session),
        mentor_feedback=getattr(counseling_session, "mentor_feedback", None),
        mentor_rating=getattr(counseling_session, "mentor_rating", None),
        mentor_feedback_date=getattr(counseling_session, "mentor_feedback_date", None),
        mentor_feedback_file_url=_mentor_feedback_file_url(counseling_session),
        student_issues_proof_file_url=_student_issues_proof_file_url(counseling_session),
        mentor_resolution_proof_file_url=_mentor_resolution_proof_file_url(counseling_session),
        issue_resolution_feedback=_get_issue_resolution_feedback(db, counseling_session.counseling_id),
        issue_resolution_feedback_proof_file_url=_issue_resolution_feedback_proof_file_url(counseling_session),
        student_name=student.student_name,
        student_email=student.student_email,
        student_phoneno=student.student_phoneno,
        mentor_name=mentor.mentor_name if mentor else None,
        mentor_email=mentor.mentor_email if mentor else None,
        mentor_phoneno=mentor.mentor_phoneno if mentor else None
    )

@router.get("/counseling/sessions", response_model=List[CounselingSessionResponse])
async def get_my_counseling_sessions(
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, description="Number of sessions to return"),
    offset: int = Query(0, description="Number of sessions to skip")
):
    """
    Get all counseling sessions for the current student
    """
    student_usn = current_student.get("student_usn")
    
    query = db.query(CounselingSession).filter(CounselingSession.student_usn == student_usn)
    
    if status:
        query = query.filter(CounselingSession.status == status)
    
    sessions = query.order_by(CounselingSession.session_date.desc()).offset(offset).limit(limit).all()
    
    result = []
    for session in sessions:
        # Get mentor details
        mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
        
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
            mentor_name=mentor.mentor_name if mentor else None,
            mentor_email=mentor.mentor_email if mentor else None,
            mentor_phoneno=mentor.mentor_phoneno if mentor else None
        ))

    return result

@router.get("/counseling/sessions/{counseling_id}", response_model=CounselingSessionResponse)
async def get_counseling_session(
    counseling_id: str,
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific counseling session
    """
    student_usn = current_student.get("student_usn")
    
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.student_usn == student_usn
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    # Get mentor details
    mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
    
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
        mentor_name=mentor.mentor_name if mentor else None,
        mentor_email=mentor.mentor_email if mentor else None,
        mentor_phoneno=mentor.mentor_phoneno if mentor else None
    )

@router.put("/counseling/sessions/{counseling_id}", response_model=CounselingSessionResponse)
async def update_counseling_session(
    counseling_id: str,
    update_data: CounselingSessionUpdate,
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Update a counseling session (only if status is scheduled)
    """
    student_usn = current_student.get("student_usn")
    
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.student_usn == student_usn
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    if session.status != "scheduled":
        raise HTTPException(status_code=400, detail="Only scheduled sessions can be updated")
    
    # Update fields
    if update_data.session_date:
        # Always treat incoming datetime as UTC for validation and storage
        session_date_utc = update_data.session_date
        if session_date_utc.tzinfo is not None:
            session_date_utc = session_date_utc.astimezone(timezone.utc).replace(tzinfo=None)
        if not GoogleMeetService.validate_meeting_time(session_date_utc):
            raise HTTPException(status_code=400, detail="Session date must be in the future")
        session.session_date = session_date_utc
    
    if update_data.venue:
        session.venue = update_data.venue
    
    if update_data.reason:
        session.reason = update_data.reason
    
    if update_data.status:
        session.status = update_data.status
    
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    # Get mentor details
    mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
    
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
        mentor_name=mentor.mentor_name if mentor else None,
        mentor_email=mentor.mentor_email if mentor else None,
        mentor_phoneno=mentor.mentor_phoneno if mentor else None
    )

@router.get("/counseling/stats", response_model=CounselingStats)
async def get_counseling_stats(
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get counseling statistics for the current student
    """
    student_usn = current_student.get("student_usn")
    
    total_sessions = db.query(CounselingSession).filter(CounselingSession.student_usn == student_usn).count()
    scheduled_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.student_usn == student_usn,
            CounselingSession.status == "scheduled"
        )
    ).count()
    completed_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.student_usn == student_usn,
            CounselingSession.status == "completed"
        )
    ).count()
    cancelled_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.student_usn == student_usn,
            CounselingSession.status == "cancelled"
        )
    ).count()
    
    # Get current time for comparison
    now = datetime.utcnow()
    
    # Upcoming sessions (scheduled and in the future)
    upcoming_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.student_usn == student_usn,
            CounselingSession.status == "scheduled",
            CounselingSession.session_date > now
        )
    ).count()
    
    urgent_sessions = db.query(CounselingSession).filter(
        and_(
            CounselingSession.student_usn == student_usn,
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

ALLOWED_FEEDBACK_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg", "gif", "webp"}
MAX_FEEDBACK_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/counseling/sessions/{counseling_id}/feedback", response_model=FeedbackResponse)
async def submit_student_feedback(
    counseling_id: str,
    feedback: str = Form(..., description="Student feedback text"),
    rating: int = Form(..., ge=1, le=5, description="Rating 1-5"),
    file: Optional[UploadFile] = File(None, description="Optional file attachment"),
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a completed counseling session (student). Optional file upload.
    """
    student_usn = current_student.get("student_usn")

    # Get the counseling session
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.student_usn == student_usn
        )
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")

    # Allow student feedback for completed or referred sessions
    if session.status not in ("completed", "referred"):
        raise HTTPException(
            status_code=400,
            detail="Feedback can only be submitted for referred or completed sessions",
        )

    if session.student_feedback:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this session")

    session.student_feedback = feedback.strip()
    session.student_rating = rating
    session.student_feedback_date = datetime.utcnow()
    feedback_file_key = None

    if file and file.filename and file.filename.strip():
        ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
        if ext not in ALLOWED_FEEDBACK_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_FEEDBACK_EXTENSIONS))}"
            )
        content = await file.read()
        if len(content) > MAX_FEEDBACK_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size must be under 10 MB")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        feedback_file_key = f"counseling-feedback/{student_usn}/{counseling_id}_{timestamp}.{ext}"
        try:
            s3_client.upload_fileobj(
                __import__("io").BytesIO(content),
                S3_BUCKET_NAME,
                feedback_file_key,
                ExtraArgs={"ContentType": file.content_type or "application/octet-stream"}
            )
            session.student_feedback_file = feedback_file_key
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    db.commit()
    db.refresh(session)
    
    # Send email notification to mentor about feedback
    try:
        mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
        student = db.query(Student).filter(Student.student_usn == student_usn).first()
        
        if mentor and mentor.mentor_email:
            email_subject = f"Student Feedback Received - {counseling_id}"
            
            email_body = f"""
            <h2 style="color: #2c3e50; margin-bottom: 20px;">Student Feedback Received</h2>
            
            <p>Dear {mentor.mentor_name if mentor else 'Mentor'},</p>
            
            <p>You have received feedback from a student for your counseling session:</p>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Session Details</h3>
                <p><strong>Session ID:</strong> {counseling_id}</p>
                <p><strong>Student:</strong> {student.student_name if student else 'Unknown'}</p>
                <p><strong>Date:</strong> {session.session_date.strftime("%B %d, %Y at %I:%M %p")}</p>
                <p><strong>Rating:</strong> {'⭐' * rating} ({rating}/5)</p>
            </div>
            
            <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Student Feedback</h3>
                <p style="font-style: italic;">"{feedback}"</p>
            </div>
            
            <p>Thank you for your dedication to student counseling!</p>
            
            <p>Best regards,<br>
            <strong>Mentee Tracker Team</strong></p>
            """
            
            send_email(mentor.mentor_email, email_subject, email_body)
            print(f"Feedback notification email sent to mentor {mentor.mentor_email}")
            
    except Exception as e:
        print(f"Failed to send feedback notification email: {e}")
    
    return FeedbackResponse(
        success=True,
        message="Feedback submitted successfully",
        feedback_id=counseling_id
    )

@router.get("/counseling/sessions/{counseling_id}/feedback")
async def get_session_feedback(
    counseling_id: str,
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get feedback for a specific counseling session
    """
    student_usn = current_student.get("student_usn")
    
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.student_usn == student_usn
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    def _feedback_file_url(s):
        if not getattr(s, "student_feedback_file", None):
            return None
        return f"https://{S3_BUCKET_NAME}.s3.{s3_client.meta.region_name}.amazonaws.com/{s.student_feedback_file}"

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
        "can_submit_feedback": session.status in ("completed", "referred") and not session.student_feedback
    }


@router.post("/counseling/sessions/{counseling_id}/issues-resolution", response_model=List[IssueResolutionResponse])
async def submit_issues_resolution(
    counseling_id: str,
    rows: str = Form(..., description="JSON array of issues-resolution rows"),
    file: Optional[UploadFile] = File(None, description="Optional proof file (PDF, images, etc.)"),
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Submit Details of Issues Raised & Resolved for a completed session (student).
    Replaces any existing rows. Optional proof file for work done after session.
    """
    student_usn = current_student.get("student_usn")
    try:
        data = IssuesResolutionSubmit(rows=json.loads(rows))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid rows JSON: {str(e)}")
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.student_usn == student_usn
        )
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    # Allow student to submit this form only for completed or referred sessions
    if session.status not in ("completed", "referred"):
        raise HTTPException(
            status_code=400,
            detail="Issues & resolution can only be submitted for referred or completed sessions",
        )
    # Delete existing rows for this session
    db.query(SessionIssuesResolution).filter(SessionIssuesResolution.counseling_id == counseling_id).delete()
    # Insert new rows
    for idx, row in enumerate(data.rows, start=1):
        rec = SessionIssuesResolution(
            counseling_id=counseling_id,
            serial_no=idx,
            issues_raised=row.issues_raised,
            date_issue_raised=row.date_issue_raised,
            resolution_details=row.resolution_details if row.resolution_details else None,
            date_resolution_provided=row.date_resolution_provided or None,
        )
        db.add(rec)
    # Optional proof file upload
    if file and file.filename and file.filename.strip():
        ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
        if ext not in ALLOWED_FEEDBACK_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Proof file type not allowed. Allowed: {', '.join(sorted(ALLOWED_FEEDBACK_EXTENSIONS))}"
            )
        content = await file.read()
        if len(content) > MAX_FEEDBACK_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Proof file must be under 10 MB")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        proof_key = f"counseling-issues-proof/{student_usn}/{counseling_id}_{timestamp}.{ext}"
        try:
            s3_client.upload_fileobj(
                __import__("io").BytesIO(content),
                S3_BUCKET_NAME,
                proof_key,
                ExtraArgs={"ContentType": file.content_type or "application/octet-stream"}
            )
            session.student_issues_proof_file = proof_key
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload proof file: {str(e)}")
    db.commit()
    db.refresh(session)
    # Return all rows for this session
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


@router.get("/counseling/sessions/{counseling_id}/issues-resolution", response_model=List[IssueResolutionResponse])
async def get_issues_resolution(
    counseling_id: str,
    current_student: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get Details of Issues Raised & Resolved for a session (student).
    """
    student_usn = current_student.get("student_usn")
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.student_usn == student_usn
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
