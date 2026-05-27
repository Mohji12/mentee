from sqlalchemy import Column, String
from app.db.database import Base

class Admin(Base):
    __tablename__ = "admin"
    
    admin_id = Column(String(255), primary_key=True)
    admin_name = Column(String(255), nullable=False)
    admin_department = Column(String(255), nullable=False)
    admin_campus = Column(String(255), nullable=False)
    admin_email = Column(String(255), unique=True, nullable=False)
    admin_phoneno = Column(String(20), nullable=False)
    admin_password = Column(String(255), nullable=False)  # Merged password column