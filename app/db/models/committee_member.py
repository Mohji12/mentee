from sqlalchemy import Column, String, Text
from app.db.database import Base


class CommitteeMember(Base):
    __tablename__ = "committee_members"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # leader | working_committee | department_faculty | program_faculty
    department = Column(String(255), nullable=True)  # for department_faculty only
    allocated_departments = Column(Text, nullable=True)  # JSON array as string for working_committee only
    allocated_programs = Column(Text, nullable=True)  # JSON array as string for program_faculty only