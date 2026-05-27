"""
Add a real faculty member as a committee dashboard user (Leader, Working Committee, Department Faculty, or HOD).
Run from project root.

Examples:

  # 1 Leader (only one)
  python add_committee_member.py --id "DR_RAO" --name "Dr. Rao" --email "rao@college.edu" --password "YourSecure@1" --role leader

  # Working committee (use real faculty id, name, email; departments must match mentor_department in DB)
  python add_committee_member.py --id "WC_FACULTY1" --name "Faculty One" --email "fac1@college.edu" --password "YourSecure@1" --role working_committee --departments "CS,ECE,IT"

  # Department faculty (department must match Mentor.mentor_department)
  python add_committee_member.py --id "FAC_CS_HEAD" --name "CS Dept Head" --email "cshead@college.edu" --password "YourSecure@1" --role department_faculty --department "CS"

  # HOD (Head of Department; department must match Mentor.mentor_department)
  python add_committee_member.py --id "HOD_CS" --name "HOD CS" --email "hodcs@college.edu" --password "YourSecure@1" --role hod --department "Computer Science"

Password must be 8-20 chars, with uppercase, lowercase, digit, and special character.
"""
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import HTTPException
from app.db.database import SessionLocal
from app.db.models.committee_member import CommitteeMember
from app.core.password import hash_password, validate_password


def main():
    parser = argparse.ArgumentParser(description="Add a committee member (real faculty) for dashboard login")
    parser.add_argument("--id", required=True, help="Login ID (e.g. employee code or email prefix)")
    parser.add_argument("--name", required=True, help="Full name")
    parser.add_argument("--email", required=True, help="Email (unique)")
    parser.add_argument("--password", required=True, help="Password (min 8 chars, upper, lower, digit, special)")
    parser.add_argument("--role", required=True, choices=["leader", "working_committee", "department_faculty", "hod"],
                        help="Dashboard role")
    parser.add_argument("--department", default=None,
                        help="For department_faculty and hod. Must match Mentor.mentor_department (e.g. CS, ECE)")
    parser.add_argument("--departments", default=None,
                        help="For working_committee only. Comma-separated list (e.g. CS,ECE,IT)")
    parser.add_argument("--update", action="store_true", help="Update existing member (password, name, etc.)")
    args = parser.parse_args()

    try:
        validate_password(args.password)
    except HTTPException as e:
        print("Password validation failed:", e.detail)
        sys.exit(1)
    hashed = hash_password(args.password)

    if args.role == "leader":
        if args.department or args.departments:
            print("Warning: leader role ignores --department and --departments")
        department, allocated_departments = None, None
    elif args.role == "working_committee":
        if not args.departments:
            print("Error: working_committee requires --departments (comma-separated)")
            sys.exit(1)
        department = None
        allocated_departments = json.dumps([d.strip() for d in args.departments.split(",")])
    elif args.role in ("department_faculty", "hod"):
        if not args.department:
            print(f"Error: {args.role} requires --department")
            sys.exit(1)
        department = args.department.strip()
        allocated_departments = None
    else:
        department = None
        allocated_departments = None

    db = SessionLocal()
    try:
        existing = db.query(CommitteeMember).filter_by(id=args.id).first()
        if existing:
            if not args.update:
                print(f"Error: ID '{args.id}' already exists. Use --update to change password/name/email.")
                sys.exit(1)
            existing.name = args.name
            existing.email = args.email
            existing.password_hash = hashed
            existing.role = args.role
            existing.department = department
            existing.allocated_departments = allocated_departments
            db.commit()
            print(f"Updated committee member: {args.id} ({args.role})")
        else:
            db.add(CommitteeMember(
                id=args.id.strip(),
                name=args.name.strip(),
                email=args.email.strip(),
                password_hash=hashed,
                role=args.role,
                department=department,
                allocated_departments=allocated_departments,
            ))
            db.commit()
            print(f"Added committee member: {args.id} ({args.role})")
        print(f"  Login with ID: {args.id} and the password you provided.")
    except Exception as e:
        db.rollback()
        print("Error:", e)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
