from fastapi import HTTPException
import bcrypt, re

# Helper function to hash passwords
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def validate_password(password: str):
    """
    Validates the given password based on predefined rules:
    - Minimum length of 8 characters
    - Contains at least one lowercase letter
    - Contains at least one uppercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if len(password) > 20:
        raise HTTPException(status_code=400, detail="Password must not exceed 20 characters.")
    if not re.search(r'[a-z]', password):  # Lowercase letter
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r'[A-Z]', password):  # Uppercase letter
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r'[0-9]', password):  # Digit
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Special character
        raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
    return True  # Password is valid
