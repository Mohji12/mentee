from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from app.db.database import Base

class Competencies(Base):
    __tablename__ = "competencies"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    student_usn = Column(String(20), ForeignKey("students.student_usn", ondelete="CASCADE"), nullable=False)

    Active_Listening = Column(Integer, CheckConstraint("Active_Listening BETWEEN 0 AND 35"))
    Building_Trust = Column(Integer, CheckConstraint("Building_Trust BETWEEN 0 AND 35"))
    Encouraging = Column(Integer, CheckConstraint("Encouraging BETWEEN 0 AND 35"))
    Identifying_Goals_Current_Reality = Column(Integer, CheckConstraint("Identifying_Goals_Current_Reality BETWEEN 0 AND 35"))
    Instructing_Developing_Capabilities = Column(Integer, CheckConstraint("Instructing_Developing_Capabilities BETWEEN 0 AND 35"))
    Inspiring = Column(Integer, CheckConstraint("Inspiring BETWEEN 0 AND 35"))
    Providing_Corrective_Feedback = Column(Integer, CheckConstraint("Providing_Corrective_Feedback BETWEEN 0 AND 35"))
    Managing_Risks = Column(Integer, CheckConstraint("Managing_Risks BETWEEN 0 AND 35"))
    Opening_Doors = Column(Integer, CheckConstraint("Opening_Doors BETWEEN 0 AND 35")) 