from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.db.models.competencies import Competencies
from app.db.models.mentors import Mentor
from app.db.models.students import Student
from app.db.models.psychometric_responses import PsychometricResponse
from app.db.models.report import Report
from app.db.models.activities import Activities
from app.db.models.mentee_competency_report import MenteeCompetencyReport
from app.db.models.MCA_assignments import MentorshipAssessment
from app.db.models.academic_performance import AcademicPerformance, AcademicPerformanceMarksheet, StudentSecondaryMarksheet
from app.db.models.experience_learning import ExperienceLearning
from app.db.models.pf16_responses import PF16Response
from app.db.models.ibp_responses import IBPResponse
from app.db.models.email_logs import EmailLog
from app.db.models.swot import SWOT
from app.db.models.activities_tracking import ActivitiesTracking
from app.db.models.counseling import CounselingSession, SessionIssuesResolution
from app.db.models.meetings import Meetings
from app.db.models.attendance import Attendance, AttendanceSession
from app.schemas.academic_performance import (
    AcademicPerformanceResponse,
    AcademicPerformanceSemesterResponse,
    AcademicPerformanceRowWithId,
    AcademicPerformanceMarksheetResponse,
    SecondaryMarksheetInfo,
)
from app.schemas.experience_learning import ExperienceLearningResponse
from app.schemas.students import SendEmailRequest
from app.core.dependencies import get_current_mentor
from app.services.s3bucket import get_document_url
from app.services.email_services import send_email
from typing import List, Optional, Dict, Any
from datetime import datetime
import pytz
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

router = APIRouter()


def _max_semesters_for_program(program: str | None) -> int:
    if program and str(program).strip().lower().startswith("bsc"):
        return 3
    return 4

@router.get("/assigned_students")
def get_assigned_students(mentor_id: str, db: Session = Depends(get_db)):
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()

    if not assigned_students:
        raise HTTPException(status_code=404, detail="No students assigned to this mentor")

    student_list = []
    for student in assigned_students:
        statuses = []

        if student.student_email and student.student_password:
            statuses.append("Signed Up")
        if all([
            student.student_name, student.student_email, student.student_phoneno,
            student.student_program, student.semester
        ]):
            statuses.append("Profile Created")

        # Check for related records *inside* the loop, for each student:
        has_psychometric = db.query(PsychometricResponse).filter(PsychometricResponse.student_usn == student.student_usn).first()
        if has_psychometric:
            statuses.append("Form Filled")
        has_swot = db.query(Report).filter(Report.student_usn == student.student_usn).first()
        if has_swot:
            statuses.append("SWOT Generated")
        has_activities = db.query(Activities).filter(Activities.student_usn == student.student_usn).first()
        if has_activities:
            statuses.append("Activities Generated")
        has_mca = db.query(MentorshipAssessment).filter(MentorshipAssessment.student_usn == student.student_usn).first()
        if has_mca:
            statuses.append("MCA FORM Filled")

        has_pf16 = db.query(PF16Response).filter(PF16Response.student_usn == student.student_usn).first()
        if has_pf16:
            statuses.append("16PF Filled")

        has_ibp = db.query(IBPResponse).filter(IBPResponse.student_usn == student.student_usn).first()
        if has_ibp:
            statuses.append("IBP Filled")

        # If all steps are present, override with complete flow status
        if all([student.student_email and student.student_password,
                all([
                    student.student_name, student.student_email, student.student_phoneno,
                    student.student_program, student.semester
                ]),
                has_psychometric, has_swot, has_activities, has_mca]):
            statuses = ["Complete Flow till MCA FORM Filled"]

        if not statuses:
            statuses.append("Not Started")

        student_list.append({
            "student_usn": student.student_usn,
            "student_name": student.student_name,
            "phone": student.student_phoneno,
            "program": student.student_program,
            "email": student.student_email,
            "linkedin": student.linkedin,
            "semester": student.semester,
            "status": " → ".join(statuses)
        })

    return student_list


