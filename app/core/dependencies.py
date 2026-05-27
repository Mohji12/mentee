from fastapi import HTTPException, Depends
from typing import Dict, List, Any
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.committee_member import CommitteeMember
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Dependency to get the current user from the JWT token."""
    try:
        payload = verify_token(token)  # Use the verify_token function
        user_id: str = payload.get("ms_ids")  # Extract the user ID (ms_ids)
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID missing in token")
        return {"user_id": user_id}  # Return the user data (extend with more details if needed)
    except HTTPException as e:
        raise e  # If token verification fails, pass the exception to the router
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

async def get_current_student(token: str = Depends(oauth2_scheme)) -> Dict:
    """Dependency to get the current student from the JWT token."""
    try:
        payload = verify_token(token)
        student_usn: str = payload.get("ms_ids")
        if not student_usn:
            raise HTTPException(status_code=401, detail="Student USN missing in token")
        return {"student_usn": student_usn}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

async def get_current_mentor(token: str = Depends(oauth2_scheme)) -> Dict:
    """Dependency to get the current mentor from the JWT token."""
    try:
        payload = verify_token(token)
        mentor_id: str = payload.get("ms_ids")
        if not mentor_id:
            raise HTTPException(status_code=401, detail="Mentor ID missing in token")
        return {"mentor_id": mentor_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")


async def get_current_admin(token: str = Depends(oauth2_scheme)) -> Dict:
    """Dependency to get the current admin from the JWT token."""
    try:
        payload = verify_token(token)
        admin_id: str = payload.get("ms_ids")
        role: str = payload.get("role", "")
        if not admin_id:
            raise HTTPException(status_code=401, detail="Admin ID missing in token")
        if role not in ["admin", "leader", "hod"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        return {"admin_id": admin_id, "role": role}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")


async def get_current_leader(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Dependency for leader role only. Returns leader id from JWT."""
    payload = verify_token(token)
    role = payload.get("role")
    ms_ids = payload.get("ms_ids")
    if role != "leader" or not ms_ids:
        raise HTTPException(status_code=403, detail="Leader access required")
    return {"leader_id": ms_ids, "role": "leader"}


async def get_current_working_committee(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Dependency for working_committee role. Returns member id and allocated_departments."""
    payload = verify_token(token)
    role = payload.get("role")
    ms_ids = payload.get("ms_ids")
    if role != "working_committee" or not ms_ids:
        raise HTTPException(status_code=403, detail="Working committee access required")
    member = db.query(CommitteeMember).filter_by(id=ms_ids).first()
    if not member:
        raise HTTPException(status_code=403, detail="Committee member not found")
    allocated = []
    if member.allocated_departments:
        try:
            allocated = json.loads(member.allocated_departments) if isinstance(member.allocated_departments, str) else member.allocated_departments
        except (json.JSONDecodeError, TypeError):
            allocated = []
    return {"member_id": ms_ids, "role": "working_committee", "allocated_departments": allocated}


async def get_current_department_faculty(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Dependency for department_faculty role. Returns member id and department."""
    payload = verify_token(token)
    role = payload.get("role")
    ms_ids = payload.get("ms_ids")
    if role != "department_faculty" or not ms_ids:
        raise HTTPException(status_code=403, detail="Department faculty access required")
    member = db.query(CommitteeMember).filter_by(id=ms_ids).first()
    if not member:
        raise HTTPException(status_code=403, detail="Committee member not found")
    return {"member_id": ms_ids, "role": "department_faculty", "department": member.department or ""}


async def get_current_hod(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Dependency for HOD role. Returns member id and department."""
    payload = verify_token(token)
    role = payload.get("role")
    ms_ids = payload.get("ms_ids")
    if role != "hod" or not ms_ids:
        raise HTTPException(status_code=403, detail="HOD access required")
    member = db.query(CommitteeMember).filter_by(id=ms_ids).first()
    if not member:
        raise HTTPException(status_code=403, detail="Committee member not found")
    return {"member_id": ms_ids, "role": "hod", "department": member.department or ""}


async def get_current_program_faculty(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Dependency for program_faculty role. Returns member id and allocated_programs."""
    payload = verify_token(token)
    role = payload.get("role")
    ms_ids = payload.get("ms_ids")
    if role != "program_faculty" or not ms_ids:
        raise HTTPException(status_code=403, detail="Program faculty access required")
    member = db.query(CommitteeMember).filter_by(id=ms_ids).first()
    if not member:
        raise HTTPException(status_code=403, detail="Committee member not found")
    allocated = []
    if member.allocated_programs:
        try:
            allocated = json.loads(member.allocated_programs) if isinstance(member.allocated_programs, str) else member.allocated_programs
        except (json.JSONDecodeError, TypeError):
            allocated = []
    return {"member_id": ms_ids, "role": "program_faculty", "allocated_programs": allocated}