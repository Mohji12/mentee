from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship

class Activities(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_usn = Column(String(20), ForeignKey("students.student_usn"))
    short_term = Column(Text)
    short_term1 = Column(Text)
    short_term2 = Column(Text)
    mid_term = Column(Text)
    mid_term1 = Column(Text)
    mid_term2 = Column(Text)
    long_term = Column(Text)
    long_term1 = Column(Text)
    long_term2 = Column(Text)
    generated_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="activities")  # Add this relationship
