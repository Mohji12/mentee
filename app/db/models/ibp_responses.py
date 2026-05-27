from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base


class IBPResponse(Base):
    __tablename__ = "ibp_responses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(String(255), nullable=False, index=True)
    responses = Column(Text, nullable=False)  # JSON string: {"1": "3", "2": "5", ...}
    submitted_at = Column(DateTime, server_default=func.now(), nullable=False)

    class Config:
        from_attributes = True
