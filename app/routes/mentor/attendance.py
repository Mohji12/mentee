from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.attendance import AttendanceSession, Attendance
from app.db.models.mentors import Mentor
from app.db.models.students import Student
from app.db.database import get_db
from app.schemas.attendance import (
    AttendanceSessionCreate,
    AttendanceSessionResponse,
    AttendanceRecordResponse,
    ManualAttendanceMarkRequest,
    ManualAttendanceBulkRequest
)
from app.utils.id_utils import generate_session_id
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import qrcode
import io
import base64
import json
import pytz

router = APIRouter()

@router.post("/attendance/generate-qr", response_model=AttendanceSessionResponse)
def generate_qr_code(
    mentor_id: str,
    session_data: AttendanceSessionCreate,
    db: Session = Depends(get_db)
):
    """Generate a QR code for attendance session"""
    # Verify mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    # Generate session ID
    session_id = generate_session_id()
    
    # Calculate expiry time in IST and store as naive datetime
    ist_tz = pytz.timezone('Asia/Kolkata')
    expires_at_ist = (datetime.now(ist_tz) + timedelta(minutes=session_data.duration_minutes)).replace(tzinfo=None)
    
    # Create QR code data (JSON with session info)
    # Store IST time in QR code
    qr_data = {
        "session_id": session_id,
        "mentor_id": mentor_id,
        "expires_at": expires_at_ist.isoformat(),  # IST time
        "session_name": session_data.session_name
    }
    qr_data_json = json.dumps(qr_data)
    
    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data_json)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert image to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Create attendance session in database
    attendance_session = AttendanceSession(
        session_id=session_id,
        mentor_id=mentor_id,
        session_name=session_data.session_name,
        qr_code_data=qr_data_json,
        expires_at=expires_at_ist,  # Store IST in database
        is_active=True,
        location=session_data.location
    )
    
    db.add(attendance_session)
    db.commit()
    db.refresh(attendance_session)
    
    # Return response with JSON data (frontend will generate QR code from this)
    response = AttendanceSessionResponse(
        session_id=attendance_session.session_id,
        mentor_id=attendance_session.mentor_id,
        session_name=attendance_session.session_name,
        qr_code_data=qr_data_json,  # JSON string for QR code generation
        created_at=attendance_session.created_at,
        expires_at=attendance_session.expires_at,
        is_active=attendance_session.is_active,
        location=attendance_session.location
    )
    
    return response

@router.get("/attendance/sessions", response_model=List[AttendanceSessionResponse])
def get_attendance_sessions(
    mentor_id: str,
    db: Session = Depends(get_db)
):
    """Get all attendance sessions for a mentor"""
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    sessions = db.query(AttendanceSession).filter(
        AttendanceSession.mentor_id == mentor_id
    ).order_by(AttendanceSession.created_at.desc()).all()
    
    # Convert QR code data to base64 image for each session
    sessions_response = []
    for session in sessions:
        # Generate QR code image from stored data
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(session.qr_code_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        sessions_response.append(AttendanceSessionResponse(
            session_id=session.session_id,
            mentor_id=session.mentor_id,
            session_name=session.session_name,
            qr_code_data=session.qr_code_data,  # JSON string
            created_at=session.created_at,
            expires_at=session.expires_at,
            is_active=session.is_active,
            location=session.location
        ))
    
    return sessions_response


@router.get("/attendance/stats")
def get_attendance_stats(mentor_id: str, db: Session = Depends(get_db)):
    """Dashboard stats: sessions, records, status counts, assigned students. Optional this-week summary."""
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    ist_tz = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist_tz).replace(tzinfo=None)

    total_sessions = db.query(func.count(AttendanceSession.session_id)).filter(
        AttendanceSession.mentor_id == mentor_id
    ).scalar() or 0

    active_sessions = db.query(func.count(AttendanceSession.session_id)).filter(
        AttendanceSession.mentor_id == mentor_id,
        AttendanceSession.is_active == True,
        AttendanceSession.expires_at >= now_ist,
    ).scalar() or 0

    total_records = db.query(func.count(Attendance.id)).filter(
        Attendance.mentor_id == mentor_id
    ).scalar() or 0

    present_count = db.query(func.count(Attendance.id)).filter(
        Attendance.mentor_id == mentor_id,
        func.lower(Attendance.status) == "present",
    ).scalar() or 0
    absent_count = db.query(func.count(Attendance.id)).filter(
        Attendance.mentor_id == mentor_id,
        func.lower(Attendance.status) == "absent",
    ).scalar() or 0
    late_count = db.query(func.count(Attendance.id)).filter(
        Attendance.mentor_id == mentor_id,
        func.lower(Attendance.status) == "late",
    ).scalar() or 0

    assigned_students_count = db.query(func.count(Student.student_usn)).filter(
        Student.assigned_mentor == mentor_id
    ).scalar() or 0

    # Current week (Monday–Sunday) in IST
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

    this_week_records = db.query(func.count(Attendance.id)).filter(
        Attendance.mentor_id == mentor_id,
        Attendance.marked_at >= week_start,
        Attendance.marked_at < week_end,
    ).scalar() or 0

    this_week_present = db.query(func.count(Attendance.id)).filter(
        Attendance.mentor_id == mentor_id,
        Attendance.marked_at >= week_start,
        Attendance.marked_at < week_end,
        func.lower(Attendance.status) == "present",
    ).scalar() or 0

    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_records": total_records,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "assigned_students_count": assigned_students_count,
        "this_week_records": this_week_records,
        "this_week_present": this_week_present,
    }


