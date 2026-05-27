from sqlalchemy import Column, String, Integer
from app.db.database import Base

class ForgotPassword(Base):
    __tablename__ = "forgot_password"

    id = Column(Integer, primary_key=True, index=True)
    mentor_student_id = Column(String(255), index=True)  # This will hold either mentor_id or student_usn
    email_id = Column(String(255), nullable=False)
    otp_code = Column(String(10), nullable=False)  # 6-digit alphanumeric OTP
