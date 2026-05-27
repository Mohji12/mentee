from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from app.db.database import Base
from datetime import datetime
import pytz

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mentor_id = Column(String(255), ForeignKey("mentors.mentor_id"), nullable=False)
    student_usn = Column(String(255), ForeignKey("students.student_usn"), nullable=True)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None), nullable=False)
    status = Column(String(50), default="sent", nullable=False)  # sent, failed
    email_type = Column(String(100), default="manual", nullable=False)  # manual, reminder, notification
    
    class Config:
        from_attributes = True
