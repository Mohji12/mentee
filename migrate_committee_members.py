"""
Create the committee_members table in the database.
Run from project root: python migrate_committee_members.py

Uses SQLAlchemy Base.metadata.create_all() so only missing tables are created.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import engine and Base; import committee_member model so the table is registered
from app.db.database import engine, Base
from app.db.models import committee_member  # noqa: F401

if __name__ == "__main__":
    print("Creating committee_members table if it does not exist...")
    Base.metadata.create_all(bind=engine)
    print("Done. committee_members table is ready.")
