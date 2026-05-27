from sqlalchemy import Column, String
from app.db.database import Base
from sqlalchemy.orm import relationship

class Mentor(Base):
    __tablename__ = "mentors"
    
    mentor_id = Column(String(255), primary_key=True)
    mentor_name = Column(String(255), nullable=False)
    mentor_department = Column(String(255), nullable=False)
    mentor_email = Column(String(255), unique=True, nullable=False)
    mentor_phoneno = Column(String(20), nullable=False)
    mentor_password = Column(String(255), nullable=False)  # Merged password column

    students = relationship("Student", back_populates="mentor")
    counseling_sessions = relationship("CounselingSession", back_populates="mentor")
    counseling_availability = relationship("CounselingAvailability", back_populates="mentor")
    experience_learning = relationship(
        "ExperienceLearning", back_populates="mentor", cascade="all, delete-orphan"
    )