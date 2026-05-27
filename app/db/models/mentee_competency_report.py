from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db.database import Base

class MenteeCompetencyReport(Base):
    __tablename__ = 'mentee_competency_report'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False)
    competency = Column(String(255), nullable=False)
    observation = Column(Text, nullable=True)
    mentor_implication = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True) 