"""
Seed program faculty members for WCMEMBER03's allocated programs.

Structure:
- BSc. Combined Dashboard (3 programs combined): 2 login IDs
  - BSc. in Biochemistry & Chemistry
  - BSc. in Biotechnology & Genetics
  - BSc. in Microbiology & Botany

- MSc. Separate Dashboards (each program has its own dashboard with 3 login IDs):
  - MSc. in Biochemistry & Chemistry → 3 login IDs
  - MSc. in Biotechnology & Genetics → 3 login IDs
  - MSc. in Microbiology & Botany → 3 login IDs

Total: 2 + 9 = 11 login IDs

Run from project root: python seed_program_faculty.py
Optional: --password "YourPassword" (default: Program@123). Change after first login.
Use --update to refresh programs/password for existing members.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.database import SessionLocal
from app.db.models.committee_member import CommitteeMember
from app.core.password import hash_password, validate_password

# BSc. programs (combined dashboard - 2 login IDs)
BSC_PROGRAMS = [
    "BSc. in Biochemistry & Chemistry",
    "BSc. in Biotechnology & Genetics",
    "BSc. in Microbiology & Botany",
]

# MSc. programs (separate dashboards - 3 login IDs each)
MSC_PROGRAMS = [
    "MSc. in Biochemistry & Chemistry",
    "MSc. in Biotechnology & Genetics",
    "MSc. in Microbiology & Botany",
]

# BSc. Combined Dashboard Members (2 login IDs)
BSC_MEMBERS = [
    {
        "id": "PFBSC001",  # Program Faculty BSc 001
        "name": "Program Faculty BSc Member 1",
        "email": "pfbsc001@jainuniversity.ac.in",
        "programs": BSC_PROGRAMS,
    },
    {
        "id": "PFBSC002",  # Program Faculty BSc 002
        "name": "Program Faculty BSc Member 2",
        "email": "pfbsc002@jainuniversity.ac.in",
        "programs": BSC_PROGRAMS,
    },
]

# MSc. Separate Dashboard Members (3 login IDs per program)
MSC_MEMBERS = []
for i, program in enumerate(MSC_PROGRAMS):
    # Extract short name for ID (e.g., "Biochemistry & Chemistry" -> "BC")
    program_short = "".join([word[0].upper() for word in program.replace("MSc. in ", "").split() if word[0].isalpha()])
    for j in range(1, 4):  # 3 members per program
        member_id = f"PFMSC{program_short}{j:02d}"  # e.g., PFMSCBC01, PFMSCBC02, PFMSCBC03
        MSC_MEMBERS.append({
            "id": member_id,
            "name": f"Program Faculty {program} Member {j}",
            "email": f"{member_id.lower()}@jainuniversity.ac.in",
            "programs": [program],  # Each member handles one MSc program
        })

ALL_PROGRAM_FACULTY = BSC_MEMBERS + MSC_MEMBERS


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Seed program faculty members with allocated programs")
    parser.add_argument("--password", default="Program@123", help="Password for all members (change after first login)")
    parser.add_argument("--update", action="store_true", help="Update existing members (programs and password)")
    args = parser.parse_args()

    try:
        validate_password(args.password)
    except Exception as e:
        print("Password validation failed:", e)
        sys.exit(1)
    hashed = hash_password(args.password)

    db = SessionLocal()
    try:
        for m in ALL_PROGRAM_FACULTY:
            existing = db.query(CommitteeMember).filter_by(id=m["id"]).first()
            if existing:
                if not args.update:
                    print(f"  Skip {m['id']} (already exists). Use --update to refresh.")
                    continue
                existing.name = m["name"]
                existing.email = m["email"]
                existing.password_hash = hashed
                existing.role = "program_faculty"
                existing.allocated_programs = json.dumps(m["programs"])
                existing.department = None
                existing.allocated_departments = None
                print(f"  Updated {m['id']} – {len(m['programs'])} program(s)")
            else:
                db.add(CommitteeMember(
                    id=m["id"],
                    name=m["name"],
                    email=m["email"],
                    password_hash=hashed,
                    role="program_faculty",
                    department=None,
                    allocated_departments=None,
                    allocated_programs=json.dumps(m["programs"]),
                ))
                print(f"  Created {m['id']} – {len(m['programs'])} program(s)")
        db.commit()
        print("\nDone. Login with each member's username (ID) and the password.")
        print("\nLogin Credentials Summary:")
        print(f"\nBSc. Combined Dashboard ({len(BSC_PROGRAMS)} programs): {len(BSC_MEMBERS)} members")
        for m in BSC_MEMBERS:
            print(f"  {m['id']} - Username: {m['id']}, Email: {m['email']}")
        
        print(f"\nMSc. Separate Dashboards:")
        for program in MSC_PROGRAMS:
            program_members = [m for m in MSC_MEMBERS if program in m["programs"]]
            print(f"  {program}: {len(program_members)} members")
            for m in program_members:
                print(f"    {m['id']} - Username: {m['id']}, Email: {m['email']}")
        
        print(f"\nTotal: {len(ALL_PROGRAM_FACULTY)} program faculty members")
    finally:
        db.close()


if __name__ == "__main__":
    main()
