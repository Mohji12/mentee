from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_mentor
from app.db.database import get_db
from app.db.models.internal_marks import InternalMarksImportBatch, InternalMarksEntry
from app.db.models.students import Student
from app.schemas.internal_marks import (
    InternalMarksBatchListItem,
    InternalMarksBatchMeta,
    InternalMarksImportResult,
    InternalMarksMatrixResponse,
    MatrixComponent,
    MatrixStudentRow,
    MatrixSubject,
    FlatColumn,
)
from app.services.internal_marks_import import run_internal_marks_import

router = APIRouter()


def _assigned_usn_set(db: Session, mentor_id: str) -> Set[str]:
    return set(_assigned_usns(db, mentor_id))


def _assigned_usns(db: Session, mentor_id: str) -> List[str]:
    rows = (
        db.query(Student.student_usn)
        .filter(Student.assigned_mentor == mentor_id)
        .order_by(Student.student_usn)
        .all()
    )
    return [r[0] for r in rows]


def _pick_batch_id(
    db: Session,
    semester: int,
    mentor_usns: List[str],
    batch_id: Optional[int],
    section_code: Optional[str],
) -> Optional[int]:
    if not mentor_usns:
        return None
    if batch_id is not None:
        b = db.query(InternalMarksImportBatch).filter(InternalMarksImportBatch.id == batch_id).first()
        if not b:
            raise HTTPException(status_code=404, detail="Batch not found")
        if b.semester != semester:
            raise HTTPException(status_code=400, detail="Batch semester does not match query semester")
        return batch_id

    q = (
        db.query(InternalMarksImportBatch.id)
        .join(InternalMarksEntry, InternalMarksEntry.batch_id == InternalMarksImportBatch.id)
        .filter(
            InternalMarksImportBatch.semester == semester,
            InternalMarksEntry.semester == semester,
            InternalMarksEntry.student_usn.in_(mentor_usns),
        )
    )
    if section_code:
        q = q.filter(InternalMarksImportBatch.section_code == section_code)

    row = q.order_by(desc(InternalMarksImportBatch.id)).first()
    return row[0] if row else None


