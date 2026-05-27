from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.attendance import AttendanceSession, Attendance
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.database import get_db
from app.schemas.attendance import (
    QRCodeScanRequest,
    AttendanceMarkRequest,
    AttendanceResponse,
    AttendanceRecordResponse
)
from app.services.email_services import send_email
from datetime import datetime, timezone, timedelta
from typing import List
import json
import pytz

router = APIRouter()

@router.post("/attendance/scan-qr", response_model=AttendanceResponse)
def scan_qr_code(
    student_usn: str,
    scan_request: QRCodeScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Scan QR code and mark attendance"""
    print(f"\n{'='*60}")
    print(f"=== ATTENDANCE SCAN REQUEST RECEIVED ===")
    print(f"{'='*60}")
    print(f"Timestamp: {datetime.now()}")
    print(f"Student USN (path): {student_usn}")
    print(f"Session ID: {scan_request.session_id}")
    print(f"Student USN (body): {scan_request.student_usn}")
    print(f"Request Body: {scan_request}")
    print(f"{'='*60}\n")
    
    # Verify student exists
    print("Step 0: Verifying student exists...")
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        print(f"✗ Student not found: {student_usn}")
        raise HTTPException(status_code=404, detail="Student not found")
    print(f"✓ Student found: {student.student_name} ({student.student_usn})")
    
    # Verify the session_id matches the student_usn from request
    if scan_request.student_usn != student_usn:
        print(f"✗ Student USN mismatch: path={student_usn}, body={scan_request.student_usn}")
        raise HTTPException(status_code=403, detail="Unauthorized: Student USN mismatch")
    print("✓ Student USN matches")
    
    # Get the attendance session
    print(f"Step 0.5: Looking up attendance session: {scan_request.session_id}")
    session = db.query(AttendanceSession).filter(
        AttendanceSession.session_id == scan_request.session_id
    ).first()
    
    if not session:
        print(f"✗ Session not found: {scan_request.session_id}")
        raise HTTPException(status_code=404, detail="Invalid QR code: Session not found")
    print(f"✓ Session found: {session.session_name} (ID: {session.session_id})")
    print(f"  - Mentor ID: {session.mentor_id}")
    print(f"  - Is Active: {session.is_active}")
    print(f"  - Expires At: {session.expires_at}")
    
    # Check if session is active
    if not session.is_active:
        print(f"✗ Session is not active")
        raise HTTPException(status_code=400, detail="This attendance session has been deactivated")
    print("✓ Session is active")
    
    # Check if session has expired (compare IST times using timezone-aware datetimes)
    ist_tz = pytz.timezone('Asia/Kolkata')
    current_ist = datetime.now(ist_tz)  # Keep timezone-aware
    
    # Get expires_at from database and make it timezone-aware (treat as IST)
    expires_at_naive = session.expires_at  # This is naive datetime from DB
    # Localize naive datetime to IST, or use as-is if already timezone-aware
    if expires_at_naive.tzinfo is None:
        expires_at_ist = ist_tz.localize(expires_at_naive)  # Treat it as IST
    else:
        expires_at_ist = expires_at_naive.astimezone(ist_tz)  # Convert to IST if already aware
    
    # Now compare timezone-aware datetimes
    if current_ist > expires_at_ist:
        raise HTTPException(status_code=400, detail="This QR code has expired")
    
    # Check if student has already marked attendance for this session
    existing_attendance = db.query(Attendance).filter(
        Attendance.session_id == scan_request.session_id,
        Attendance.student_usn == student_usn
    ).first()
    
    if existing_attendance:
        print(f"Attendance already exists for student {student_usn} and session {scan_request.session_id}")
        raise HTTPException(status_code=400, detail="Attendance already marked for this session")
    
    print(f"No existing attendance found. Creating new record...")
    
    # Get current time in IST and store as naive datetime (database doesn't store timezone)
    ist_tz = pytz.timezone('Asia/Kolkata')
    current_ist = datetime.now(ist_tz)
    # Convert to naive datetime for database storage (removes timezone info, keeps IST time)
    marked_at_ist = current_ist.replace(tzinfo=None)
    
    # Create attendance record
    print(f"Creating attendance record with data:")
    print(f"  - session_id: {scan_request.session_id}")
    print(f"  - student_usn: {student_usn}")
    print(f"  - mentor_id: {session.mentor_id}")
    print(f"  - status: present")
    print(f"  - marked_at: {marked_at_ist}")
    
    attendance = Attendance(
        session_id=scan_request.session_id,
        student_usn=student_usn,
        mentor_id=session.mentor_id,
        status="present",
        marked_at=marked_at_ist
    )
    
    try:
        print("Step 1: Adding attendance object to session...")
        db.add(attendance)
        print("✓ Attendance object added to session")
        
        print("Step 2: Flushing to database (without commit)...")
        # Flush to get the ID before commit (helps with debugging)
        db.flush()
        attendance_id_before_commit = attendance.id if hasattr(attendance, 'id') and attendance.id else None
        print(f"✓ Flushed to database. Attendance ID: {attendance_id_before_commit}")
        
        print("Step 3: Committing transaction to database...")
        # Commit the transaction - THIS IS CRITICAL
        db.commit()
        print("✓✓✓ Transaction COMMITTED successfully ✓✓✓")
        
        print("Step 4: Refreshing attendance object to get final state...")
        # Refresh to get the final ID and ensure data is persisted
        db.refresh(attendance)
        print(f"✓ Attendance object refreshed")
        print(f"  - ID: {attendance.id}")
        print(f"  - Session: {attendance.session_id}")
        print(f"  - Student: {attendance.student_usn}")
        print(f"  - Marked At: {attendance.marked_at}")
        
        print("Step 5: Verifying record exists in database with fresh query...")
        # Force a new query to verify the commit actually persisted
        db.expire_all()  # Clear session cache to force fresh query
        
        # Verify the record was actually saved by querying it back
        verify_attendance = db.query(Attendance).filter(
            Attendance.session_id == scan_request.session_id,
            Attendance.student_usn == student_usn
        ).first()
        
        if verify_attendance:
            print(f"✓✓✓ VERIFICATION PASSED: Attendance record confirmed in database ✓✓✓")
            print(f"  - Verified ID: {verify_attendance.id}")
            print(f"  - Verified Session: {verify_attendance.session_id}")
            print(f"  - Verified Student: {verify_attendance.student_usn}")
            print(f"  - Verified Marked At: {verify_attendance.marked_at}")
            # Use verified record for response to ensure we have the actual database record
            attendance = verify_attendance
        else:
            print(f"✗✗✗ CRITICAL ERROR: Attendance record NOT FOUND in database after commit! ✗✗✗")
            print(f"  - Session ID searched: {scan_request.session_id}")
            print(f"  - Student USN searched: {student_usn}")
            print(f"  - Attendance ID from object: {attendance.id if hasattr(attendance, 'id') else 'N/A'}")
            
            # Try one more time with a small delay (in case of replication lag)
            import time
            print("Retrying verification after 0.5 second delay...")
            time.sleep(0.5)
            verify_attendance_retry = db.query(Attendance).filter(
                Attendance.session_id == scan_request.session_id,
                Attendance.student_usn == student_usn
            ).first()
            if verify_attendance_retry:
                print(f"✓ Record found on retry: ID={verify_attendance_retry.id}")
                attendance = verify_attendance_retry
            else:
                print(f"✗✗✗ Record still not found after retry - COMMIT FAILED! ✗✗✗")
                # Rollback any pending changes
                db.rollback()
                raise HTTPException(status_code=500, detail="Attendance record was not saved to database. The commit may have failed silently. Please try again.")
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as commit_error:
        db.rollback()
        error_type = type(commit_error).__name__
        error_message = str(commit_error)
        print(f"✗ ERROR committing attendance record:")
        print(f"  Error Type: {error_type}")
        print(f"  Error Message: {error_message}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        
        # Provide more specific error messages
        if "Duplicate entry" in error_message or "UNIQUE constraint" in error_message:
            raise HTTPException(status_code=400, detail="Attendance already marked for this session")
        elif "Foreign key constraint" in error_message or "Cannot add or update" in error_message:
            raise HTTPException(status_code=400, detail="Invalid session or student reference")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to save attendance record: {error_message}")
    
    # Get mentor information for email
    mentor = db.query(Mentor).filter(Mentor.mentor_id == session.mentor_id).first()
    
    # Send email notification to student
    if student and student.student_email:
        try:
            # Format the marked_at datetime for email (already stored as IST, just format it)
            # Since marked_at is stored as IST (naive), we need to treat it as IST
            ist_tz = pytz.timezone('Asia/Kolkata')
            # Convert naive datetime to IST-aware datetime
            marked_at_ist = ist_tz.localize(attendance.marked_at)
            marked_at_formatted = marked_at_ist.strftime("%B %d, %Y at %I:%M %p IST")
            
            email_subject = f"Attendance Marked Successfully - {session.session_name or 'Session'}"
            
            email_body = f"""
            <h2 style="color: #4caf50; margin-bottom: 20px;">✓ Attendance Confirmed</h2>
            
            <p>Dear <strong>{student.student_name or student_usn}</strong>,</p>
            
            <p>Your attendance has been successfully marked for the following session:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Session Name:</strong> {session.session_name or 'N/A'}</p>
                <p style="margin: 5px 0;"><strong>Session ID:</strong> {session.session_id}</p>
                <p style="margin: 5px 0;"><strong>Mentor:</strong> {mentor.mentor_name if mentor else 'N/A'}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: #4caf50; font-weight: bold;">Present</span></p>
                <p style="margin: 5px 0;"><strong>Marked At:</strong> {marked_at_formatted}</p>
                <p style="margin: 5px 0;"><strong>Location:</strong> {session.location or 'N/A'}</p>
            </div>
            
            <p style="margin-top: 20px;">Your attendance record has been updated in the system. If you have any questions or concerns, please contact your mentor.</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                <p style="font-size: 14px; color: #666;">
                    <strong>Mentor Contact Information:</strong><br>
                    {f'Name: {mentor.mentor_name}<br>Email: {mentor.mentor_email}<br>Phone: {mentor.mentor_phoneno}' if mentor else 'Contact information not available'}
                </p>
            </div>
            
            <p style="margin-top: 20px;">Thank you for your participation!</p>
            """
            
            # Define email sending function with error handling
            def send_attendance_email():
                try:
                    result = send_email(student.student_email, email_subject, email_body)
                    if result:
                        print(f"✓ Attendance confirmation email sent successfully to {student.student_email}")
                    else:
                        print(f"✗ Failed to send attendance confirmation email to {student.student_email}")
                except Exception as e:
                    print(f"✗ Exception while sending attendance email to {student.student_email}: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
            
            # Send email in background
            background_tasks.add_task(send_attendance_email)
            print(f"Attendance confirmation email queued for {student.student_email}")
            
        except Exception as e:
            print(f"Failed to prepare attendance confirmation email for {student.student_email}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # Don't fail the request if email fails
    
    # Final verification - query database directly to ensure record exists
    print("Performing final database verification before returning response...")
    db.expire_all()  # Clear all cached objects
    final_check = db.query(Attendance).filter(
        Attendance.session_id == scan_request.session_id,
        Attendance.student_usn == student_usn
    ).first()
    
    if not final_check:
        print("✗ CRITICAL ERROR: Record not found in database after all operations!")
        print("This indicates the commit may have failed silently or was rolled back.")
        raise HTTPException(status_code=500, detail="Attendance record was not saved to database. Please try again.")
    
    print(f"✓ Final verification passed: Record ID={final_check.id} exists in database")
    
    response_data = AttendanceResponse(
        id=final_check.id,  # Use verified record ID
        session_id=final_check.session_id,
        student_usn=final_check.student_usn,
        mentor_id=final_check.mentor_id,
        marked_at=final_check.marked_at,
        status=final_check.status,
        notes=final_check.notes
    )
    
    print(f"=== Attendance Record Created Successfully ===")
    print(f"ID: {response_data.id}")
    print(f"Session ID: {response_data.session_id}")
    print(f"Student USN: {response_data.student_usn}")
    print(f"Mentor ID: {response_data.mentor_id}")
    print(f"Status: {response_data.status}")
    print(f"Marked At: {response_data.marked_at}")
    print(f"Response will be returned to client")
    print(f"=============================================")
    
    return response_data

@router.post("/attendance/mark", response_model=AttendanceResponse)
def mark_attendance(
    student_usn: str,
    attendance_request: AttendanceMarkRequest,
    db: Session = Depends(get_db)
):
    """Manually mark attendance (alternative to QR scan)"""
    # Verify student exists
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get the attendance session
    session = db.query(AttendanceSession).filter(
        AttendanceSession.session_id == attendance_request.session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if session is active
    if not session.is_active:
        raise HTTPException(status_code=400, detail="This attendance session has been deactivated")
    
    # Check if student has already marked attendance for this session
    existing_attendance = db.query(Attendance).filter(
        Attendance.session_id == attendance_request.session_id,
        Attendance.student_usn == student_usn
    ).first()
    
    if existing_attendance:
        # Update existing attendance
        existing_attendance.status = attendance_request.status
        existing_attendance.notes = attendance_request.notes
        # Get current time in IST
        ist_tz = pytz.timezone('Asia/Kolkata')
        current_ist = datetime.now(ist_tz).replace(tzinfo=None)
        existing_attendance.marked_at = current_ist
        db.commit()
        db.refresh(existing_attendance)
        
        return AttendanceResponse(
            id=existing_attendance.id,
            session_id=existing_attendance.session_id,
            student_usn=existing_attendance.student_usn,
            mentor_id=existing_attendance.mentor_id,
            marked_at=existing_attendance.marked_at,
            status=existing_attendance.status,
            notes=existing_attendance.notes
        )
    
    # Create new attendance record
    attendance = Attendance(
        session_id=attendance_request.session_id,
        student_usn=student_usn,
        mentor_id=session.mentor_id,
        status=attendance_request.status,
        notes=attendance_request.notes,
        marked_at=datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return AttendanceResponse(
        id=attendance.id,
        session_id=attendance.session_id,
        student_usn=attendance.student_usn,
        mentor_id=attendance.mentor_id,
        marked_at=attendance.marked_at,
        status=attendance.status,
        notes=attendance.notes
    )


@router.get("/attendance/stats")
def get_student_attendance_stats(student_usn: str, db: Session = Depends(get_db)):
    """Dashboard stats for a student: total records, present/absent/late counts, this week present."""
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    total_records = db.query(func.count(Attendance.id)).filter(
        Attendance.student_usn == student_usn
    ).scalar() or 0

    present_count = db.query(func.count(Attendance.id)).filter(
        Attendance.student_usn == student_usn,
        func.lower(Attendance.status) == "present",
    ).scalar() or 0
    absent_count = db.query(func.count(Attendance.id)).filter(
        Attendance.student_usn == student_usn,
        func.lower(Attendance.status) == "absent",
    ).scalar() or 0
    late_count = db.query(func.count(Attendance.id)).filter(
        Attendance.student_usn == student_usn,
        func.lower(Attendance.status) == "late",
    ).scalar() or 0

    ist_tz = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist_tz).replace(tzinfo=None)
    today = now_ist.date() if hasattr(now_ist, "date") else now_ist
    if hasattr(today, "weekday"):
        days_since_monday = today.weekday()
    else:
        days_since_monday = 0
    week_start = datetime.combine(
        today - timedelta(days=days_since_monday),
        datetime.min.time()
    )
    week_end = week_start + timedelta(days=7)

    this_week_present = db.query(func.count(Attendance.id)).filter(
        Attendance.student_usn == student_usn,
        Attendance.marked_at >= week_start,
        Attendance.marked_at < week_end,
        func.lower(Attendance.status) == "present",
    ).scalar() or 0

    return {
        "total_records": total_records,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "this_week_present": this_week_present,
    }


@router.get("/attendance/my-records", response_model=List[AttendanceRecordResponse])
def get_my_attendance_records(
    student_usn: str,
    db: Session = Depends(get_db)
):
    """Get all attendance records for a student"""
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all attendance records for this student
    attendance_records = db.query(Attendance).filter(
        Attendance.student_usn == student_usn
    ).order_by(Attendance.marked_at.desc()).all()
    
    # Join with session table to get session names
    records_response = []
    for record in attendance_records:
        session = db.query(AttendanceSession).filter(
            AttendanceSession.session_id == record.session_id
        ).first()
        
        records_response.append(AttendanceRecordResponse(
            id=record.id,
            session_id=record.session_id,
            student_usn=record.student_usn,
            student_name=student.student_name,
            mentor_id=record.mentor_id,
            marked_at=record.marked_at,
            status=record.status,
            notes=record.notes,
            session_name=session.session_name if session else None
        ))
    
    return records_response

@router.get("/attendance/check-session/{session_id}")
def check_session_validity(
    student_usn: str,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Check if a session is valid and if student has already marked attendance"""
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    session = db.query(AttendanceSession).filter(
        AttendanceSession.session_id == session_id
    ).first()
    
    if not session:
        return {
            "valid": False,
            "message": "Session not found",
            "already_marked": False
        }
    
    # Check if already marked
    existing_attendance = db.query(Attendance).filter(
        Attendance.session_id == session_id,
        Attendance.student_usn == student_usn
    ).first()
    
    # Compare IST times using timezone-aware datetimes
    ist_tz = pytz.timezone('Asia/Kolkata')
    current_ist = datetime.now(ist_tz)  # Keep timezone-aware
    
    # Get expires_at from database and make it timezone-aware (treat as IST)
    expires_at_naive = session.expires_at  # This is naive datetime from DB
    # Localize naive datetime to IST, or use as-is if already timezone-aware
    if expires_at_naive.tzinfo is None:
        expires_at_ist = ist_tz.localize(expires_at_naive)  # Treat it as IST
    else:
        expires_at_ist = expires_at_naive.astimezone(ist_tz)  # Convert to IST if already aware
    
    # Now compare timezone-aware datetimes
    is_valid = (
        session.is_active and
        current_ist <= expires_at_ist
    )
    
    return {
        "valid": is_valid,
        "message": "Session is valid" if is_valid else "Session is expired or inactive",
        "already_marked": existing_attendance is not None,
        "session_name": session.session_name,
        "expires_at": session.expires_at.isoformat()
    }



