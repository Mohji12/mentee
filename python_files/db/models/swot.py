from sqlalchemy import Column, String, Integer, ForeignKey, Text
from app.db.database import Base

class SWOT(Base):
    __tablename__ = 'swot'

    id = Column(Integer, primary_key=True, index=True)
    student_usn = Column(String, ForeignKey('students.student_usn'), index=True)
    swot_analysis = Column(Text)
