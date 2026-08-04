from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_student
from app.db.database import get_db
from app.db.models.academic_performance import (
    AcademicPerformance,
    AcademicPerformanceMarksheet,
    StudentSecondaryMarksheet,
)
from app.db.models.students import Student
from app.schemas.academic_performance import (
    AcademicDocumentsSummary,
    AcademicPerformanceAddRow,
    AcademicPerformanceMarksheetResponse,
    AcademicPerformanceResponse,
    AcademicPerformanceRowWithId,
    AcademicPerformanceSemesterResponse,
    AcademicPerformanceUpdateRow,
    SecondaryMarksheetInfo,
    SecondaryMarksheetMetadataUpdate,
    SemesterMarksheetMetadataUpdate,
)
from app.services import academic_document_service as doc_svc

router = APIRouter()


def _max_semesters_for_program(program: str | None) -> int:
    if program and str(program).strip().lower().startswith("bsc"):
        return 3
    return 4


def _get_marksheet_view_url(marksheet_url: str) -> str:
    return doc_svc.get_view_url(marksheet_url)


def _require_secondary_marksheets(db: Session, student_usn: str) -> None:
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


def _secondary_info(m: StudentSecondaryMarksheet) -> SecondaryMarksheetInfo:
    return SecondaryMarksheetInfo(
        standard=m.standard,
        document_type=m.document_type or doc_svc.document_type_for_standard(m.standard),
        marksheet_url=m.marksheet_url,
        marksheet_view_url=_get_marksheet_view_url(m.marksheet_url),
        uploaded_at=m.uploaded_at,
        updated_at=m.updated_at,
        board_university=m.board_university,
        institution_name=m.institution_name,
        year_of_passing=m.year_of_passing,
        percentage_cgpa=m.percentage_cgpa,
        verification_status=m.verification_status or "pending",
        remarks=m.remarks,
        uploaded_by=m.uploaded_by,
        verified_by=m.verified_by,
        verified_at=m.verified_at,
    )


def _semester_marksheet_info(m: AcademicPerformanceMarksheet) -> AcademicPerformanceMarksheetResponse:
    return AcademicPerformanceMarksheetResponse(
        semester=m.semester,
        marksheet_url=m.marksheet_url,
        marksheet_view_url=_get_marksheet_view_url(m.marksheet_url),
        uploaded_at=m.uploaded_at,
        updated_at=m.updated_at,
        sgpa=m.sgpa,
        cgpa=m.cgpa,
        percentage=m.percentage,
        total_credits=m.total_credits,
        backlogs=m.backlogs,
        result_status=m.result_status,
        academic_year=m.academic_year,
        verification_status=m.verification_status or "pending",
        remarks=m.remarks,
        uploaded_by=m.uploaded_by,
        verified_by=m.verified_by,
        verified_at=m.verified_at,
    )


def _build_documents_summary(
    db: Session,
    student_usn: str,
    max_semesters: int,
    secondary: list[StudentSecondaryMarksheet],
    marksheets: list[AcademicPerformanceMarksheet],
) -> AcademicDocumentsSummary:
    secondary_by = {m.standard: m for m in secondary}
    ms_by_sem = {m.semester: m for m in marksheets}
    all_docs = list(secondary) + list(marksheets)

    total_uploaded = len(all_docs)
    missing = 0
    if 10 not in secondary_by:
        missing += 1
    if 12 not in secondary_by:
        missing += 1
    for sem in range(1, max_semesters + 1):
        if sem not in ms_by_sem:
            missing += 1

    pending = verified = rejected = reupload = 0
    for d in all_docs:
        st = (d.verification_status or "pending").lower()
        if st == "verified":
            verified += 1
        elif st == "rejected":
            rejected += 1
        elif st == "reupload_required":
            reupload += 1
        else:
            pending += 1

    return AcademicDocumentsSummary(
        total_uploaded=total_uploaded,
        missing_count=missing,
        pending_verification=pending,
        verified=verified,
        rejected=rejected,
        reupload_required=reupload,
    )


