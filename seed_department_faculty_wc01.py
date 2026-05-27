"""
Seed department faculty members for WCMEMBER01's allocated departments.

WCMEMBER01 has 3 departments:
  1. Physics & Electronics → 1 faculty
  2. Data Analytics & Mathematical Science → 2 faculty
  3. Computer Science and IT → 1 faculty

Each faculty member gets a unique 10-character uppercase ID and can only access their assigned department's data.

Run: python seed_department_faculty_wc01.py
Optional: --password "YourPassword" (default: Faculty@123)
Use --update to refresh existing members.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import SessionLocal
from app.db.models.committee_member import CommitteeMember
from app.core.password import hash_password, validate_password

# Department faculty assignments for WCMEMBER01's departments
DEPARTMENT_FACULTY = [
    # Physics & Electronics - 1 faculty
    {
        "id": "DFPE001001",  # 10 chars: DF (Department Faculty) + PE (Physics Electronics) + 001
        "name": "Physics & Electronics Faculty 1",
        "email": "dfpe001@jainuniversity.ac.in",
        "department": "Physics & Electronics",
    },
    # Data Analytics & Mathematical Science - 2 faculty
    {
        "id": "DFDA001001",  # DF + DA (Data Analytics) + 001
        "name": "Data Analytics Faculty 1",
        "email": "dfda001@jainuniversity.ac.in",
        "department": "Data Analytics & Mathematical Science",
    },
    {
        "id": "DFDA001002",  # DF + DA + 002
        "name": "Data Analytics Faculty 2",
        "email": "dfda002@jainuniversity.ac.in",
        "department": "Data Analytics & Mathematical Science",
    },
    # Computer Science and IT - 1 faculty
    {
        "id": "DFCS001001",  # DF + CS (Computer Science) + 001
        "name": "Computer Science Faculty 1",
        "email": "dfcs001@jainuniversity.ac.in",
        "department": "Computer Science and IT",
    },
]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed department faculty for WCMEMBER01's departments")
    parser.add_argument("--password", default="Faculty@123", help="Password for all faculty (change after first login)")
    parser.add_argument("--update", action="store_true", help="Update existing faculty (department and password)")
    args = parser.parse_args()

    try:
        validate_password(args.password)
    except Exception as e:
        print("Password validation failed:", e)
        sys.exit(1)
    hashed = hash_password(args.password)

    db = SessionLocal()
    try:
        print("Creating/updating department faculty members for WCMEMBER01's departments:\n")
        for faculty in DEPARTMENT_FACULTY:
            existing = db.query(CommitteeMember).filter_by(id=faculty["id"]).first()
            if existing:
                if not args.update:
                    print(f"  Skip {faculty['id']} (already exists). Use --update to refresh.")
                    continue
                existing.name = faculty["name"]
                existing.email = faculty["email"]
                existing.password_hash = hashed
                existing.role = "department_faculty"
                existing.department = faculty["department"]
                existing.allocated_departments = None
                print(f"  Updated {faculty['id']} – {faculty['department']}")
            else:
                db.add(CommitteeMember(
                    id=faculty["id"],
                    name=faculty["name"],
                    email=faculty["email"],
                    password_hash=hashed,
                    role="department_faculty",
                    department=faculty["department"],
                    allocated_departments=None,
                ))
                print(f"  Created {faculty['id']} – {faculty['department']}")
        db.commit()
        print("\n" + "="*60)
        print("Department Faculty Login Credentials:")
        print("="*60)
        for faculty in DEPARTMENT_FACULTY:
            print(f"\n  Username: {faculty['id']}")
            print(f"  Email: {faculty['email']}")
            print(f"  Department: {faculty['department']}")
            print(f"  Password: {args.password}")
            print(f"  Dashboard: /department-faculty/{faculty['id']}")
        print("\n" + "="*60)
        print("\nSummary by Department:")
        dept_groups = {}
        for f in DEPARTMENT_FACULTY:
            dept = f["department"]
            if dept not in dept_groups:
                dept_groups[dept] = []
            dept_groups[dept].append(f["id"])
        for dept, ids in dept_groups.items():
            print(f"  {dept}: {len(ids)} faculty ({', '.join(ids)})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