@router.post("/send-email")
def send_email_to_student(
    mentor_id: str,
    body: SendEmailRequest,
    db: Session = Depends(get_db),
):
    """Send an email to an assigned student (to their official student_email)."""
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    student = db.query(Student).filter(Student.student_usn == body.student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.assigned_mentor != mentor_id:
        raise HTTPException(
            status_code=403,
            detail="This student is not assigned to you. You can only email your assigned mentees.",
        )

    if not student.student_email or not isinstance(student.student_email, str) or "@" not in student.student_email:
        raise HTTPException(
            status_code=400,
            detail="This student has no valid email on file. Cannot send email.",
        )

    try:
        # Wrap message in a simple paragraph for HTML email
        html_body = f"<p>{body.message.replace(chr(10), '<br>')}</p>"
        result = send_email(student.student_email, body.subject, html_body)
        
        # Try to log the email to database (don't fail if table doesn't exist)
        try:
            email_log = EmailLog(
                mentor_id=mentor_id,
                student_usn=body.student_usn,
                recipient_email=student.student_email,
                recipient_name=student.student_name or body.student_usn,
                subject=body.subject,
                message=body.message,
                status="sent" if result else "failed",
                email_type="manual",
                sent_at=datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)
            )
            db.add(email_log)
            db.commit()
        except Exception as log_error:
            db.rollback()
            print(f"Warning: Could not log email to database: {log_error}")
        
        if result:
            return {"success": True, "message": f"Email sent to {student.student_email}"}
        raise HTTPException(status_code=503, detail="Failed to send email. Please try again.")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email. Please try again.")


