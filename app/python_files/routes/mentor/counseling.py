from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.db.database import get_db
from app.db.models.counseling import CounselingSession, CounselingAvailability
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.schemas.counseling import (
    CounselingSessionResponse, 
    CounselingSessionUpdate,
    CounselingAvailabilityCreate,
    CounselingAvailabilityResponse,
    CounselingStats,
    MentorFeedbackSubmit,
    FeedbackResponse
)
from app.core.dependencies import get_current_mentor
from app.services.email_services import send_email
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

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
        session.status = update_data.status
    
    if update_data.notes:
        session.notes = update_data.notes
    
    if update_data.feedback:
        session.feedback = update_data.feedback
    
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    # Get student details
    student = db.query(Student).filter(Student.student_usn == session.student_usn).first()
    
    # Send email notification to student if status changed
    if update_data.status and update_data.status != "scheduled":
        try:
            # Format session date for email
            formatted_date = session.session_date.strftime("%B %d, %Y at %I:%M %p")
            
            # Create email content based on status
            if update_data.status == "completed":
                email_subject = f"Counseling Session Completed - {session.counseling_id}"
                status_color = "#28a745"
                status_text = "Completed"
            elif update_data.status == "cancelled":
                email_subject = f"Counseling Session Cancelled - {session.counseling_id}"
                status_color = "#dc3545"
                status_text = "Cancelled"
            elif update_data.status == "rescheduled":
                email_subject = f"Counseling Session Rescheduled - {session.counseling_id}"
                status_color = "#ffc107"
                status_text = "Rescheduled"
            else:
                email_subject = f"Counseling Session Updated - {session.counseling_id}"
                status_color = "#17a2b8"
                status_text = update_data.status.title()
            
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
                    {f'<li>Your session has been marked as {status_text.lower()}</li>' if update_data.status else ''}
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
            # Don't raise exception here as the session was already updated successfully
    
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
    feedback_data: MentorFeedbackSubmit,
    current_mentor: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a completed counseling session (mentor)
    """
    mentor_id = current_mentor.get("mentor_id")
    
    # Get the counseling session
    session = db.query(CounselingSession).filter(
        and_(
            CounselingSession.counseling_id == counseling_id,
            CounselingSession.mentor_id == mentor_id
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Counseling session not found")
    
    # Check if session is completed
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Feedback can only be submitted for completed sessions")
    
    # Check if feedback already exists
    if session.mentor_feedback:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this session")
    
    # Update session with mentor feedback
    session.mentor_feedback = feedback_data.feedback
    session.mentor_rating = feedback_data.rating
    session.mentor_feedback_date = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    # Send email notification to student about feedback
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
                <p><strong>Rating:</strong> {'⭐' * feedback_data.rating} ({feedback_data.rating}/5)</p>
            </div>
            
            <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Mentor Feedback</h3>
                <p style="font-style: italic;">"{feedback_data.feedback}"</p>
            </div>
            
            <p>We hope this feedback helps you in your academic journey!</p>
            
            <p>Best regards,<br>
            <strong>Mentee Tracker Team</strong></p>
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
        "mentor_feedback": session.mentor_feedback,
        "mentor_rating": session.mentor_rating,
        "mentor_feedback_date": session.mentor_feedback_date,
        "can_submit_feedback": session.status == "completed" and not session.mentor_feedback
    }
