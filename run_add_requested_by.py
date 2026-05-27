"""
One-time script to add requested_by column to activities_tracking.
Run: python run_add_requested_by.py
"""
import sys
from sqlalchemy import text

def main():
    from app.db.database import engine
    sql = "ALTER TABLE activities_tracking ADD COLUMN requested_by VARCHAR(20) NULL"
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        print("Column requested_by added successfully.")
    except Exception as e:
        if "Duplicate column name" in str(e) or "1060" in str(e):
            print("Column already exists. Nothing to do.")
            return 0
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
