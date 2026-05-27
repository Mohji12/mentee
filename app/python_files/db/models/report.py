from sqlalchemy import Column, String, Integer,  ForeignKey, Text
from app.db.database import Base


class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_usn = Column(String(20), ForeignKey("students.student_usn"), nullable=False)
    professional_aspirations = Column(Text, nullable=False)
    hobbies_interests = Column(Text, nullable=False)
    strengths = Column(Text, nullable=False)
    weaknesses = Column(Text, nullable=False)
    opportunities = Column(Text, nullable=False)
    threats = Column(Text, nullable=False)
    detailed_analysis = Column(Text, nullable=False)
