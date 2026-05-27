"""
One-time script to add student_feedback_file column to counseling_sessions.
Run from project root: python run_add_student_feedback_file.py
"""
import sys
from sqlalchemy import text

def main():
    from app.db.database import engine
    sql = "ALTER TABLE counseling_sessions ADD COLUMN student_feedback_file VARCHAR(500) NULL"
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        print("Column student_feedback_file added successfully.")
    except Exception as e:
        if "Duplicate column name" in str(e) or "1060" in str(e):
            print("Column already exists. Nothing to do.")
            return 0
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
