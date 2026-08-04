"""Shared helpers for academic document upload, validation, and verification."""
from __future__ import annotations

import hashlib
import io
from datetime import datetime
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.models.notifications import Notification
from app.services.s3bucket import get_document_url, s3_client

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

MODIFIABLE_STATUSES = {"pending", "rejected", "reupload_required"}


def can_modify_document(record) -> bool:
    status = (getattr(record, "verification_status", None) or "pending").lower()
    return status in MODIFIABLE_STATUSES


def _extension_from_filename(filename: str) -> Optional[str]:
    if not filename or "." not in filename:
        return None
    return "." + filename.rsplit(".", 1)[-1].lower()


def _validate_magic_bytes(content: bytes, extension: str) -> None:
    if not content or len(content) < 4:
        raise HTTPException(status_code=400, detail="File appears to be corrupted or empty.")
    if extension == ".pdf":
        if not content.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="Corrupted or invalid PDF file.")
    elif extension in {".jpg", ".jpeg"}:
        if not content.startswith(b"\xff\xd8\xff"):
            raise HTTPException(status_code=400, detail="Corrupted or invalid JPEG file.")
    elif extension == ".png":
        if not content.startswith(b"\x89PNG\r\n\x1a\n"):
            raise HTTPException(status_code=400, detail="Corrupted or invalid PNG file.")


async def validate_and_read_upload(file: UploadFile) -> Tuple[bytes, str, str]:
    """Validate type/size/corruption and return (content, extension, content_type)."""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    extension = _extension_from_filename(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: PDF, JPG, JPEG, PNG.",
        )

    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        # Some browsers send empty/octet-stream; allow if extension is valid
        if content_type not in ("application/octet-stream", ""):
            raise HTTPException(
                status_code=400,
                detail="Invalid content type. Allowed: PDF, JPG, JPEG, PNG.",
            )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 20 MB limit.")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File appears to be corrupted or empty.")

    _validate_magic_bytes(content, extension)
    return content, extension, content_type or "application/octet-stream"


def file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def check_duplicate_hash(
    db: Session,
    model,
    student_usn: str,
    file_hash_value: str,
    *,
    exclude_id: Optional[int] = None,
) -> None:
    """Reject if the same file hash already exists for this student on this model."""
    if not file_hash_value:
        return
    q = db.query(model).filter(
        model.student_usn == student_usn.strip(),
        model.file_hash == file_hash_value,
    )
    if exclude_id is not None:
        q = q.filter(model.id != exclude_id)
    existing = q.first()
    if existing:
        raise HTTPException(status_code=400, detail="This document is already uploaded (duplicate file).")


def upload_bytes_to_storage(content: bytes, key: str, content_type: str) -> str:
    return s3_client.upload_fileobj(
        io.BytesIO(content),
        None,
        key,
        ExtraArgs={"ContentType": content_type},
    )


def delete_stored_document(stored_url: Optional[str]) -> None:
    if not stored_url:
        return
    try:
        s3_client.delete_object(Key=stored_url)
    except Exception as exc:
        print(f"Warning: failed to delete document {stored_url}: {exc}")


def get_view_url(stored_url: Optional[str]) -> str:
    return get_document_url(stored_url) if stored_url else ""


def notify_student_academic(
    db: Session,
    student_usn: str,
    title: str,
    message: str,
    link: Optional[str] = None,
) -> None:
    db.add(
        Notification(
            student_usn=student_usn.strip(),
            title=title,
            message=message,
            category="academic",
            is_read=False,
            created_at=datetime.utcnow(),
            link=link,
        )
    )


def apply_verification(
    record,
    action: str,
    remarks: Optional[str],
    verified_by: str,
) -> str:
    """Apply verify/reject/request_reupload to a marksheet record. Returns new status."""
    action_l = (action or "").strip().lower()
    if action_l not in {"verify", "reject", "request_reupload"}:
        raise HTTPException(
            status_code=400,
            detail="action must be one of: verify, reject, request_reupload",
        )
    if action_l == "verify":
        record.verification_status = "verified"
    elif action_l == "reject":
        record.verification_status = "rejected"
    else:
        record.verification_status = "reupload_required"
    record.remarks = remarks.strip() if remarks else record.remarks
    record.verified_by = verified_by
    record.verified_at = datetime.utcnow()
    return record.verification_status


def document_type_for_standard(standard: int) -> str:
    return "10th" if standard == 10 else "12th"
