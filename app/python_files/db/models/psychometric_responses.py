from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base

class PsychometricResponse(Base):
    __tablename__ = 'psychometric_responses'

    id = Column(Integer, primary_key=True, index=True)
    student_usn = Column(String, nullable=False)
    present_address = Column(Text)
    permanent_address = Column(Text)
    educational_qualifications = Column(Text)
    subjects_strength = Column(Text)
    subjects_weakness = Column(Text)
    previous_work_experience = Column(Text)
    father_name = Column(String)
    father_mobile_no = Column(String)
    father_education = Column(String)
    father_employment = Column(String)
    mother_name = Column(String)
    mother_mobile_no = Column(String)
    mother_education = Column(String)
    mother_employment = Column(String)
    siblings_details = Column(Text)
    professional_dream = Column(Text)
    professional_fear = Column(Text)
    happiness_sources = Column(Text)
    expectations = Column(Text)
    goal_achieving_opportunities = Column(Text)
    participate_in_skill_programs = Column(Text)
    interested_skill_programs = Column(Text)
    external_factors_affecting_growth = Column(Text)
    primary_stressors = Column(Text)
    biggest_distractions = Column(Text)
    strongest_skills = Column(Text)
    areas_of_low_confidence = Column(Text)
    hobbies_interests = Column(Text)
    consent_given = Column(String)
    
    # This will store the time when the response was submitted
    submitted_at = Column(DateTime, server_default=func.now())
    
    class Config:
        from_attributes = True
