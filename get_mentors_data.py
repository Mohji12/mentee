"""
Get all mentor data from the mentors table (raw SQL, no ORM).
Run from project root: python get_mentors_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

def main():
    from sqlalchemy import text
    from app.db.database import engine

    sql = text("SELECT mentor_id, mentor_name, mentor_department, mentor_email, mentor_phoneno FROM mentors ORDER BY mentor_id")
    with engine.connect() as conn:
        result = conn.execute(sql)
        rows = result.fetchall()
        keys = result.keys()

    if not rows:
        print("No mentors in table.")
        return

    for row in rows:
        print(dict(zip(keys, row)))
    print(f"\nTotal: {len(rows)} mentor(s)")

if __name__ == "__main__":
    main()
