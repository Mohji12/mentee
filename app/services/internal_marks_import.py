"""Shared CSV/Excel parsing and DB write for internal marks imports."""
import io
import re
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from app.db.models.internal_marks import InternalMarksImportBatch, InternalMarksEntry
from app.db.models.students import Student


def slug_component(label: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (label or "").lower().strip())
    s = s.strip("_")
    return s or "component"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for c in df.columns:
        key = str(c).strip().lower().replace(" ", "_").replace("-", "_")
        mapping[c] = key
    return df.rename(columns=mapping)


def parse_internal_marks_file(raw: bytes, filename: str) -> pd.DataFrame:
    name = (filename or "").lower()
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(io.BytesIO(raw))
    return pd.read_csv(io.BytesIO(raw))


def run_internal_marks_import(
    db: Session,
    *,
    semester: int,
    file_bytes: bytes,
    filename: str,
    section_code: Optional[str],
    program_label: Optional[str],
    branch_label: Optional[str],
    title: Optional[str],
    academic_year: Optional[str],
    created_by: str,
    allowed_student_usns: Optional[Set[str]],
    reject_reason_not_allowed: str = "student is not assigned to you",
) -> Tuple[InternalMarksImportBatch, int, int, int, List[str], List[str]]:
    """
    If allowed_student_usns is set, rows for other USNs are skipped with errors.
    Returns (batch, rows_inserted, rows_updated, rows_skipped, errors, warnings).
    """
    df = parse_internal_marks_file(file_bytes, filename)
    if df.empty:
        raise ValueError("No rows in file")

    df = normalize_columns(df)
    col_map = {str(c).strip().lower().replace(" ", "_").replace("-", "_"): c for c in df.columns}

    def col(*names: str):
        for n in names:
            n = n.lower().replace(" ", "_").replace("-", "_")
            if n in col_map:
                return col_map[n]
        return None

    c_usn = col("student_usn", "usn", "student_code", "studentcode")
    c_subj = col("subject_code", "course_code", "subjectcode")
    c_comp = col("component_label", "component", "assessment", "assessment_type")
    c_score = col("score", "marks", "value")
    c_subj_name = col("subject_name", "course_name", "subject_title")

    if not c_usn or not c_subj or not c_comp or not c_score:
        raise ValueError(
            "Missing required columns. Need: student_usn (or usn/student_code), subject_code, "
            "component_label (or component), score (or marks). Optional: subject_name."
        )

    batch = InternalMarksImportBatch(
        semester=semester,
        section_code=(section_code or None),
        program_label=(program_label or None),
        branch_label=(branch_label or None),
        title=(title or None),
        academic_year=(academic_year or None),
        created_by=created_by,
    )
    db.add(batch)
    db.flush()

    component_order: Dict[Tuple[str, str], int] = {}
    next_idx: Dict[str, int] = {}

    errors: List[str] = []
    warnings: List[str] = []
    rows_inserted = 0
    rows_updated = 0
    rows_skipped = 0

    for idx, row in df.iterrows():
        line_no = int(idx) + 2
        try:
            usn = str(row[c_usn]).strip() if pd.notna(row[c_usn]) else ""
            subj = str(row[c_subj]).strip() if pd.notna(row[c_subj]) else ""
            comp_label = str(row[c_comp]).strip() if pd.notna(row[c_comp]) else ""
            score_val = row[c_score]
            if pd.isna(score_val):
                score_str = None
            else:
                score_str = str(score_val).strip()
                if score_str.lower() in ("nan", "none", ""):
                    score_str = None

            subj_name = None
            if c_subj_name and pd.notna(row.get(c_subj_name)):
                subj_name = str(row[c_subj_name]).strip() or None

            if not usn or not subj or not comp_label:
                rows_skipped += 1
                errors.append(f"Line {line_no}: missing usn, subject_code, or component_label")
                continue

            if allowed_student_usns is not None and usn not in allowed_student_usns:
                rows_skipped += 1
                errors.append(f"Line {line_no}: {reject_reason_not_allowed} ({usn})")
                continue

            st = db.query(Student).filter(Student.student_usn == usn).first()
            if not st:
                rows_skipped += 1
                errors.append(f"Line {line_no}: unknown student_usn {usn}")
                continue

            if allowed_student_usns is None and not st.assigned_mentor:
                warnings.append(f"Line {line_no}: student {usn} has no assigned mentor")

            ckey = slug_component(comp_label)
            pair = (subj, ckey)
            if pair not in component_order:
                cur = next_idx.get(subj, 0)
                component_order[pair] = cur
                next_idx[subj] = cur + 1
            sort_order = component_order[pair]

            existing = (
                db.query(InternalMarksEntry)
                .filter(
                    InternalMarksEntry.batch_id == batch.id,
                    InternalMarksEntry.student_usn == usn,
                    InternalMarksEntry.subject_code == subj,
                    InternalMarksEntry.component_key == ckey,
                )
                .first()
            )
            if existing:
                existing.score = score_str
                existing.component_label = comp_label
                existing.subject_name = subj_name or existing.subject_name
                existing.sort_order = sort_order
                rows_updated += 1
            else:
                db.add(
                    InternalMarksEntry(
                        batch_id=batch.id,
                        student_usn=usn,
                        semester=semester,
                        subject_code=subj,
                        subject_name=subj_name,
                        component_key=ckey,
                        component_label=comp_label,
                        sort_order=sort_order,
                        score=score_str,
                    )
                )
                rows_inserted += 1
        except Exception as e:
            rows_skipped += 1
            errors.append(f"Line {line_no}: {e}")

    db.commit()
    return batch, rows_inserted, rows_updated, rows_skipped, errors[:200], warnings[:200]
