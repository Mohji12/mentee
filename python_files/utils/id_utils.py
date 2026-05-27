from sqlalchemy.orm import Session
from app.db.models.query import Query
import random, string, datetime
from datetime import datetime

# Helper function to generate OTP
def generate_otp(length: int = 6) -> str:
    # Use only digits
    character_set = string.digits
    otp = ''.join(random.choices(character_set, k=length))
    return otp

# Helper function to generate mentor ID
def generate_mentor_id() -> str:
    # Generate mentor ID as "JUM" followed by timestamp (7 digits)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    mentor_id = f"JUM{timestamp[-7:]}"  # Ensure it is 10 digits
    return mentor_id

def generate_activity_id():
    """Generate a unique activity ID in the format 'ACT' + 12 random characters."""
    return "ACT" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

# ✅ Function to generate unique Query ID
def generate_query_id(db: Session):
    date_str = datetime.now().strftime("%Y%m%d")  # Format: YYYYMMDD
    last_query = db.query(Query).order_by(Query.id.desc()).first()

    if last_query:
        last_id = last_query.id[-3:]  # Get last 3 digits of ID
        new_id_num = str(int(last_id) + 1).zfill(3)  # Increment & pad with zeros
    else:
        new_id_num = "001"

    return f"Q2024{date_str}{new_id_num}"  # Format: Q2024YYYYMMDDXXX