@router.post("/internal-marks/import", response_model=InternalMarksImportResult)
async def mentor_import_internal_marks(
    mentor_id: str,
    semester: int = Form(..., ge=1, le=8),
    file: UploadFile = File(...),
    section_code: Optional[str] = Form(None),
    program_label: Optional[str] = Form(None),
    branch_label: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    academic_year: Optional[str] = Form(None),
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Mentor-only: import CSV/Excel. Only rows for students assigned to this mentor are accepted."""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    allowed = _assigned_usn_set(db, mentor_id)
    if not allowed:
        raise HTTPException(
            status_code=400,
            detail="You have no assigned students; nothing can be imported.",
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        batch, ins, upd, skip, errors, warnings = run_internal_marks_import(
            db,
            semester=semester,
            file_bytes=raw,
            filename=file.filename or "",
            section_code=section_code,
            program_label=program_label,
            branch_label=branch_label,
            title=title,
            academic_year=academic_year,
            created_by=mentor_id,
            allowed_student_usns=allowed,
            reject_reason_not_allowed="student is not assigned to you",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return InternalMarksImportResult(
        batch_id=batch.id,
        rows_inserted=ins,
        rows_updated=upd,
        rows_skipped=skip,
        errors=errors,
        warnings=warnings,
    )


@router.get("/internal-marks/batches", response_model=List[InternalMarksBatchListItem])
def list_internal_marks_batches(
    mentor_id: str,
    semester: int = Query(..., ge=1, le=8),
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    usns = _assigned_usns(db, mentor_id)
    if not usns:
        return []

    subq = (
        db.query(
            InternalMarksEntry.batch_id,
            func.count(InternalMarksEntry.id).label("cnt"),
        )
        .filter(
            InternalMarksEntry.semester == semester,
            InternalMarksEntry.student_usn.in_(usns),
        )
        .group_by(InternalMarksEntry.batch_id)
        .subquery()
    )

    rows = (
        db.query(InternalMarksImportBatch, subq.c.cnt)
        .join(subq, InternalMarksImportBatch.id == subq.c.batch_id)
        .filter(InternalMarksImportBatch.semester == semester)
        .order_by(desc(InternalMarksImportBatch.id))
        .all()
    )

    out: List[InternalMarksBatchListItem] = []
    for b, cnt in rows:
        out.append(
            InternalMarksBatchListItem(
                id=b.id,
                semester=b.semester,
                section_code=b.section_code,
                title=b.title,
                created_at=b.created_at.isoformat() if b.created_at else None,
                row_count=int(cnt or 0),
            )
        )
    return out


@router.get("/internal-marks/matrix", response_model=InternalMarksMatrixResponse)
def get_internal_marks_matrix(
    mentor_id: str,
    semester: int = Query(..., ge=1, le=8),
    batch_id: Optional[int] = Query(None),
    section_code: Optional[str] = Query(None),
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    students = (
        db.query(Student)
        .filter(Student.assigned_mentor == mentor_id)
        .order_by(Student.student_usn)
        .all()
    )
    if not students:
        return InternalMarksMatrixResponse(batch=None, subjects=[], flat_columns=[], students=[])

    usns = [s.student_usn for s in students]
    bid = _pick_batch_id(db, semester, usns, batch_id, section_code)
    if bid is None:
        return InternalMarksMatrixResponse(batch=None, subjects=[], flat_columns=[], students=[])

    batch = db.query(InternalMarksImportBatch).filter(InternalMarksImportBatch.id == bid).first()
    if not batch:
        return InternalMarksMatrixResponse(batch=None, subjects=[], flat_columns=[], students=[])

    entries = (
        db.query(InternalMarksEntry)
        .filter(
            InternalMarksEntry.batch_id == bid,
            InternalMarksEntry.semester == semester,
            InternalMarksEntry.student_usn.in_(usns),
        )
        .all()
    )

    # Build column structure: subject_code -> ordered components
    subject_names: Dict[str, Optional[str]] = {}
    components_by_subject: Dict[str, Dict[str, Tuple[str, int]]] = defaultdict(dict)
    for e in entries:
        if e.subject_name:
            subject_names[e.subject_code] = e.subject_name
        elif e.subject_code not in subject_names:
            subject_names[e.subject_code] = None
        ck = e.component_key
        if ck not in components_by_subject[e.subject_code]:
            components_by_subject[e.subject_code][ck] = (e.component_label, e.sort_order)

    subject_codes_sorted = sorted(components_by_subject.keys())

    flat_columns: List[FlatColumn] = []
    subjects_out: List[MatrixSubject] = []

    for sc in subject_codes_sorted:
        comp_map = components_by_subject[sc]
        comp_items = sorted(
            comp_map.items(),
            key=lambda x: (x[1][1], x[0]),
        )
        comps: List[MatrixComponent] = []
        for ckey, (clabel, sord) in comp_items:
            comps.append(
                MatrixComponent(
                    component_key=ckey,
                    component_label=clabel,
                    sort_order=sord,
                )
            )
            flat_columns.append(
                FlatColumn(
                    subject_code=sc,
                    subject_name=subject_names.get(sc),
                    component_key=ckey,
                    component_label=clabel,
                    sort_order=sord,
                )
            )
        subjects_out.append(
            MatrixSubject(
                subject_code=sc,
                subject_name=subject_names.get(sc),
                components=comps,
            )
        )

    # score lookup: (usn, subj, comp_key) -> score
    score_map: Dict[Tuple[str, str, str], Optional[str]] = {}
    for e in entries:
        score_map[(e.student_usn, e.subject_code, e.component_key)] = e.score

    student_rows: List[MatrixStudentRow] = []
    for st in students:
        scores: List[Optional[str]] = []
        for fc in flat_columns:
            scores.append(score_map.get((st.student_usn, fc.subject_code, fc.component_key)))
        student_rows.append(
            MatrixStudentRow(
                student_usn=st.student_usn,
                student_name=st.student_name,
                scores=scores,
            )
        )

    batch_meta = InternalMarksBatchMeta(
        id=batch.id,
        semester=batch.semester,
        section_code=batch.section_code,
        program_label=batch.program_label,
        branch_label=batch.branch_label,
        title=batch.title,
        academic_year=batch.academic_year,
    )

    return InternalMarksMatrixResponse(
        batch=batch_meta,
        subjects=subjects_out,
        flat_columns=flat_columns,
        students=student_rows,
    )
