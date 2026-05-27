"""
Add allocated_programs column to committee_members table.
Run from project root: python add_allocated_programs_column.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from app.db.database import engine

def main():
    try:
        with engine.connect() as conn:
            # Check if column already exists
            check_sql = text("""
                SELECT COUNT(*) as col_count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'committee_members'
                AND COLUMN_NAME = 'allocated_programs'
            """)
            result = conn.execute(check_sql)
            col_exists = result.fetchone()[0] > 0
            
            if col_exists:
                print("Column 'allocated_programs' already exists in committee_members table.")
                return
            
            # Add the column
            alter_sql = text("""
                ALTER TABLE committee_members 
                ADD COLUMN allocated_programs TEXT NULL COMMENT 'JSON array as string for program_faculty only'
            """)
            conn.execute(alter_sql)
            conn.commit()
            print("Successfully added 'allocated_programs' column to committee_members table.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