@router.get("/email-history")
def get_email_history(
    mentor_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Get email history for a mentor."""
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    
    emails = db.query(EmailLog).filter(
        EmailLog.mentor_id == mentor_id
    ).order_by(desc(EmailLog.sent_at)).limit(limit).all()
    
    return {
        "emails": [
            {
                "id": email.id,
                "student_usn": email.student_usn,
                "recipient_name": email.recipient_name,
                "recipient_email": email.recipient_email,
                "subject": email.subject,
                "message": email.message[:200] + "..." if len(email.message) > 200 else email.message,
                "full_message": email.message,
                "sent_at": email.sent_at.isoformat() if email.sent_at else None,
                "status": email.status,
                "email_type": email.email_type
            }
            for email in emails
        ],
        "total": len(emails)
    }


@router.get("/student_stats")
def get_mentor_student_statistics(mentor_id: str, db: Session = Depends(get_db)):
    # Verify the mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    # Fetch assigned students
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    if not assigned_students:
        raise HTTPException(status_code=404, detail="No students assigned to this mentor")

    # Initialize counters
    psychometric_filled = 0
    report_generated = 0
    activities_generated = 0

    # Count unique students with observation recommendations
    observation_generated = db.query(
        MenteeCompetencyReport.student_usn
    ).filter(
        MenteeCompetencyReport.student_usn.in_([s.student_usn for s in assigned_students])
    ).distinct().count()

    # Count unique students with MCA form filled
    mca_filled = db.query(
        MentorshipAssessment.student_usn
    ).filter(
        MentorshipAssessment.student_usn.in_([s.student_usn for s in assigned_students])
    ).distinct().count()

    # Count unique students with PF16 form filled
    pf16_filled = db.query(
        PF16Response.student_usn
    ).filter(
        PF16Response.student_usn.in_([s.student_usn for s in assigned_students])
    ).distinct().count()

    # Count unique students with IBP form filled
    ibp_filled = db.query(
        IBPResponse.student_usn
    ).filter(
        IBPResponse.student_usn.in_([s.student_usn for s in assigned_students])
    ).distinct().count()

    for student in assigned_students:
        # Check if the psychometric form is filled
        psychometric_entry = db.query(PsychometricResponse).filter(
            PsychometricResponse.student_usn == student.student_usn
        ).first()
        if psychometric_entry:
            psychometric_filled += 1

        # Check if the report is generated
        report_entry = db.query(Report).filter(Report.student_usn == student.student_usn).first()
        if report_entry:
            report_generated += 1

        # Check if activities are generated
        activity_entry = db.query(Activities).filter(
            Activities.student_usn == student.student_usn
        ).first()
        if activity_entry:
            activities_generated += 1

    # Return the statistics
    return {
        "total_students": len(assigned_students),
        "psychometric_form_filled": psychometric_filled,
        "report_generated": report_generated,
        "activities_generated": activities_generated,
        "mca_filled": mca_filled,
        "observation_generated": observation_generated,
        "pf16_filled": pf16_filled,
        "ibp_filled": ibp_filled,
    }


def _get_marksheet_view_url_mentor(marksheet_url: str) -> str:
    """Return view URL for marksheet (Cloudinary or legacy S3)."""
    return get_document_url(marksheet_url)


@router.get("/students/{student_usn}/academic-performance", response_model=AcademicPerformanceResponse)
def get_student_academic_performance_mentor(
    mentor_id: str,
    student_usn: str,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Mentor view: get academic performance of an assigned student (read-only)."""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.assigned_mentor != mentor_id:
        raise HTTPException(status_code=403, detail="Student is not assigned to you")
    max_semesters = _max_semesters_for_program(student.student_program)

    # Get secondary marksheets (10th, 12th)
    secondary = (
        db.query(StudentSecondaryMarksheet)
        .filter(StudentSecondaryMarksheet.student_usn == student_usn.strip())
        .all()
    )
    secondary_by_standard = {m.standard: m for m in secondary}
    secondary_marksheets_response = {}
    for std in (10, 12):
        if std in secondary_by_standard:
            m = secondary_by_standard[std]
            secondary_marksheets_response[std] = SecondaryMarksheetInfo(
                standard=std,
                marksheet_url=m.marksheet_url,
                marksheet_view_url=_get_marksheet_view_url_mentor(m.marksheet_url),
                uploaded_at=m.uploaded_at,
            )
    can_fill_semester = 10 in secondary_by_standard and 12 in secondary_by_standard

    # Get academic performance rows
    rows = (
        db.query(AcademicPerformance)
        .filter(AcademicPerformance.student_usn == student_usn.strip())
        .order_by(AcademicPerformance.semester, AcademicPerformance.id)
        .all()
    )
    
    # Get marksheets
    marksheets = (
        db.query(AcademicPerformanceMarksheet)
        .filter(AcademicPerformanceMarksheet.student_usn == student_usn.strip())
        .all()
    )
    marksheets_by_semester = {m.semester: m for m in marksheets}
    
    by_semester = {}
    for r in rows:
        if r.semester not in by_semester:
            by_semester[r.semester] = []
        by_semester[r.semester].append(
            AcademicPerformanceRowWithId(
                id=r.id,
                course=r.course,
                grade=r.grade or "",
                overall_attendance=r.overall_attendance or "",
                is_locked=r.is_locked or False
            )
        )
    
    # Build semester responses with marksheet info
    semester_responses = []
    for sem in sorted(by_semester.keys()):
        marksheet_info = None
        if sem in marksheets_by_semester:
            m = marksheets_by_semester[sem]
            marksheet_info = AcademicPerformanceMarksheetResponse(
                semester=sem,
                marksheet_url=m.marksheet_url,
                marksheet_view_url=_get_marksheet_view_url_mentor(m.marksheet_url),
                uploaded_at=m.uploaded_at
            )
        semester_responses.append(
            AcademicPerformanceSemesterResponse(
                semester=sem,
                rows=by_semester[sem],
                marksheet=marksheet_info
            )
        )
    
    # Include semesters with marksheets but no rows
    for sem in marksheets_by_semester.keys():
        if sem not in by_semester:
            m = marksheets_by_semester[sem]
            marksheet_info = AcademicPerformanceMarksheetResponse(
                semester=sem,
                marksheet_url=m.marksheet_url,
                marksheet_view_url=_get_marksheet_view_url_mentor(m.marksheet_url),
                uploaded_at=m.uploaded_at
            )
            semester_responses.append(
                AcademicPerformanceSemesterResponse(
                    semester=sem,
                    rows=[],
                    marksheet=marksheet_info
                )
            )
    
    return AcademicPerformanceResponse(
        submitted_at=None,
        max_semesters=max_semesters,
        can_fill_semester=can_fill_semester,
        secondary_marksheets=secondary_marksheets_response,
        semesters=semester_responses,
    )


@router.get("/students/{student_usn}/academic-performance/marksheet/{semester}")
def get_student_marksheet_mentor(
    mentor_id: str,
    student_usn: str,
    semester: int,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Mentor view: get marksheet view URL for a specific semester."""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.assigned_mentor != mentor_id:
        raise HTTPException(status_code=403, detail="Student is not assigned to you")
    
    marksheet = db.query(AcademicPerformanceMarksheet).filter(
        AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
        AcademicPerformanceMarksheet.semester == semester
    ).first()
    
    if not marksheet:
        raise HTTPException(status_code=404, detail="Marksheet not found for this semester")
    
    try:
        view_url = _get_marksheet_view_url_mentor(marksheet.marksheet_url)
        return {
            "semester": semester,
            "marksheet_url": marksheet.marksheet_url,
            "marksheet_view_url": view_url,
            "uploaded_at": marksheet.uploaded_at.isoformat() if marksheet.uploaded_at else None
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate view URL: {str(e)}")


@router.get("/students/{student_usn}/academic-performance/secondary-marksheet/{standard}")
def get_student_secondary_marksheet_mentor(
    mentor_id: str,
    student_usn: str,
    standard: int,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Mentor view: get 10th or 12th standard marksheet view URL."""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if standard not in (10, 12):
        raise HTTPException(status_code=400, detail="Standard must be 10 or 12")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.assigned_mentor != mentor_id:
        raise HTTPException(status_code=403, detail="Student is not assigned to you")
    row = (
        db.query(StudentSecondaryMarksheet)
        .filter(
            StudentSecondaryMarksheet.student_usn == student_usn.strip(),
            StudentSecondaryMarksheet.standard == standard,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Marksheet not found for {standard}th standard")
    try:
        view_url = _get_marksheet_view_url_mentor(row.marksheet_url)
        return {
            "standard": standard,
            "marksheet_url": row.marksheet_url,
            "marksheet_view_url": view_url,
            "uploaded_at": row.uploaded_at.isoformat() if row.uploaded_at else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate view URL: {str(e)}")


@router.get("/students/experience-learning", response_model=List[ExperienceLearningResponse])
def get_assigned_students_experience_learning(
    mentor_id: str,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Get all experience learning entries from assigned students"""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Verify mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    # Get all assigned students
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()
    
    if not assigned_students:
        return []

    # Get all experience learning entries for assigned students
    student_usns = [student.student_usn for student in assigned_students]
    entries = (
        db.query(ExperienceLearning)
        .filter(
            ExperienceLearning.student_usn.in_(student_usns),
            ExperienceLearning.mentor_id.is_(None)  # Only student entries, not mentor entries
        )
        .order_by(ExperienceLearning.created_at.desc())
        .all()
    )

    # Create a mapping of student_usn to student_name for display
    student_map = {student.student_usn: student.student_name for student in assigned_students}

    result = []
    for entry in entries:
        entry_dict = {
            "id": entry.id,
            "student_usn": entry.student_usn,
            "mentor_id": entry.mentor_id,
            "title": entry.title,
            "detailed_explanation": entry.detailed_explanation,
            "proof_file_path": entry.proof_file_path,
            "proof_url": None,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }

        # Generate proof URL if proof exists
        if entry.proof_file_path:
            try:
                proof_url = get_document_url(entry.proof_file_path)
                entry_dict["proof_url"] = proof_url
            except Exception:
                pass

        # Create response with student_name included
        response_data = {
            "id": entry_dict["id"],
            "student_usn": entry_dict["student_usn"],
            "mentor_id": entry_dict["mentor_id"],
            "title": entry_dict["title"],
            "detailed_explanation": entry_dict["detailed_explanation"],
            "proof_file_path": entry_dict["proof_file_path"],
            "proof_url": entry_dict["proof_url"],
            "created_at": entry_dict["created_at"],
            "updated_at": entry_dict["updated_at"],
            "student_name": student_map.get(entry.student_usn, "Unknown")
        }
        result.append(ExperienceLearningResponse(**response_data))

    return result


@router.get("/students/{student_usn}/details")
def get_student_details(
    mentor_id: str,
    student_usn: str,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get comprehensive details of a student assigned to the mentor.
    Aggregates data from multiple tables: profile, academic performance, 
    forms status, activities, counseling sessions, and meetings.
    """
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Verify student exists and is assigned to this mentor
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.assigned_mentor != mentor_id:
        raise HTTPException(status_code=403, detail="Student is not assigned to you")
    
    # 1. Basic Profile
    profile = {
        "student_usn": student.student_usn,
        "student_name": student.student_name,
        "student_email": student.student_email,
        "student_phoneno": student.student_phoneno,
        "student_program": student.student_program,
        "semester": student.semester,
        "student_batch": student.student_batch,
        "linkedin": student.linkedin,
        "gender": student.gender,
        "blood_group": student.blood_group,
        "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None,
        "parent_guardian_contact": student.parent_guardian_contact,
    }
    
    # 2. Academic Performance Summary
    academic_performance = _get_academic_performance_summary(db, student_usn, mentor_id)
    
    # 3. Forms Status
    forms_status = _get_forms_status(db, student_usn)
    
    # 4. Activities
    activities = _get_activities_summary(db, student_usn)
    
    # 5. Counseling Sessions
    counseling_sessions = _get_counseling_sessions(db, student_usn)
    
    # 6. Meetings
    meetings = _get_meetings(db, student_usn, mentor_id)
    
    # 7. Attendance
    attendance = _get_attendance_stats(db, student_usn, mentor_id)
    
    # 8. Experiential Learning
    experiential_learning = _get_experiential_learning(db, student_usn)
    
    return {
        "profile": profile,
        "academic_performance": academic_performance,
        "forms_status": forms_status,
        "activities": activities,
        "counseling_sessions": counseling_sessions,
        "meetings": meetings,
        "attendance": attendance,
        "experiential_learning": experiential_learning,
    }


# JAIN report styling constants
_HEADER_GREY = colors.HexColor("#4a4a4a")
_LIGHT_GREY = colors.HexColor("#e8e8e8")


def _split_for_abcd(text: str) -> List[str]:
    """Split text into up to 4 items for (a)(b)(c)(d) format."""
    if not text or not str(text).strip():
        return ["", "", "", ""]
    s = str(text).strip()
    parts = [p.strip() for p in s.replace("\r\n", "\n").split("\n") if p.strip()]
    while len(parts) < 4:
        parts.append("")
    return parts[:4]


def _draw_jain_header(c, width, height, jain_logo_reader):
    """Draw JAIN logo at top right."""
    if jain_logo_reader:
        try:
            c.drawImage(jain_logo_reader, width - 130, height - 70, width=100, height=50)
        except Exception:
            pass


def _draw_table_on_canvas(c, table_data, col_widths, x, y, header_bg=_HEADER_GREY):
    """Draw a ReportLab Table on canvas, return y position after table."""
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT_GREY]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
    ]))
    t.wrapOn(c, sum(col_widths), 600)
    t.drawOn(c, x, y - t._height)
    return y - t._height - 15


def _get_academic_performance_summary(db: Session, student_usn: str, mentor_id: str) -> Dict[str, Any]:
    """Get academic performance summary for a student."""
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    max_semesters = _max_semesters_for_program(student.student_program if student else None)
    
    # Get secondary marksheets (10th, 12th)
    secondary = (
        db.query(StudentSecondaryMarksheet)
        .filter(StudentSecondaryMarksheet.student_usn == student_usn)
        .all()
    )
    secondary_marksheets = {}
    for m in secondary:
        secondary_marksheets[m.standard] = {
            "standard": m.standard,
            "marksheet_url": m.marksheet_url,
            "marksheet_view_url": _get_marksheet_view_url_mentor(m.marksheet_url) if m.marksheet_url else None,
            "uploaded_at": m.uploaded_at.isoformat() if m.uploaded_at else None,
        }
    
    # Get semester-wise academic performance
    rows = (
        db.query(AcademicPerformance)
        .filter(AcademicPerformance.student_usn == student_usn)
        .order_by(AcademicPerformance.semester, AcademicPerformance.id)
        .all()
    )
    
    marksheets = (
        db.query(AcademicPerformanceMarksheet)
        .filter(AcademicPerformanceMarksheet.student_usn == student_usn)
        .all()
    )
    marksheets_by_semester = {m.semester: m for m in marksheets}
    
    semesters = {}
    for r in rows:
        if r.semester not in semesters:
            semesters[r.semester] = {"rows": [], "marksheet": None}
        semesters[r.semester]["rows"].append({
            "id": r.id,
            "course": r.course,
            "grade": r.grade or "",
            "overall_attendance": r.overall_attendance or "",
            "is_locked": r.is_locked or False,
        })
    
    for sem, m in marksheets_by_semester.items():
        if sem not in semesters:
            semesters[sem] = {"rows": [], "marksheet": None}
        semesters[sem]["marksheet"] = {
            "marksheet_url": m.marksheet_url,
            "marksheet_view_url": _get_marksheet_view_url_mentor(m.marksheet_url) if m.marksheet_url else None,
            "uploaded_at": m.uploaded_at.isoformat() if m.uploaded_at else None,
        }
    
    return {
        "max_semesters": max_semesters,
        "secondary_marksheets": secondary_marksheets,
        "semesters": semesters,
    }


def _get_forms_status(db: Session, student_usn: str) -> Dict[str, Any]:
    """Get completion status of all forms for a student."""
    # Psychometric
    psychometric = db.query(PsychometricResponse).filter(
        PsychometricResponse.student_usn == student_usn
    ).first()
    
    # SWOT
    swot = db.query(SWOT).filter(SWOT.student_usn == student_usn).first()
    
    # Report (generated SWOT analysis)
    report = db.query(Report).filter(Report.student_usn == student_usn).first()
    
    # MCA Assessment
    mca = db.query(MentorshipAssessment).filter(
        MentorshipAssessment.student_usn == student_usn
    ).first()
    
    # PF16
    pf16 = db.query(PF16Response).filter(
        PF16Response.student_usn == student_usn
    ).first()
    
    # IBP
    ibp = db.query(IBPResponse).filter(
        IBPResponse.student_usn == student_usn
    ).first()
    
    return {
        "psychometric": {
            "completed": psychometric is not None,
            "submitted_at": psychometric.submitted_at.isoformat() if psychometric and psychometric.submitted_at else None,
        },
        "swot": {
            "completed": swot is not None or report is not None,
            "has_analysis": report is not None,
        },
        "mca": {
            "completed": mca is not None,
            "submitted_at": mca.submitted_at.isoformat() if mca and mca.submitted_at else None,
        },
        "pf16": {
            "completed": pf16 is not None,
            "submitted_at": pf16.submitted_at.isoformat() if pf16 and pf16.submitted_at else None,
        },
        "ibp": {
            "completed": ibp is not None,
            "submitted_at": ibp.submitted_at.isoformat() if ibp and ibp.submitted_at else None,
        },
    }


def _get_activities_summary(db: Session, student_usn: str) -> List[Dict[str, Any]]:
    """Get all activities for a student."""
    activities = (
        db.query(ActivitiesTracking)
        .filter(ActivitiesTracking.student_usn == student_usn)
        .all()
    )
    
    result = []
    for a in activities:
        proof_url = None
        if a.proof:
            try:
                proof_url = get_document_url(a.proof)
            except Exception:
                pass
        
        result.append({
            "id": a.id,
            "activity": a.activities,
            "duration_type": a.duration_type,
            "deadline": a.deadline.isoformat() if a.deadline else None,
            "status": a.status,
            "percentage": a.percentage,
            "remarks": a.remarks,
            "benefitted": a.benefitted,
            "completed_in": a.completed_in,
            "rejection_reason": a.rejection_reason,
            "requested_by": a.requested_by,
            "proof_url": proof_url,
        })
    
    return result


def _get_counseling_sessions(db: Session, student_usn: str) -> List[Dict[str, Any]]:
    """Get all counseling sessions for a student."""
    sessions = (
        db.query(CounselingSession)
        .filter(CounselingSession.student_usn == student_usn)
        .order_by(desc(CounselingSession.session_date))
        .all()
    )
    
    result = []
    for s in sessions:
        result.append({
            "id": s.id,
            "counseling_id": s.counseling_id,
            "session_date": s.session_date.isoformat() if s.session_date else None,
            "venue": s.venue,
            "reason": s.reason,
            "status": s.status,
            "is_urgent": s.is_urgent,
            "notes": s.notes,
            "feedback": s.feedback,
            "outcome_status": getattr(s, "outcome_status", None),
            "outcome_notes": getattr(s, "outcome_notes", None),
            "followup_date": s.followup_date.isoformat() if getattr(s, "followup_date", None) else None,
            "student_rating": s.student_rating,
            "mentor_rating": s.mentor_rating,
            "referred_to_name": s.referred_to_name,
            "referred_to_contact": s.referred_to_contact,
            "google_meet_link": s.google_meet_link,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    
    return result


def _get_meetings(db: Session, student_usn: str, mentor_id: str) -> List[Dict[str, Any]]:
    """Get all meetings for a student with this mentor."""
    meetings = (
        db.query(Meetings)
        .filter(
            Meetings.student_usn == student_usn,
            Meetings.mentor_id == mentor_id
        )
        .order_by(desc(Meetings.meeting_date))
        .all()
    )
    
    result = []
    for m in meetings:
        result.append({
            "id": m.id,
            "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
            "venue": m.venue,
            "status": m.status,
            "attendance": m.attendance,
            "agenda": m.agenda,
            "duration": m.duration,
            "meeting_mode": m.meeting_mode,
            "progress_notes": m.progress_notes,
            "google_meet_link": m.google_meet_link,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
    
    return result


def _get_attendance_stats(db: Session, student_usn: str, mentor_id: str) -> Dict[str, Any]:
    """Get attendance statistics and records for a student."""
    # Get all attendance records for this student with this mentor
    attendance_records = (
        db.query(Attendance, AttendanceSession)
        .join(AttendanceSession, Attendance.session_id == AttendanceSession.session_id)
        .filter(
            Attendance.student_usn == student_usn,
            Attendance.mentor_id == mentor_id
        )
        .order_by(desc(Attendance.marked_at))
        .all()
    )
    
    # Calculate statistics
    total_sessions = len(attendance_records)
    present_count = sum(1 for a, _ in attendance_records if a.status == "present")
    late_count = sum(1 for a, _ in attendance_records if a.status == "late")
    absent_count = sum(1 for a, _ in attendance_records if a.status == "absent")
    
    # Calculate attendance percentage (present + late counts as attended)
    attendance_percentage = 0
    if total_sessions > 0:
        attendance_percentage = round(((present_count + late_count) / total_sessions) * 100, 1)
    
    # Build records list
    records = []
    for attendance, session in attendance_records:
        records.append({
            "id": attendance.id,
            "session_id": attendance.session_id,
            "session_name": session.session_name or "Unnamed Session",
            "location": session.location,
            "marked_at": attendance.marked_at.isoformat() if attendance.marked_at else None,
            "session_date": session.created_at.isoformat() if session.created_at else None,
            "status": attendance.status,
            "notes": attendance.notes,
        })
    
    return {
        "summary": {
            "total_sessions": total_sessions,
            "present": present_count,
            "late": late_count,
            "absent": absent_count,
            "attendance_percentage": attendance_percentage,
        },
        "records": records,
    }


def _get_experiential_learning(db: Session, student_usn: str) -> List[Dict[str, Any]]:
    """Get all experiential learning entries for a student."""
    entries = (
        db.query(ExperienceLearning)
        .filter(ExperienceLearning.student_usn == student_usn)
        .order_by(desc(ExperienceLearning.created_at))
        .all()
    )
    
    result = []
    for entry in entries:
        proof_url = None
        if entry.proof_file_path:
            try:
                proof_url = get_document_url(entry.proof_file_path)
            except Exception:
                pass
        
        result.append({
            "id": entry.id,
            "title": entry.title,
            "detailed_explanation": entry.detailed_explanation,
            "proof_file_path": entry.proof_file_path,
            "proof_url": proof_url,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
        })
    
    return result


def _get_issues_resolutions_for_report(db: Session, student_usn: str) -> List[Dict[str, Any]]:
    """Get all issues raised and resolved from counseling sessions for a student."""
    sessions = (
        db.query(CounselingSession)
        .filter(CounselingSession.student_usn == student_usn)
        .all()
    )
    result = []
    sn = 1
    for session in sessions:
        resolutions = (
            db.query(SessionIssuesResolution)
            .filter(SessionIssuesResolution.counseling_id == session.counseling_id)
            .order_by(SessionIssuesResolution.serial_no)
            .all()
        )
        for r in resolutions:
            date_raised = r.date_issue_raised.strftime("%d-%b-%Y") if r.date_issue_raised else ""
            date_resolved = r.date_resolution_provided.strftime("%d-%b-%Y") if r.date_resolution_provided else ""
            result.append({
                "serial_no": sn,
                "issues_raised": r.issues_raised or "",
                "date_issue_raised": date_raised,
                "resolution_details": r.resolution_details or "",
                "date_resolution_provided": date_resolved,
            })
            sn += 1
    return result
