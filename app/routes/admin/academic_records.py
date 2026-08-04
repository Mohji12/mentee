"""Admin academic records verification and reports."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.db.database import get_db
from app.db.models.academic_performance import AcademicPerformanceMarksheet, StudentSecondaryMarksheet
from app.db.models.students import Student
from app.schemas.academic_performance import AcademicDocumentListItem, AcademicRecordVerifyRequest
from app.services import academic_document_service as doc_svc
from app.services.s3bucket import get_document_url

router = APIRouter()


def _view_url(url: str) -> str:
    return get_document_url(url)


def _list_documents(
    db: Session,
    *,
    verification_status: Optional[str] = None,
    document_type: Optional[str] = None,
    student_usn: Optional[str] = None,
    semester: Optional[int] = None,
) -> List[AcademicDocumentListItem]:
    items: list[AcademicDocumentListItem] = []
    students = {s.student_usn: s.student_name for s in db.query(Student).all()}

    sec_q = db.query(StudentSecondaryMarksheet)
    if student_usn:
        sec_q = sec_q.filter(StudentSecondaryMarksheet.student_usn == student_usn.strip())
    if verification_status:
        sec_q = sec_q.filter(func.lower(StudentSecondaryMarksheet.verification_status) == verification_status.lower())
    for m in sec_q.all():
        dtype = m.document_type or doc_svc.document_type_for_standard(m.standard)
        if document_type and document_type.lower() not in {dtype.lower(), str(m.standard), f"{m.standard}th"}:
            continue
        if semester is not None:
            continue
        items.append(
            AcademicDocumentListItem(
                student_usn=m.student_usn,
                student_name=students.get(m.student_usn),
                document_kind="secondary",
                standard=m.standard,
                document_type=dtype,
                verification_status=m.verification_status or "pending",
                uploaded_at=m.uploaded_at,
                marksheet_view_url=_view_url(m.marksheet_url),
                remarks=m.remarks,
                institution_name=m.institution_name,
                board_university=m.board_university,
            )
        )

    sem_q = db.query(AcademicPerformanceMarksheet)
    if student_usn:
        sem_q = sem_q.filter(AcademicPerformanceMarksheet.student_usn == student_usn.strip())
    if verification_status:
        sem_q = sem_q.filter(func.lower(AcademicPerformanceMarksheet.verification_status) == verification_status.lower())
    if semester is not None:
        sem_q = sem_q.filter(AcademicPerformanceMarksheet.semester == semester)
    for m in sem_q.all():
        if document_type and document_type.lower() not in {"semester", "graduation", f"sem{m.semester}", str(m.semester)}:
            continue
        items.append(
            AcademicDocumentListItem(
                student_usn=m.student_usn,
                student_name=students.get(m.student_usn),
                document_kind="semester",
                semester=m.semester,
                document_type=f"Semester {m.semester}",
                verification_status=m.verification_status or "pending",
                uploaded_at=m.uploaded_at,
                marksheet_view_url=_view_url(m.marksheet_url),
                remarks=m.remarks,
                academic_year=m.academic_year,
            )
        )
    items.sort(key=lambda x: x.uploaded_at or datetime.min, reverse=True)
    return items


@router.get(
    "/academic-records",
    summary="List academic documents (admin)",
    description="Filter by verification status, document type, student USN, or semester.",
)
def list_academic_records(
    admin_id: str,
    current: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    verification_status: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    student_usn: Optional[str] = Query(None),
    semester: Optional[int] = Query(None, ge=1, le=8),
):
    if current.get("admin_id") != admin_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return _list_documents(
        db,
        verification_status=verification_status,
        document_type=document_type,
        student_usn=student_usn,
        semester=semester,
    )


@router.get("/academic-records/reports/pending", summary="Pending verification report")
def report_pending(admin_id: str, current: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    if current.get("admin_id") != admin_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return _list_documents(db, verification_status="pending")


@router.get("/academic-records/reports/verified", summary="Verified documents report")
def report_verified(admin_id: str, current: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    if current.get("admin_id") != admin_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return _list_documents(db, verification_status="verified")


@router.get("/academic-records/reports/rejected", summary="Rejected documents report")
def report_rejected(admin_id: str, current: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    if current.get("admin_id") != admin_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return _list_documents(db, verification_status="rejected")


@router.patch(
    "/academic-records/secondary/{student_usn}/{standard}/verify",
    summary="Admin verify/reject/request re-upload for secondary marksheet",
)
def admin_verify_secondary(
    admin_id: str,
    student_usn: str,
    standard: int,
    data: AcademicRecordVerifyRequest,
    current: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if current.get("admin_id") != admin_id:
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
        raise HTTPException(status_code=404, detail="Document not found")
    new_status = doc_svc.apply_verification(row, data.action, data.remarks, admin_id)
    titles = {
        "verified": "Document Approved",
        "rejected": "Document Rejected",
        "reupload_required": "Re-upload Required",
    }
    doc_svc.notify_student_academic(
        db,
        student_usn,
        titles.get(new_status, "Academic Document Update"),
        f"Your {standard}th marksheet status is now '{new_status}'. {data.remarks or ''}".strip(),
        link=f"/student/{student_usn}/academic-performance",
    )
    db.commit()
    return {"message": f"Document marked as {new_status}", "verification_status": new_status}


@router.patch(
    "/academic-records/semester/{student_usn}/{semester}/verify",
    summary="Admin verify/reject/request re-upload for semester marksheet",
)
def admin_verify_semester(
    admin_id: str,
    student_usn: str,
    semester: int,
    data: AcademicRecordVerifyRequest,
    current: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if current.get("admin_id") != admin_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    row = db.query(AcademicPerformanceMarksheet).filter(
        AcademicPerformanceMarksheet.student_usn == student_usn.strip(),
        AcademicPerformanceMarksheet.semester == semester,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    new_status = doc_svc.apply_verification(row, data.action, data.remarks, admin_id)
    titles = {
        "verified": "Document Approved",
        "rejected": "Document Rejected",
        "reupload_required": "Re-upload Required",
    }
    doc_svc.notify_student_academic(
        db,
        student_usn,
        titles.get(new_status, "Academic Document Update"),
        f"Your semester {semester} marksheet status is now '{new_status}'. {data.remarks or ''}".strip(),
        link=f"/student/{student_usn}/academic-performance",
    )
    db.commit()
    return {"message": f"Document marked as {new_status}", "verification_status": new_status}
