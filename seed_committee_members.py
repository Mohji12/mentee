"""
Seed committee members for the three-tier dashboards.
Run from project root: python seed_committee_members.py

Creates:
- 1 leader (id: leader1)
- 3 working committee members (wc1, wc2, wc3) with allocated_departments
- 2 department faculty (faculty_cs, faculty_ece) - adjust department names to match your mentors table

Default password for all: Committee@1 (change in production)
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import SessionLocal
from app.db.models.committee_member import CommitteeMember
from app.core.password import hash_password

DEFAULT_PASSWORD = "Committee@1"


def main():
    db = SessionLocal()
    try:
        hashed = hash_password(DEFAULT_PASSWORD)

        # 1 Leader
        if db.query(CommitteeMember).filter_by(id="leader1").first() is None:
            db.add(CommitteeMember(
                id="leader1",
                name="Core Committee Leader",
                email="leader@menteetracker.local",
                password_hash=hashed,
                role="leader",
                department=None,
                allocated_departments=None,
            ))
            print("Added leader (leader1)")
        else:
            print("Leader leader1 already exists")

        # 3 Working committee (allocate example departments; change to match your mentor_department values)
        for member_id, name, email, depts in [
            ("wc1", "Working Committee 1", "wc1@menteetracker.local", ["CS", "ECE"]),
            ("wc2", "Working Committee 2", "wc2@menteetracker.local", ["IT", "EEE"]),
            ("wc3", "Working Committee 3", "wc3@menteetracker.local", ["MECH", "CIVIL"]),
        ]:
            if db.query(CommitteeMember).filter_by(id=member_id).first() is None:
                db.add(CommitteeMember(
                    id=member_id,
                    name=name,
                    email=email,
                    password_hash=hashed,
                    role="working_committee",
                    department=None,
                    allocated_departments=json.dumps(depts),
                ))
                print(f"Added working committee ({member_id})")
            else:
                print(f"Working committee {member_id} already exists")

        # 2 Department faculty (department must match Mentor.mentor_department in your DB)
        for member_id, name, email, dept in [
            ("faculty_cs", "Department Faculty CS", "faculty_cs@menteetracker.local", "CS"),
            ("faculty_ece", "Department Faculty ECE", "faculty_ece@menteetracker.local", "ECE"),
        ]:
            if db.query(CommitteeMember).filter_by(id=member_id).first() is None:
                db.add(CommitteeMember(
                    id=member_id,
                    name=name,
                    email=email,
                    password_hash=hashed,
                    role="department_faculty",
                    department=dept,
                    allocated_departments=None,
                ))
                print(f"Added department faculty ({member_id}, department={dept})")
            else:
                print(f"Department faculty {member_id} already exists")

        db.commit()
        print("\nDone. Default password for all: " + DEFAULT_PASSWORD)
        print("Login IDs: leader1, wc1, wc2, wc3, faculty_cs, faculty_ece")
    except Exception as e:
        db.rollback()
        print("Error:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
