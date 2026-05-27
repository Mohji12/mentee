from sqlalchemy import Column, String
from app.db.database import Base
from sqlalchemy.orm import relationship

class Mentor(Base):
    __tablename__ = "mentors"
    
    mentor_id = Column(String, primary_key=True)
    mentor_name = Column(String, nullable=False)
    mentor_department = Column(String, nullable=False)
    mentor_email = Column(String, unique=True, nullable=False)
    mentor_phoneno = Column(String, nullable=False)
    mentor_password = Column(String, nullable=False)  # Merged password column

    students = relationship("Student", back_populates="mentor")
    counseling_sessions = relationship("CounselingSession", back_populates="mentor")
    counseling_availability = relationship("CounselingAvailability", back_populates="mentor")