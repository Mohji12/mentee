from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from app.db.database import Base

class ActivitiesTracking(Base):
    __tablename__ = 'activities_tracking'
    
    id = Column(String(255), primary_key=True)
    student_usn = Column(String(255), ForeignKey('students.student_usn'))
    activities = Column(String(500))  # Activity details
    duration_type = Column(String(50))  # Short term, Mid term, Long term
    deadline = Column(DateTime, nullable=True)
    remarks = Column(String(500), nullable=True)
    completed_in = Column(Integer, nullable=True)
    benefitted = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    proof = Column(String(500))  # File path for uploaded proof

    # Who requested this activity: 'mentee', 'mentor', or None (SWOT/system)
    requested_by = Column(String(20), nullable=True)

    # Mentor-related fields
    status = Column(String(50), default="Pending")  # Pending, Approved, Rejected
    rejection_reason = Column(String(500), nullable=True)  # Reason if rejected
    percentage = Column(Integer, nullable=True)  # Percentage given by mentor (0-100)

    class Config:
        from_attributes = True
