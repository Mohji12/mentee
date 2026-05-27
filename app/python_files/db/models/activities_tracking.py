from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from app.db.database import Base

class ActivitiesTracking(Base):
    __tablename__ = 'activities_tracking'
    
    id = Column(String, primary_key=True)
    student_usn = Column(String, ForeignKey('students.student_usn'))
    activities = Column(String)  # Activity details
    duration_type = Column(String)  # Short term, Mid term, Long term
    deadline = Column(DateTime, nullable=True)
    remarks = Column(String, nullable=True)
    completed_in = Column(Integer, nullable=True)
    benefitted = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    proof = Column(String)  # File path for uploaded proof

    # Mentor-related fields
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    rejection_reason = Column(String, nullable=True)  # Reason if rejected
    percentage = Column(Integer, nullable=True)  # Percentage given by mentor (0-100)

    class Config:
        from_attributes = True
