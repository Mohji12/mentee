from sqlalchemy import Column, String
from app.db.database import Base

class Admin(Base):
    __tablename__ = "admin"
    
    admin_id = Column(String, primary_key=True)
    admin_name = Column(String, nullable=False)
    admin_department = Column(String, nullable=False)
    admin_campus = Column(String, nullable=False)
    admin_email = Column(String, unique=True, nullable=False)
    admin_phoneno = Column(String, nullable=False)
    admin_password = Column(String, nullable=False)  # Merged password column