"""
Export mentor-wise assigned student count to Excel.
Run from project root: python export_mentor_wise_student_count.py
Output: mentor_wise_student_count.xlsx
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))


def main():
    try:
        import pandas as pd
    except ImportError:
        print("Install: pip install pandas openpyxl")
        return 1

    from sqlalchemy import text
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        q = text("""
            SELECT
                m.mentor_id,
                m.mentor_name,
                m.mentor_email,
                m.mentor_department AS department,
                COUNT(s.student_usn) AS assigned_student_count
            FROM mentors m
            LEFT JOIN students s ON m.mentor_id = s.assigned_mentor
            GROUP BY m.mentor_id, m.mentor_name, m.mentor_email, m.mentor_department
            ORDER BY m.mentor_department, assigned_student_count DESC, m.mentor_name
        """)
        rows = db.execute(q).fetchall()
        df = pd.DataFrame(
            rows,
            columns=["Mentor ID", "Mentor Name", "Mentor Email", "Department", "Assigned Student Count"],
        )

        out = project_root / "mentor_wise_student_count.xlsx"
        df.to_excel(out, sheet_name="Mentor-wise student count", index=False, engine="openpyxl")
        print("Written:", out)
        print("Rows:", len(df))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