def _matches_filters(
    *,
    document_type: Optional[str],
    semester: Optional[int],
    verification_status: Optional[str],
    academic_year: Optional[str],
    uploaded_from: Optional[datetime],
    uploaded_to: Optional[datetime],
    search: Optional[str],
    kind: str,
    std: Optional[int] = None,
    sem: Optional[int] = None,
    status: Optional[str] = None,
    year: Optional[str] = None,
    uploaded_at: Optional[datetime] = None,
    institution: Optional[str] = None,
    board: Optional[str] = None,
    doc_type_label: Optional[str] = None,
) -> bool:
    if document_type:
        dt = document_type.strip().lower()
        if kind == "secondary":
            label = (doc_type_label or "").lower()
            if dt not in {label, f"{std}th", str(std)}:
                return False
        elif kind == "semester":
            if dt not in {"semester", "graduation", f"sem{sem}", f"semester {sem}"}:
                if not (dt.isdigit() and int(dt) == sem):
                    return False
    if semester is not None and kind == "semester" and sem != semester:
        return False
    if semester is not None and kind == "secondary":
        return False
    if verification_status and (status or "pending").lower() != verification_status.strip().lower():
        return False
    if academic_year and kind == "semester":
        if not year or academic_year.strip().lower() not in year.lower():
            return False
    if uploaded_from and uploaded_at and uploaded_at < uploaded_from:
        return False
    if uploaded_to and uploaded_at and uploaded_at > uploaded_to:
        return False
    if search:
        q = search.strip().lower()
        blob = " ".join(
            [
                institution or "",
                board or "",
                year or "",
                doc_type_label or "",
                str(std or ""),
                str(sem or ""),
            ]
        ).lower()
        if q not in blob:
            return False
    return True


def _build_academic_response(
    db: Session,
    student: Student,
    *,
    document_type: Optional[str] = None,
    semester: Optional[int] = None,
    verification_status: Optional[str] = None,
    academic_year: Optional[str] = None,
    uploaded_from: Optional[datetime] = None,
    uploaded_to: Optional[datetime] = None,
    search: Optional[str] = None,
) -> AcademicPerformanceResponse:
    usn = student.student_usn.strip()
    max_semesters = _max_semesters_for_program(student.student_program)

    rows = (
        db.query(AcademicPerformance)
        .filter(AcademicPerformance.student_usn == usn)
        .order_by(AcademicPerformance.semester, AcademicPerformance.id)
        .all()
    )
    secondary = (
        db.query(StudentSecondaryMarksheet)
        .filter(StudentSecondaryMarksheet.student_usn == usn)
        .all()
    )
    marksheets = (
        db.query(AcademicPerformanceMarksheet)
        .filter(AcademicPerformanceMarksheet.student_usn == usn)
        .all()
    )

    secondary_by_standard = {m.standard: m for m in secondary}
    secondary_marksheets_response = {}
    for std in (10, 12):
        if std not in secondary_by_standard:
            continue
        m = secondary_by_standard[std]
        if not _matches_filters(
            document_type=document_type,
            semester=semester,
            verification_status=verification_status,
            academic_year=academic_year,
            uploaded_from=uploaded_from,
            uploaded_to=uploaded_to,
            search=search,
            kind="secondary",
            std=std,
            status=m.verification_status,
            year=m.year_of_passing,
            uploaded_at=m.uploaded_at,
            institution=m.institution_name,
            board=m.board_university,
            doc_type_label=m.document_type or doc_svc.document_type_for_standard(std),
        ):
            continue
        secondary_marksheets_response[std] = _secondary_info(m)

    can_fill_semester = 10 in secondary_by_standard and 12 in secondary_by_standard
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
                is_locked=r.is_locked or False,
            )
        )

    semester_responses = []
    all_sems = set(by_semester.keys()) | set(marksheets_by_semester.keys())
    for sem in sorted(all_sems):
        marksheet_info = None
        if sem in marksheets_by_semester:
            m = marksheets_by_semester[sem]
            if _matches_filters(
                document_type=document_type,
                semester=semester,
                verification_status=verification_status,
                academic_year=academic_year,
                uploaded_from=uploaded_from,
                uploaded_to=uploaded_to,
                search=search,
                kind="semester",
                sem=sem,
                status=m.verification_status,
                year=m.academic_year,
                uploaded_at=m.uploaded_at,
                doc_type_label=f"semester {sem}",
            ):
                marksheet_info = _semester_marksheet_info(m)
            elif any([document_type, semester, verification_status, academic_year, uploaded_from, uploaded_to, search]):
                # Filtered out marksheet; still show rows if no semester filter mismatch
                if semester is not None and semester != sem:
                    continue
                marksheet_info = None
        if semester is not None and sem != semester and not by_semester.get(sem):
            continue
        semester_responses.append(
            AcademicPerformanceSemesterResponse(
                semester=sem,
                rows=by_semester.get(sem, []),
                marksheet=marksheet_info,
            )
        )

    summary = _build_documents_summary(db, usn, max_semesters, secondary, marksheets)

    return AcademicPerformanceResponse(
        submitted_at=None,
        max_semesters=max_semesters,
        can_fill_semester=can_fill_semester,
        secondary_marksheets=secondary_marksheets_response,
        semesters=semester_responses,
        documents_summary=summary,
    )


