"""
Verify allocated_programs column exists and show table structure.
Run from project root: python verify_allocated_programs_column.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from app.db.database import engine

def main():
    try:
        with engine.connect() as conn:
            # Show table structure
            show_sql = text("DESCRIBE committee_members")
            result = conn.execute(show_sql)
            rows = result.fetchall()
            
            print("committee_members table structure:")
            print("-" * 80)
            for row in rows:
                print(f"{row[0]:<30} {row[1]:<20} {row[2]:<10} {row[3]:<10} {row[4] or ''}")
            print("-" * 80)
            
            # Check specifically for allocated_programs
            check_sql = text("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'committee_members'
                AND COLUMN_NAME = 'allocated_programs'
            """)
            result = conn.execute(check_sql)
            col_info = result.fetchone()
            
            if col_info:
                print(f"\nFound allocated_programs column:")
                print(f"  Column Name: {col_info[0]}")
                print(f"  Data Type: {col_info[1]}")
                print(f"  Nullable: {col_info[2]}")
                print(f"  Comment: {col_info[3]}")
            else:
                print("\nERROR: allocated_programs column NOT found!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
