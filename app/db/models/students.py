from sqlalchemy import Column, String, Integer, ForeignKey, Date, DateTime, Boolean
from app.db.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Student(Base):
    __tablename__ = "students"
    
    # Signup and Login Fields
    student_usn = Column(String(255), primary_key=True)
    student_name = Column(String(255), nullable=True)
    student_email = Column(String(255), unique=True, nullable=False)
    student_phoneno = Column(String(20), nullable=True)
    student_program = Column(String(255), nullable=True)
    semester = Column(Integer, nullable=True)
    student_batch = Column(String(50), nullable=True)
    assigned_mentor = Column(String(255), ForeignKey("mentors.mentor_id"), nullable=True)
    student_password = Column(String(255), nullable=False)
    linkedin = Column(String(500), nullable=True)
    # Profile extras
    gender = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    parent_guardian_contact = Column(String(20), nullable=True)
    mother_contact = Column(String(20), nullable=True)
    father_contact = Column(String(20), nullable=True)
    profile_photo_url = Column(String(500), nullable=True)
    is_alumni = Column(Boolean, nullable=False, default=False, server_default="0")
    alumni_since = Column(DateTime, nullable=True)

    activities = relationship("Activities", back_populates="student") # Add this relationship
    experience_learning = relationship(
        "ExperienceLearning", back_populates="student", cascade="all, delete-orphan"
    )
    mentor = relationship("Mentor", back_populates="students")
    queries = relationship("Query", back_populates="student") #Added this line.
    counseling_sessions = relationship("CounselingSession", back_populates="student")
    academic_performance = relationship("AcademicPerformance", back_populates="student", cascade="all, delete-orphan")
    academic_performance_marksheets = relationship("AcademicPerformanceMarksheet", back_populates="student", cascade="all, delete-orphan")
    secondary_marksheets = relationship("StudentSecondaryMarksheet", back_populates="student", cascade="all, delete-orphan")