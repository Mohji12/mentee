from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_mentor

router = APIRouter()


@router.get("/students/{student_usn}/pf16-form/download")
def download_student_pf16_excel(
    mentor_id: str,
    student_usn: str,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """16PF Excel download is restricted to admin only. Mentors cannot download."""
    raise HTTPException(
        status_code=403,
        detail="Only admin can download 16PF Excel reports. Please contact your administrator."
    )


@router.get("/students/pf16-form/download-all")
def download_all_assigned_students_pf16_zip(
    mentor_id: str,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """16PF Excel/ZIP download is restricted to admin only. Mentors cannot download."""
    raise HTTPException(
        status_code=403,
        detail="Only admin can download 16PF Excel reports. Please contact your administrator."
    )
