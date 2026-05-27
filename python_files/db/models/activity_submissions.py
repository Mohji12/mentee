from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from app.db.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class ActivitySubmissions(Base):
    __tablename__ = "activity_submissions"

    submission_id = Column(String(20), primary_key=True)  # Unique submission ID
    activity_id = Column(String(20), ForeignKey("activities_tracking.id"), nullable=False)
    student_usn = Column(String(255), ForeignKey("students.student_usn"), nullable=False)
    mentor_id = Column(String(255), ForeignKey("mentors.mentor_id"), nullable=False)
    proof = Column(String(2048), nullable=False)  # File stored in S3 (no public URL)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="Pending")  # Pending, Approved, Rejected
    rejection_reason = Column(Text, nullable=True)
    completed_in = Column(Integer, nullable=True)  # Days taken to complete
    percentage = Column(Integer, nullable=True)  # Percentage given by mentor (0-100)

        # Relationships
    activity = relationship("ActivitiesTracking", backref="submissions")
    student = relationship("Student", backref="submissions")
    mentor = relationship("Mentor", backref="submissions")