@router.get(
    "/academic-performance",
    response_model=AcademicPerformanceResponse,
    summary="Get academic performance and documents",
    description="Returns course rows, 10th/12th and semester marksheets with verification metadata. Supports filters.",
)
def get_academic_performance(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
    document_type: Optional[str] = Query(None, description="10th, 12th, semester, or graduation"),
    semester: Optional[int] = Query(None, ge=1, le=8),
    verification_status: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    uploaded_from: Optional[datetime] = Query(None),
    uploaded_to: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None, description="Search institution/board/year"),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return _build_academic_response(
        db,
        student,
        document_type=document_type,
        semester=semester,
        verification_status=verification_status,
        academic_year=academic_year,
        uploaded_from=uploaded_from,
        uploaded_to=uploaded_to,
        search=search,
    )


@router.get(
    "/academic-performance/reports/summary",
    response_model=AcademicDocumentsSummary,
    summary="Academic records summary report",
)
def academic_records_summary(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    max_semesters = _max_semesters_for_program(student.student_program)
    secondary = db.query(StudentSecondaryMarksheet).filter(StudentSecondaryMarksheet.student_usn == student_usn.strip()).all()
    marksheets = db.query(AcademicPerformanceMarksheet).filter(AcademicPerformanceMarksheet.student_usn == student_usn.strip()).all()
    return _build_documents_summary(db, student_usn, max_semesters, secondary, marksheets)


@router.post("/academic-performance/rows", response_model=AcademicPerformanceResponse)
def add_academic_performance_row(
    student_usn: str,
    data: AcademicPerformanceAddRow,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
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
        is_locked=True,
    )
    db.add(rec)
    db.commit()
    return _build_academic_response(db, student)


@router.put("/academic-performance/rows/{row_id}", response_model=AcademicPerformanceResponse)
def update_academic_performance_row(
    student_usn: str,
    row_id: int,
    data: AcademicPerformanceUpdateRow,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
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
    row.is_locked = True
    db.commit()
    return _build_academic_response(db, student)


@router.delete("/academic-performance/rows/{row_id}", response_model=AcademicPerformanceResponse)
def delete_academic_performance_row(
    student_usn: str,
    row_id: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
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
    return _build_academic_response(db, student)


@router.post(
    "/academic-performance/marksheet/{semester}",
    summary="Upload or replace semester marksheet",
    description="Upload PDF/JPG/PNG (max 20MB) with optional SGPA/CGPA metadata. Blocked if verified.",
)
async def upload_marksheet(
    student_usn: str,
    semester: int,
    file: UploadFile = File(...),
    sgpa: Optional[str] = Form(None),
    cgpa: Optional[str] = Form(None),
    percentage: Optional[str] = Form(None),
    total_credits: Optional[str] = Form(None),
    backlogs: Optional[str] = Form(None),
    result_status: Optional[str] = Form(None),
    academic_year: Optional[str] = Form(None),
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")

    content, file_extension, content_type = await doc_svc.validate_and_read_upload(file)
    fhash = doc_svc.file_hash(content)

    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    _require_secondary_marksheets(db, student_usn)
    max_semesters = _max_semesters_for_program(student.student_program)
    if semester < 1 or semester > max_semesters:
        raise HTTPException(status_code=400, detail=f"Invalid semester. Allowed 1-{max_semesters} for your program.")

    existing = db.query(AcademicPerformanceMarksheet).filter(
        AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
        AcademicPerformanceMarksheet.semester == semester,
    ).first()
    if existing and not doc_svc.can_modify_document(existing):
        raise HTTPException(
            status_code=400,
            detail="Document is verified and cannot be replaced. Contact administrator for re-upload permission.",
        )

    doc_svc.check_duplicate_hash(
        db,
        AcademicPerformanceMarksheet,
        student_usn,
        fhash,
        exclude_id=existing.id if existing else None,
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    s3_file_name = f"marksheets/{student_usn}/semester_{semester}_{timestamp}{file_extension}"
    try:
        file_url = doc_svc.upload_bytes_to_storage(content, s3_file_name, content_type)
        if existing:
            doc_svc.delete_stored_document(existing.marksheet_url)
            existing.marksheet_url = file_url
            existing.updated_at = datetime.utcnow()
            existing.file_hash = fhash
            existing.uploaded_by = student_usn.strip()
            existing.verification_status = "pending"
            existing.verified_by = None
            existing.verified_at = None
            if sgpa is not None:
                existing.sgpa = sgpa.strip() or None
            if cgpa is not None:
                existing.cgpa = cgpa.strip() or None
            if percentage is not None:
                existing.percentage = percentage.strip() or None
            if total_credits is not None:
                existing.total_credits = total_credits.strip() or None
            if backlogs is not None:
                existing.backlogs = backlogs.strip() or None
            if result_status is not None:
                existing.result_status = result_status.strip() or None
            if academic_year is not None:
                existing.academic_year = academic_year.strip() or None
        else:
            db.add(
                AcademicPerformanceMarksheet(
                    student_usn=student_usn.strip(),
                    semester=semester,
                    marksheet_url=file_url,
                    sgpa=(sgpa or "").strip() or None,
                    cgpa=(cgpa or "").strip() or None,
                    percentage=(percentage or "").strip() or None,
                    total_credits=(total_credits or "").strip() or None,
                    backlogs=(backlogs or "").strip() or None,
                    result_status=(result_status or "").strip() or None,
                    academic_year=(academic_year or "").strip() or None,
                    verification_status="pending",
                    uploaded_by=student_usn.strip(),
                    file_hash=fhash,
                )
            )
        db.commit()
        return {"message": "Marksheet uploaded successfully", "semester": semester, "marksheet_url": file_url}
    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to upload marksheet: {str(e)}")


@router.patch(
    "/academic-performance/marksheet/{semester}",
    summary="Update semester marksheet metadata",
)
def update_marksheet_metadata(
    student_usn: str,
    semester: int,
    data: SemesterMarksheetMetadataUpdate,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    row = db.query(AcademicPerformanceMarksheet).filter(
        AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
        AcademicPerformanceMarksheet.semester == semester,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Marksheet not found for this semester")
    if not doc_svc.can_modify_document(row):
        raise HTTPException(status_code=400, detail="Verified documents cannot be edited.")
    for field in ("sgpa", "cgpa", "percentage", "total_credits", "backlogs", "result_status", "academic_year"):
        val = getattr(data, field)
        if val is not None:
            setattr(row, field, val.strip() or None)
    row.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Marksheet metadata updated", "marksheet": _semester_marksheet_info(row)}


@router.delete(
    "/academic-performance/marksheet/{semester}",
    summary="Delete semester marksheet",
    description="Allowed only when status is pending, rejected, or reupload_required.",
)
def delete_marksheet(
    student_usn: str,
    semester: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    row = db.query(AcademicPerformanceMarksheet).filter(
        AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
        AcademicPerformanceMarksheet.semester == semester,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Marksheet not found for this semester")
    if not doc_svc.can_modify_document(row):
        raise HTTPException(status_code=400, detail="Verified documents cannot be deleted.")
    doc_svc.delete_stored_document(row.marksheet_url)
    db.delete(row)
    db.commit()
    return {"message": "Marksheet deleted successfully"}


@router.get(
    "/academic-performance/marksheet/{semester}",
    summary="View semester marksheet URL",
)
def get_marksheet(
    student_usn: str,
    semester: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    marksheet = db.query(AcademicPerformanceMarksheet).filter(
        AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
        AcademicPerformanceMarksheet.semester == semester,
    ).first()
    if not marksheet:
        raise HTTPException(status_code=404, detail="Marksheet not found for this semester")
    info = _semester_marksheet_info(marksheet)
    return info.model_dump() if hasattr(info, "model_dump") else info.dict()


@router.get(
    "/academic-performance/marksheet/{semester}/download",
    summary="Download semester marksheet",
)
def download_marksheet(
    student_usn: str,
    semester: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    marksheet = db.query(AcademicPerformanceMarksheet).filter(
        AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
        AcademicPerformanceMarksheet.semester == semester,
    ).first()
    if not marksheet:
        raise HTTPException(status_code=404, detail="Marksheet not found for this semester")
    return {
        "semester": semester,
        "download_url": _get_marksheet_view_url(marksheet.marksheet_url),
        "filename": f"semester_{semester}_marksheet",
    }


@router.post(
    "/academic-performance/secondary-marksheet/{standard}",
    summary="Upload or replace 10th/12th marksheet",
)
async def upload_secondary_marksheet(
    student_usn: str,
    standard: int,
    file: UploadFile = File(...),
    board_university: Optional[str] = Form(None),
    institution_name: Optional[str] = Form(None),
    year_of_passing: Optional[str] = Form(None),
    percentage_cgpa: Optional[str] = Form(None),
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    if standard not in (10, 12):
        raise HTTPException(status_code=400, detail="Standard must be 10 or 12")

    content, file_extension, content_type = await doc_svc.validate_and_read_upload(file)
    fhash = doc_svc.file_hash(content)

    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = (
        db.query(StudentSecondaryMarksheet)
        .filter(
            StudentSecondaryMarksheet.student_usn == student_usn.strip(),
            StudentSecondaryMarksheet.standard == standard,
        )
        .first()
    )
    if existing and not doc_svc.can_modify_document(existing):
        raise HTTPException(
            status_code=400,
            detail="Document is verified and cannot be replaced. Contact administrator for re-upload permission.",
        )
    doc_svc.check_duplicate_hash(
        db,
        StudentSecondaryMarksheet,
        student_usn,
        fhash,
        exclude_id=existing.id if existing else None,
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    s3_file_name = f"marksheets/{student_usn}/secondary_{standard}_{timestamp}{file_extension}"
    try:
        file_url = doc_svc.upload_bytes_to_storage(content, s3_file_name, content_type)
        if existing:
            doc_svc.delete_stored_document(existing.marksheet_url)
            existing.marksheet_url = file_url
            existing.updated_at = datetime.utcnow()
            existing.file_hash = fhash
            existing.uploaded_by = student_usn.strip()
            existing.document_type = doc_svc.document_type_for_standard(standard)
            existing.verification_status = "pending"
            existing.verified_by = None
            existing.verified_at = None
            if board_university is not None:
                existing.board_university = board_university.strip() or None
            if institution_name is not None:
                existing.institution_name = institution_name.strip() or None
            if year_of_passing is not None:
                existing.year_of_passing = year_of_passing.strip() or None
            if percentage_cgpa is not None:
                existing.percentage_cgpa = percentage_cgpa.strip() or None
        else:
            db.add(
                StudentSecondaryMarksheet(
                    student_usn=student_usn.strip(),
                    standard=standard,
                    marksheet_url=file_url,
                    document_type=doc_svc.document_type_for_standard(standard),
                    board_university=(board_university or "").strip() or None,
                    institution_name=(institution_name or "").strip() or None,
                    year_of_passing=(year_of_passing or "").strip() or None,
                    percentage_cgpa=(percentage_cgpa or "").strip() or None,
                    verification_status="pending",
                    uploaded_by=student_usn.strip(),
                    file_hash=fhash,
                )
            )
        db.commit()
        return {
            "message": f"{standard}th standard marksheet uploaded successfully",
            "standard": standard,
            "marksheet_url": file_url,
        }
    except HTTPException:
        raise
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Failed to upload marksheet: {str(e)}")


@router.patch(
    "/academic-performance/secondary-marksheet/{standard}",
    summary="Update 10th/12th marksheet metadata",
)
def update_secondary_metadata(
    student_usn: str,
    standard: int,
    data: SecondaryMarksheetMetadataUpdate,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
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
    if not doc_svc.can_modify_document(row):
        raise HTTPException(status_code=400, detail="Verified documents cannot be edited.")
    for field in ("board_university", "institution_name", "year_of_passing", "percentage_cgpa"):
        val = getattr(data, field)
        if val is not None:
            setattr(row, field, val.strip() or None)
    row.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Metadata updated", "marksheet": _secondary_info(row)}


@router.delete(
    "/academic-performance/secondary-marksheet/{standard}",
    summary="Delete 10th/12th marksheet",
)
def delete_secondary_marksheet(
    student_usn: str,
    standard: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
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
    if not doc_svc.can_modify_document(row):
        raise HTTPException(status_code=400, detail="Verified documents cannot be deleted.")
    doc_svc.delete_stored_document(row.marksheet_url)
    db.delete(row)
    db.commit()
    return {"message": f"{standard}th marksheet deleted successfully"}


@router.get(
    "/academic-performance/secondary-marksheet/{standard}",
    summary="View 10th/12th marksheet URL",
)
def get_secondary_marksheet(
    student_usn: str,
    standard: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
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
    info = _secondary_info(row)
    return info.model_dump() if hasattr(info, "model_dump") else info.dict()


@router.get(
    "/academic-performance/secondary-marksheet/{standard}/download",
    summary="Download 10th/12th marksheet",
)
def download_secondary_marksheet(
    student_usn: str,
    standard: int,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
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
    return {
        "standard": standard,
        "download_url": _get_marksheet_view_url(row.marksheet_url),
        "filename": f"{standard}th_marksheet",
    }
