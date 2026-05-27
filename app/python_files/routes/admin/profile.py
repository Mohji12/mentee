from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.admin import Admin

router = APIRouter()

@router.get("/profile")
def get_admin_profile(admin_id: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter_by(admin_id=admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin with ID {admin_id} not found")

    # Return mentor details
    return {
        "admin_id": admin.admin_id,
        "admin_name": admin.admin_name,
        "admin_department": admin.admin_department,
        "admin_email": admin.admin_email,
        "admin_phoneno": admin.admin_phoneno,
        "admin_campus":admin.admin_campus
    }
