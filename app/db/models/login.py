from sqlalchemy import Column, String, Integer, DateTime
from app.db.database import Base
from datetime import datetime, timezone

class Login(Base):
    __tablename__ = 'login'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    ms_ids = Column(String(255), nullable=False)  # User ID (ms_ids, student_usn, or mentor_id)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))  # Updated for Lambda compatibility
    exp_timestamp = Column(DateTime, nullable=False)  # Expiration timestamp
    access_token = Column(String(500), nullable=False)  # Access token for the login session
    jti = Column(String(255), nullable=False)  # JWT ID for uniquely identifying the token

    def __repr__(self):
        return f"<Login(ms_ids={self.ms_ids}, jti={self.jti}, access_token={self.access_token})>"