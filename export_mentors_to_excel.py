"""
Export all mentor data from the mentors table to an Excel file.
Uses raw SQL only (no ORM) so no other models need to be loaded.

Run from project root: python export_mentors_to_excel.py
Output: mentors_export.xlsx (in current directory)
Password column is excluded for security.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

def main():
    try:
        import pandas as pd
        from sqlalchemy import text
        from app.db.database import engine
    except ImportError as e:
        print(f"Error: {e}")
        print("Ensure dependencies are installed: pip install pandas openpyxl")
        return 1

    # Raw SQL: only mentors table, no ORM (avoids Student/relationship resolution)
    sql = text("""
        SELECT mentor_id AS "Mentor ID",
               mentor_name AS "Name",
               mentor_department AS "Department",
               mentor_email AS "Email",
               mentor_phoneno AS "Phone"
        FROM mentors
        ORDER BY mentor_id
    """)
    with engine.connect() as conn:
        result = conn.execute(sql)
        rows = result.fetchall()
        columns = result.keys()

    if not rows:
        print("No mentors found in the database.")
        return 0

    df = pd.DataFrame(rows, columns=columns)
    out_file = "mentors_export.xlsx"
    df.to_excel(out_file, index=False, sheet_name="Mentors", engine="openpyxl")
    print(f"Exported {len(rows)} mentor(s) to {out_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
