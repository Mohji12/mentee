from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.academic_performance import AcademicPerformance, AcademicPerformanceMarksheet, StudentSecondaryMarksheet
from app.schemas.academic_performance import (
    AcademicPerformanceSubmit,
    AcademicPerformanceResponse,
    AcademicPerformanceSemesterResponse,
    AcademicPerformanceRow,
    AcademicPerformanceRowWithId,
    AcademicPerformanceAddRow,
    AcademicPerformanceUpdateRow,
    AcademicPerformanceMarksheetResponse,
    SecondaryMarksheetInfo,
)
from app.core.dependencies import get_current_student
from app.services.s3bucket import s3_client, S3_BUCKET_NAME, S3_EXPIRATION
from datetime import datetime

router = APIRouter()


def _max_semesters_for_program(program: str | None) -> int:
    if program and str(program).strip().lower().startswith("bsc"):
        return 3
    return 4


def _get_marksheet_view_url(marksheet_url: str) -> str:
    """Generate presigned URL for viewing marksheet."""
    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": marksheet_url},
            ExpiresIn=S3_EXPIRATION
        )
        return presigned_url
    except Exception:
        return ""


def _require_secondary_marksheets(db: Session, student_usn: str) -> None:
    """Raise HTTP 400 if student has not uploaded both 10th and 12th marksheets."""
    rows = (
        db.query(StudentSecondaryMarksheet.standard)
        .filter(StudentSecondaryMarksheet.student_usn == student_usn.strip())
        .all()
    )
    standards = {r[0] for r in rows}
    if standards != {10, 12}:
        raise HTTPException(
            status_code=400,
            detail="Please upload both 10th and 12th standard marksheets first, then you can add semester grades and marksheets.",
        )


@router.get("/academic-performance", response_model=AcademicPerformanceResponse)
def get_academic_performance(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Get current student's academic performance (if submitted) and max_semesters from program."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    max_semesters = _max_semesters_for_program(student.student_program)
    
    # Get academic performance rows
    rows = (
        db.query(AcademicPerformance)
        .filter(AcademicPerformance.student_usn == student_usn.strip())
        .order_by(AcademicPerformance.semester, AcademicPerformance.id)
        .all()
    )
    
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
                marksheet_view_url=_get_marksheet_view_url(m.marksheet_url),
                uploaded_at=m.uploaded_at,
            )
    can_fill_semester = 10 in secondary_by_standard and 12 in secondary_by_standard

    # Get semester marksheets
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
                marksheet_view_url=_get_marksheet_view_url(m.marksheet_url),
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
                marksheet_view_url=_get_marksheet_view_url(m.marksheet_url),
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
        submitted_at=None,  # Row-level locking: no overall submission date
        max_semesters=max_semesters,
        can_fill_semester=can_fill_semester,
        secondary_marksheets=secondary_marksheets_response,
        semesters=semester_responses,
    )


