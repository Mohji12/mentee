from sqlalchemy import Column, String, ForeignKey, Text
from app.db.database import Base
from sqlalchemy.orm import relationship

class Query(Base):
    __tablename__ = "query"

    id = Column(String(50), primary_key=True, nullable=False)
    usn = Column(String(255), ForeignKey("students.student_usn", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phoneno = Column(String(15), nullable=True)
    program = Column(String(255), nullable=True)
    ass_mentor = Column(String(255), nullable=True)
    query_issue = Column(Text, nullable=True)

    # Relationship (if needed, you can access student details via Query.student)
    student = relationship("Student", back_populates="queries")
