"""
Fix spelling mistakes and normalize department names in the mentors table
so departments are not repeated due to typos or "&" vs "and" variations.

Run: python fix_mentor_department_spelling.py
Use --dry-run to only print what would be updated without changing the DB.
"""

import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine

# Map incorrect/duplicate department name -> correct canonical name.
# CIVIL, CS, ECE, EEE, IT, MECH are excluded from the leader dropdown in the API (not updated here).
DEPARTMENT_FIXES = {
    # Spelling fixes (removes "Data Analytics & Mathematial Science" and "Physics and Electronics" as separate entries)
    "Data Analytics & Mathematial Science": "Data Analytics & Mathematical Science",
    "Mathematial Science": "Mathematical Science",
    # Normalize "&" vs "and" to one form (use "&" to match other departments)
    "Physics and Electronics": "Physics & Electronics",
    "Biochemistry and Chemistry": "Biochemistry & Chemistry",
    "Biotechnology and Genetics": "Biotechnology & Genetics",
    "Microbiology and Botany": "Microbiology & Botany",
    "Data Analytics and Mathematical Science": "Data Analytics & Mathematical Science",
    # Add more wrong -> right mappings as needed
}


def main():
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN – no changes will be written to the database.\n")

    with engine.connect() as conn:
        for wrong, correct in DEPARTMENT_FIXES.items():
            if wrong == correct:
                continue
            # Count how many rows have the wrong value
            r = conn.execute(
                text("SELECT COUNT(*) FROM mentors WHERE mentor_department = :w"),
                {"w": wrong},
            )
            count = r.scalar()
            if count == 0:
                continue
            print(f"  '{wrong}' -> '{correct}' ({count} mentor(s))")
            if not dry_run:
                conn.execute(
                    text(
                        "UPDATE mentors SET mentor_department = :c WHERE mentor_department = :w"
                    ),
                    {"c": correct, "w": wrong},
                )
        if not dry_run:
            conn.commit()

    if dry_run:
        print("\nRun without --dry-run to apply updates.")
    else:
        print("\nDone. Mentor departments updated.")


def list_departments():
    """Print all distinct mentor_department values (to find more spelling issues)."""
    with engine.connect() as conn:
        r = conn.execute(
            text("SELECT mentor_department, COUNT(*) AS cnt FROM mentors GROUP BY mentor_department ORDER BY mentor_department")
        )
        rows = r.fetchall()
    print("Current mentor_department values and counts:\n")
    for dept, cnt in rows:
        print(f"  {cnt:4d}  {dept}")
    print("\nAdd any wrong spellings to DEPARTMENT_FIXES in this script, then run without --list.")


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_departments()
    else:
        main()
