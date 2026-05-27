from fastapi import HTTPException, Depends
from typing import Dict
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token

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