from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship

class Activities(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_usn = Column(String(20), ForeignKey("students.student_usn"))
    short_term = Column(String(255))
    short_term1 = Column(String(255))
    short_term2 = Column(String(255))
    mid_term = Column(String(255))
    mid_term1 = Column(String(255))
    mid_term2 = Column(String(255))
    long_term = Column(String(255))
    long_term1 = Column(String(255))
    long_term2 = Column(String(255))
    generated_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="activities")  # Add this relationship
