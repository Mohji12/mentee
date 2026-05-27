from sqlalchemy import Column, String, Integer, ForeignKey
from app.db.database import Base
from sqlalchemy.orm import relationship

class Student(Base):
    __tablename__ = "students"
    
    # Signup and Login Fields
    student_usn = Column(String, primary_key=True)
    student_name = Column(String, nullable=True)
    student_email = Column(String, unique=True, nullable=False)
    student_phoneno = Column(String, nullable=True)
    student_program = Column(String, nullable=True)
    semester = Column(Integer, nullable=True)
    student_batch = Column(String, nullable=True)
    assigned_mentor = Column(String, ForeignKey("mentors.mentor_id"), nullable=True)
    student_password = Column(String, nullable=False)
    linkedin = Column(String, nullable=True)

    activities = relationship("Activities", back_populates="student") # Add this relationship
    mentor = relationship("Mentor", back_populates="students")
    queries = relationship("Query", back_populates="student") #Added this line.
    counseling_sessions = relationship("CounselingSession", back_populates="student")
