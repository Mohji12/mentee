"""
Seed the three working committee members (second-stage dashboard) with allocated departments.

  Member 1: Physics & Electronics, Computer Science and IT, Data Analytics & Mathematical Science
  Member 2: Forensic science, Psychology
  Member 3: All remaining departments (Biotechnology & Genetics, Biochemistry & Chemistry,
            Languages (English, Sanskrit, Kannada, Hindi, HRM), Microbiology & Botany, etc.)

Department names must match mentor_department in the mentors table exactly.
Run from project root: python seed_working_committee_three.py

Optional: --password "YourPassword" (default: Committee@123). Change after first login.
Use --update to refresh departments/password for existing members.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import SessionLocal
from app.db.models.committee_member import CommitteeMember
from app.core.password import hash_password, validate_password

# All departments that appear in the application (must match mentors.mentor_department)
ALL_DEPARTMENTS = [
    "Physics & Electronics",
    "Computer Science and IT",
    "Data Analytics & Mathematical Science",
    "Forensic science",
    "Psychology",
    "Biotechnology & Genetics",
    "Biochemistry & Chemistry",
    "Languages (English, Sanskrit, Kannada, Hindi, HRM)",
    "Microbiology & Botany",
]

MEMBER_1_DEPARTMENTS = [
    "Physics & Electronics",
    "Computer Science and IT",
    "Data Analytics & Mathematical Science",
]

MEMBER_2_DEPARTMENTS = [
    "Forensic science",
    "Psychology",
]

# Member 3 gets all remaining (not assigned to member 1 or 2)
MEMBER_3_DEPARTMENTS = [d for d in ALL_DEPARTMENTS if d not in MEMBER_1_DEPARTMENTS and d not in MEMBER_2_DEPARTMENTS]

THREE_MEMBERS = [
    {
        "id": "WCMEMBER01",  # 10 characters, all uppercase
        "name": "Committee Member 1",
        "email": "wc1@jainuniversity.ac.in",
        "departments": MEMBER_1_DEPARTMENTS,
    },
    {
        "id": "WCMEMBER02",  # 10 characters, all uppercase
        "name": "Committee Member 2",
        "email": "wc2@jainuniversity.ac.in",
        "departments": MEMBER_2_DEPARTMENTS,
    },
    {
        "id": "WCMEMBER03",  # 10 characters, all uppercase
        "name": "Committee Member 3",
        "email": "wc3@jainuniversity.ac.in",
        "departments": MEMBER_3_DEPARTMENTS,
    },
]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed 3 working committee members with allocated departments")
    parser.add_argument("--password", default="Committee@123", help="Password for all 3 (change after first login)")
    parser.add_argument("--update", action="store_true", help="Update existing members (departments and password)")
    args = parser.parse_args()

    try:
        validate_password(args.password)
    except Exception as e:
        print("Password validation failed:", e)
        sys.exit(1)
    hashed = hash_password(args.password)

    db = SessionLocal()
    try:
        for m in THREE_MEMBERS:
            existing = db.query(CommitteeMember).filter_by(id=m["id"]).first()
            if existing:
                if not args.update:
                    print(f"  Skip {m['id']} (already exists). Use --update to refresh.")
                    continue
                existing.name = m["name"]
                existing.email = m["email"]
                existing.password_hash = hashed
                existing.role = "working_committee"
                existing.allocated_departments = json.dumps(m["departments"])
                existing.department = None
                print(f"  Updated {m['id']} – {len(m['departments'])} departments")
            else:
                db.add(CommitteeMember(
                    id=m["id"],
                    name=m["name"],
                    email=m["email"],
                    password_hash=hashed,
                    role="working_committee",
                    department=None,
                    allocated_departments=json.dumps(m["departments"]),
                ))
                print(f"  Created {m['id']} – {len(m['departments'])} departments")
        db.commit()
        print("\nDone. Login with each member's username (ID) and the password; redirects to /working-committee/<member_id>.")
        print("\nLogin Credentials:")
        for m in THREE_MEMBERS:
            print(f"  {m['id']} - Username: {m['id']}, Email: {m['email']}, Departments: {len(m['departments'])}")
        print("\nDepartment Allocations:")
        print("Member 1:", MEMBER_1_DEPARTMENTS)
        print("Member 2:", MEMBER_2_DEPARTMENTS)
        print("Member 3 (remaining):", MEMBER_3_DEPARTMENTS)
    finally:
        db.close()


if __name__ == "__main__":
    main()