@router.get("/attendance/records/{session_id}", response_model=List[AttendanceRecordResponse])
def get_attendance_records(
    mentor_id: str,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get attendance records for a specific session"""
    # Verify mentor and session
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    session = db.query(AttendanceSession).filter(
        AttendanceSession.session_id == session_id,
        AttendanceSession.mentor_id == mentor_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all attendance records for this session
    attendance_records = db.query(Attendance).filter(
        Attendance.session_id == session_id
    ).all()
    
    # Join with student table to get student names
    records_response = []
    for record in attendance_records:
        student = db.query(Student).filter(Student.student_usn == record.student_usn).first()
        records_response.append(AttendanceRecordResponse(
            id=record.id,
            session_id=record.session_id,
            student_usn=record.student_usn,
            student_name=student.student_name if student else None,
            mentor_id=record.mentor_id,
            marked_at=record.marked_at,
            status=record.status,
            notes=record.notes,
            session_name=session.session_name
        ))
    
    return records_response

@router.get("/attendance/all-records", response_model=List[AttendanceRecordResponse])
def get_all_attendance_records(
    mentor_id: str,
    db: Session = Depends(get_db)
):
    """Get all attendance records for a mentor across all sessions"""
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    # Get all attendance records for this mentor
    attendance_records = db.query(Attendance).filter(
        Attendance.mentor_id == mentor_id
    ).order_by(Attendance.marked_at.desc()).all()
    
    # Join with student and session tables
    records_response = []
    for record in attendance_records:
        student = db.query(Student).filter(Student.student_usn == record.student_usn).first()
        session = db.query(AttendanceSession).filter(
            AttendanceSession.session_id == record.session_id
        ).first()
        
        records_response.append(AttendanceRecordResponse(
            id=record.id,
            session_id=record.session_id,
            student_usn=record.student_usn,
            student_name=student.student_name if student else None,
            mentor_id=record.mentor_id,
            marked_at=record.marked_at,
            status=record.status,
            notes=record.notes,
            session_name=session.session_name if session else None
        ))
    
    return records_response


@router.get("/attendance/weekly-report")
def get_weekly_attendance_report(
    mentor_id: str,
    week_start: Optional[str] = Query(None, description="Monday of week (YYYY-MM-DD). Default: current week."),
    db: Session = Depends(get_db),
):
    """Weekly attendance report for each assigned student. Week is Monday–Sunday in IST."""
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    ist_tz = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist_tz).replace(tzinfo=None)
    today = now_ist.date() if hasattr(now_ist, "date") else now_ist
    if hasattr(today, "weekday"):
        days_since_monday = today.weekday()
    else:
        days_since_monday = 0

    if week_start:
        try:
            start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="week_start must be YYYY-MM-DD")
        week_start_dt = datetime.combine(start_date, datetime.min.time())
    else:
        monday = today - timedelta(days=days_since_monday)
        week_start_dt = datetime.combine(monday, datetime.min.time())

    week_end_dt = week_start_dt + timedelta(days=7)

    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    attendance_in_week = (
        db.query(Attendance)
        .filter(
            Attendance.mentor_id == mentor_id,
            Attendance.marked_at >= week_start_dt,
            Attendance.marked_at < week_end_dt,
        )
        .all()
    )

    session_cache = {}
    def get_session_name(sid):
        if sid not in session_cache:
            s = db.query(AttendanceSession).filter(AttendanceSession.session_id == sid).first()
            session_cache[sid] = s.session_name if s else None
        return session_cache[sid]

    by_student = {}
    for rec in attendance_in_week:
        if rec.student_usn not in by_student:
            by_student[rec.student_usn] = []
        by_student[rec.student_usn].append({
            "session_id": rec.session_id,
            "session_name": get_session_name(rec.session_id),
            "marked_at": rec.marked_at.isoformat() if hasattr(rec.marked_at, "isoformat") else str(rec.marked_at),
            "status": rec.status,
        })

    students_response = []
    for student in assigned_students:
        records = by_student.get(student.student_usn, [])
        present_count = sum(1 for r in records if (r.get("status") or "").lower() == "present")
        absent_count = sum(1 for r in records if (r.get("status") or "").lower() == "absent")
        late_count = sum(1 for r in records if (r.get("status") or "").lower() == "late")
        students_response.append({
            "student_usn": student.student_usn,
            "student_name": student.student_name,
            "records": records,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
        })

    return {
        "week_start": week_start_dt.date().isoformat() if hasattr(week_start_dt.date(), "isoformat") else str(week_start_dt.date()),
        "week_end": (week_end_dt - timedelta(days=1)).date().isoformat() if hasattr((week_end_dt - timedelta(days=1)).date(), "isoformat") else str((week_end_dt - timedelta(days=1)).date()),
        "students": students_response,
    }


@router.post("/attendance/deactivate-session/{session_id}")
def deactivate_session(
    mentor_id: str,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Deactivate an attendance session"""
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    session = db.query(AttendanceSession).filter(
        AttendanceSession.session_id == session_id,
        AttendanceSession.mentor_id == mentor_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    db.commit()
    
    return {"message": "Session deactivated successfully"}

@router.get("/attendance/manual/{session_id}")
def get_students_for_manual_attendance(
    mentor_id: str,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get all assigned students with their attendance status for a session"""
    # Verify mentor and session
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    session = db.query(AttendanceSession).filter(
        AttendanceSession.session_id == session_id,
        AttendanceSession.mentor_id == mentor_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all assigned students
    assigned_students = db.query(Student).filter(
        Student.assigned_mentor == mentor_id
    ).all()
    
    # Get existing attendance records for this session
    existing_attendance = db.query(Attendance).filter(
        Attendance.session_id == session_id
    ).all()
    
    # Create a map of student_usn to attendance record
    attendance_map = {record.student_usn: record for record in existing_attendance}
    
    # Build response with student info and attendance status
    students_list = []
    for student in assigned_students:
        attendance_record = attendance_map.get(student.student_usn)
        students_list.append({
            "student_usn": student.student_usn,
            "student_name": student.student_name,
            "student_email": student.student_email,
            "has_attendance": attendance_record is not None,
            "attendance_id": attendance_record.id if attendance_record else None,
            "status": attendance_record.status if attendance_record else None,
            "marked_at": attendance_record.marked_at if attendance_record else None,
            "notes": attendance_record.notes if attendance_record else None
        })
    
    return {
        "session_id": session_id,
        "session_name": session.session_name,
        "students": students_list
    }

@router.post("/attendance/manual-mark")
def mark_manual_attendance(
    mentor_id: str,
    request: ManualAttendanceMarkRequest,
    db: Session = Depends(get_db)
):
    """Mark attendance manually for one or more students"""
    # Verify mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    session_id = request.session_id
    student_usn = request.student_usn
    status = request.status
    notes = request.notes
    
    if not session_id or not student_usn:
        raise HTTPException(status_code=400, detail="session_id and student_usn are required")
    
    # Verify session belongs to mentor
    session = db.query(AttendanceSession).filter(
        AttendanceSession.session_id == session_id,
        AttendanceSession.mentor_id == mentor_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify student is assigned to this mentor
    student = db.query(Student).filter(
        Student.student_usn == student_usn,
        Student.assigned_mentor == mentor_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=403, detail="Student not assigned to this mentor")
    
    # Check if attendance already exists
    existing_attendance = db.query(Attendance).filter(
        Attendance.session_id == session_id,
        Attendance.student_usn == student_usn
    ).first()
    
    ist_tz = pytz.timezone('Asia/Kolkata')
    marked_at = datetime.now(ist_tz).replace(tzinfo=None)
    
    if existing_attendance:
        # Update existing attendance
        existing_attendance.status = status
        existing_attendance.notes = notes
        existing_attendance.marked_at = marked_at
        db.commit()
        db.refresh(existing_attendance)
        
        return {
            "id": existing_attendance.id,
            "session_id": existing_attendance.session_id,
            "student_usn": existing_attendance.student_usn,
            "mentor_id": existing_attendance.mentor_id,
            "marked_at": existing_attendance.marked_at,
            "status": existing_attendance.status,
            "notes": existing_attendance.notes,
            "message": "Attendance updated successfully"
        }
    else:
        # Create new attendance record
        attendance = Attendance(
            session_id=session_id,
            student_usn=student_usn,
            mentor_id=mentor_id,
            marked_at=marked_at,
            status=status,
            notes=notes
        )
        
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        return {
            "id": attendance.id,
            "session_id": attendance.session_id,
            "student_usn": attendance.student_usn,
            "mentor_id": attendance.mentor_id,
            "marked_at": attendance.marked_at,
            "status": attendance.status,
            "notes": attendance.notes,
            "message": "Attendance marked successfully"
        }

@router.post("/attendance/manual-mark-bulk")
def mark_manual_attendance_bulk(
    mentor_id: str,
    request: ManualAttendanceBulkRequest,
    db: Session = Depends(get_db)
):
    """Mark attendance manually for multiple students at once"""
    # Verify mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    session_id = request.session_id
    students = request.students  # List of {student_usn, status, notes}
    
    if not session_id or not students:
        raise HTTPException(status_code=400, detail="session_id and students list are required")
    
    # Verify session belongs to mentor
    session = db.query(AttendanceSession).filter(
        AttendanceSession.session_id == session_id,
        AttendanceSession.mentor_id == mentor_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    ist_tz = pytz.timezone('Asia/Kolkata')
    marked_at = datetime.now(ist_tz).replace(tzinfo=None)
    
    results = []
    for student_data in students:
        student_usn = student_data.get("student_usn")
        status = student_data.get("status", "present")
        notes = student_data.get("notes")
        
        if not student_usn:
            continue
        
        # Verify student is assigned to this mentor
        student = db.query(Student).filter(
            Student.student_usn == student_usn,
            Student.assigned_mentor == mentor_id
        ).first()
        
        if not student:
            results.append({
                "student_usn": student_usn,
                "success": False,
                "message": "Student not assigned to this mentor"
            })
            continue
        
        # Check if attendance already exists
        existing_attendance = db.query(Attendance).filter(
            Attendance.session_id == session_id,
            Attendance.student_usn == student_usn
        ).first()
        
        if existing_attendance:
            # Update existing attendance
            existing_attendance.status = status
            existing_attendance.notes = notes
            existing_attendance.marked_at = marked_at
            results.append({
                "student_usn": student_usn,
                "success": True,
                "message": "Attendance updated",
                "attendance_id": existing_attendance.id
            })
        else:
            # Create new attendance record
            attendance = Attendance(
                session_id=session_id,
                student_usn=student_usn,
                mentor_id=mentor_id,
                marked_at=marked_at,
                status=status,
                notes=notes
            )
            db.add(attendance)
            results.append({
                "student_usn": student_usn,
                "success": True,
                "message": "Attendance marked",
                "attendance_id": None  # Will be set after commit
            })
    
    db.commit()
    
    # Refresh to get IDs for new records
    for i, result in enumerate(results):
        if result.get("success") and result.get("attendance_id") is None:
            student_usn = result.get("student_usn")
            attendance = db.query(Attendance).filter(
                Attendance.session_id == session_id,
                Attendance.student_usn == student_usn
            ).first()
            if attendance:
                result["attendance_id"] = attendance.id
    
    return {
        "session_id": session_id,
        "results": results,
        "message": f"Processed {len(results)} students"
    }

