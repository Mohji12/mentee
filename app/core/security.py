from fastapi import HTTPException
import datetime
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
import uuid

# Secret key for encoding/decoding JWT (use a strong, unique key in production)
SECRET_KEY = "menteetracker"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 145  # Token validity

def verify_token(token: str):
    """Verify the JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(status_code=401, detail="JTI missing in token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Helper Functions to Generate and Verify Tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with expiration and a unique JWT ID (jti)."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    jti = str(uuid.uuid4())  # Generate a unique identifier
    to_encode.update({"exp": expire, "jti": jti})  # Add the jti and expiration to the payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti
    
