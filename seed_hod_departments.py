"""
Seed one HOD (Head of Department) user per department for the 10 departments.
Run from project root: python seed_hod_departments.py

Creates 10 committee members with role='hod', one per department. Each login ID
is exactly 10 characters. Department names must match mentors.mentor_department
so each HOD sees their department's students.

Existing HOD rows are removed before inserting, so re-running updates the DB to
use only these 10-char login IDs. Writes HOD_CREDENTIALS.md with Login ID and
default password for each HOD.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import SessionLocal
from app.db.models.committee_member import CommitteeMember
from app.core.password import hash_password

DEFAULT_PASSWORD = "HOD@123"

# (login_id, department name) - login_id must be exactly 10 characters; department must match Mentor.mentor_department
HOD_DEPARTMENTS = [
    ("hod01bioch", "Biochemistry & Chemistry"),
    ("hod02biote", "Biotechnology & Genetics"),
    ("hod03comps", "Computer Science"),
    ("hod04csit0", "Computer Science and IT"),
    ("hod05dataa", "Data Analytics & Mathematical Science"),
    ("hod06foren", "Forensic science"),
    ("hod07lang0", "Languages (English, Sanskrit, Kannada, Hindi, HRM)"),
    ("hod08micro", "Microbiology & Botany"),
    ("hod09phys0", "Physics & Electronics"),
    ("hod10psyo0", "Psychology"),
]


def write_credentials_file(credentials_path: Path, rows: list, default_password: str) -> None:
    content = f"""# HOD login credentials (default password)

Default password for all: {default_password}

| Department | Login ID |
|------------|----------|
"""
    for dept, login_id in rows:
        content += f"| {dept} | {login_id} |\n"
    content += "\nUse the Login ID and default password on the application login page to access the HOD dashboard for that department.\n"
    credentials_path.write_text(content, encoding="utf-8")
    print(f"Wrote credentials to {credentials_path}")


def main():
    db = SessionLocal()
    credentials_path = Path(__file__).resolve().parent / "HOD_CREDENTIALS.md"
    rows_for_file = []

    try:
        # Remove existing HODs so DB only has the new 10-char login IDs
        deleted = db.query(CommitteeMember).filter(CommitteeMember.role == "hod").delete()
        if deleted:
            print(f"Removed {deleted} existing HOD user(s).")
        hashed = hash_password(DEFAULT_PASSWORD)

        for login_id, department in HOD_DEPARTMENTS:
            assert len(login_id) == 10, f"Login ID must be 10 characters: {login_id!r}"
            email = f"{login_id}@menteetracker.local"
            name = f"HOD - {department}"

            existing = db.query(CommitteeMember).filter_by(id=login_id).first()
            if existing:
                existing.name = name
                existing.email = email
                existing.password_hash = hashed
                existing.role = "hod"
                existing.department = department
                existing.allocated_departments = None
                print(f"Updated HOD ({login_id}, department={department})")
            else:
                db.add(CommitteeMember(
                    id=login_id,
                    name=name,
                    email=email,
                    password_hash=hashed,
                    role="hod",
                    department=department,
                    allocated_departments=None,
                ))
                print(f"Added HOD ({login_id}, department={department})")
            rows_for_file.append((department, login_id))

        db.commit()
        write_credentials_file(credentials_path, rows_for_file, DEFAULT_PASSWORD)
        print("\nDone. Default password for all: " + DEFAULT_PASSWORD)
        print("Login IDs: " + ", ".join(login_id for _, login_id in HOD_DEPARTMENTS))
    except Exception as e:
        db.rollback()
        print("Error:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