@router.post("/academic-performance/rows", response_model=AcademicPerformanceResponse)
def add_academic_performance_row(
    student_usn: str,
    data: AcademicPerformanceAddRow,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Add a single row (save by row). Row is locked immediately after save - cannot edit/delete."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    _require_secondary_marksheets(db, student_usn)
    max_semesters = _max_semesters_for_program(student.student_program)
    if data.semester < 1 or data.semester > max_semesters:
        raise HTTPException(status_code=400, detail=f"Invalid semester. Allowed 1-{max_semesters} for your program.")
    rec = AcademicPerformance(
        student_usn=student_usn.strip(),
        semester=data.semester,
        course=data.course.strip(),
        grade=(data.grade or "").strip(),
        overall_attendance=(data.overall_attendance or "").strip(),
        is_locked=True,  # Lock immediately when saved
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return get_academic_performance(student_usn, current, db)


@router.put("/academic-performance/rows/{row_id}", response_model=AcademicPerformanceResponse)
def update_academic_performance_row(
    student_usn: str,
    row_id: int,
    data: AcademicPerformanceUpdateRow,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Update a single saved row. Only allowed if row is not locked."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    _require_secondary_marksheets(db, student_usn)
    row = db.query(AcademicPerformance).filter(
        AcademicPerformance.id == row_id,
        AcademicPerformance.student_usn == student_usn.strip(),
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    if row.is_locked:
        raise HTTPException(status_code=400, detail="This row is locked and cannot be edited.")
    row.course = data.course.strip()
    row.grade = (data.grade or "").strip()
    row.overall_attendance = (data.overall_attendance or "").strip()
    row.is_locked = True  # Lock after update
    db.commit()
    return get_academic_performance(student_usn, current, db)


@router.delete("/academic-performance/rows/{row_id}", response_model=AcademicPerformanceResponse)
def delete_academic_performance_row(
    student_usn: str,
    row_id: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Delete a single saved row. Only allowed if row is not locked."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    _require_secondary_marksheets(db, student_usn)
    row = db.query(AcademicPerformance).filter(
        AcademicPerformance.id == row_id,
        AcademicPerformance.student_usn == student_usn.strip(),
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    if row.is_locked:
        raise HTTPException(status_code=400, detail="This row is locked and cannot be deleted.")
    db.delete(row)
    db.commit()
    return get_academic_performance(student_usn, current, db)


@router.post("/academic-performance/marksheet/{semester}")
def upload_marksheet(
    student_usn: str,
    semester: int,
    file: UploadFile = File(...),
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Upload marksheet for a specific semester."""
    # Validate early without database queries first
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Validate file type (PDF, images)
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif'}
    file_extension = None
    if "." in file.filename:
        file_extension = "." + file.filename.rsplit(".", 1)[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: PDF, JPG, JPEG, PNG, GIF")
    
    # Now do database queries
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    _require_secondary_marksheets(db, student_usn)

    max_semesters = _max_semesters_for_program(student.student_program)
    if semester < 1 or semester > max_semesters:
        raise HTTPException(status_code=400, detail=f"Invalid semester. Allowed 1-{max_semesters} for your program.")

    # Generate S3 file name
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    s3_file_name = f"marksheets/{student_usn}/semester_{semester}_{timestamp}{file_extension}"
    
    try:
        # Upload to S3
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            s3_file_name,
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream"
            }
        )
        
        # Check if marksheet already exists for this semester
        existing = db.query(AcademicPerformanceMarksheet).filter(
            AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
            AcademicPerformanceMarksheet.semester == semester
        ).first()
        
        if existing:
            # Update existing marksheet
            existing.marksheet_url = s3_file_name
            existing.updated_at = datetime.utcnow()
        else:
            # Create new marksheet record
            marksheet = AcademicPerformanceMarksheet(
                student_usn=student_usn.strip(),
                semester=semester,
                marksheet_url=s3_file_name
            )
            db.add(marksheet)
        
        db.commit()
        
        return {
            "message": "Marksheet uploaded successfully",
            "semester": semester,
            "marksheet_url": s3_file_name
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Rollback database transaction on error
        try:
            db.rollback()
        except Exception:
            pass
        # Try to delete uploaded file from S3 if database operation failed
        try:
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_file_name)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to upload marksheet: {str(e)}")


@router.get("/academic-performance/marksheet/{semester}")
def get_marksheet(
    student_usn: str,
    semester: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Get marksheet view URL for a specific semester."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    marksheet = db.query(AcademicPerformanceMarksheet).filter(
        AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
        AcademicPerformanceMarksheet.semester == semester
    ).first()
    
    if not marksheet:
        raise HTTPException(status_code=404, detail="Marksheet not found for this semester")
    
    try:
        view_url = _get_marksheet_view_url(marksheet.marksheet_url)
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


# --- Secondary marksheets (10th and 12th standard) ---

@router.post("/academic-performance/secondary-marksheet/{standard}")
def upload_secondary_marksheet(
    student_usn: str,
    standard: int,
    file: UploadFile = File(...),
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Upload 10th or 12th standard marksheet. Required before filling semester grades."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    if standard not in (10, 12):
        raise HTTPException(status_code=400, detail="Standard must be 10 or 12")
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".gif"}
    file_extension = None
    if "." in file.filename:
        file_extension = "." + file.filename.rsplit(".", 1)[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: PDF, JPG, JPEG, PNG, GIF")

    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    s3_file_name = f"marksheets/{student_usn}/secondary_{standard}_{timestamp}{file_extension}"

    try:
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            s3_file_name,
            ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
        )
        existing = (
            db.query(StudentSecondaryMarksheet)
            .filter(
                StudentSecondaryMarksheet.student_usn == student_usn.strip(),
                StudentSecondaryMarksheet.standard == standard,
            )
            .first()
        )
        if existing:
            existing.marksheet_url = s3_file_name
            existing.updated_at = datetime.utcnow()
        else:
            db.add(
                StudentSecondaryMarksheet(
                    student_usn=student_usn.strip(),
                    standard=standard,
                    marksheet_url=s3_file_name,
                )
            )
        db.commit()
        return {
            "message": f"{standard}th standard marksheet uploaded successfully",
            "standard": standard,
            "marksheet_url": s3_file_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        try:
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_file_name)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to upload marksheet: {str(e)}")


@router.get("/academic-performance/secondary-marksheet/{standard}")
def get_secondary_marksheet(
    student_usn: str,
    standard: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Get view URL for 10th or 12th standard marksheet."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    if standard not in (10, 12):
        raise HTTPException(status_code=400, detail="Standard must be 10 or 12")
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
        view_url = _get_marksheet_view_url(row.marksheet_url)
        return {
            "standard": standard,
            "marksheet_url": row.marksheet_url,
            "marksheet_view_url": view_url,
            "uploaded_at": row.uploaded_at.isoformat() if row.uploaded_at else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate view URL: {str(e)}")


