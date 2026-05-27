#!/usr/bin/env python3
"""
Export mentor-wise students and unassigned student count to Excel.
- Sheet 1: Summary (total mentors, assigned students, count of students NOT assigned)
- Sheet 2: Mentor-wise students (each mentor with their students)
- Sheet 3: Unassigned students (full list of students without a mentor)
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

try:
    import pandas as pd
except ImportError:
    print("Install dependencies: pip install pandas openpyxl")
    sys.exit(1)

from app.db.database import SessionLocal
from sqlalchemy import text


def export_mentor_wise_and_unassigned(output_filename=None):
    db = SessionLocal()
    try:
        print("=" * 70)
        print("EXPORT: Mentor-wise students & Unassigned student count")
        print("=" * 70)

        # --- 1. Unassigned students (no mentor) ---
        unassigned_query = text("""
            SELECT student_usn, student_name, student_email, student_program, semester, student_batch
            FROM students
            WHERE assigned_mentor IS NULL
            ORDER BY student_usn
        """)
        unassigned_result = db.execute(unassigned_query).fetchall()
        unassigned_count = len(unassigned_result)
        df_unassigned = pd.DataFrame(unassigned_result, columns=[
            "Student USN", "Student Name", "Student Email", "Program", "Semester", "Batch"
        ])
        df_unassigned = df_unassigned.fillna("")

        # --- 2. Mentor-wise students ---
        mentor_wise_query = text("""
            SELECT
                m.mentor_id AS "Mentor ID",
                m.mentor_name AS "Mentor Name",
                m.mentor_department AS "Department",
                m.mentor_email AS "Mentor Email",
                s.student_usn AS "Student USN",
                s.student_name AS "Student Name",
                s.student_email AS "Student Email",
                s.student_program AS "Program",
                s.semester AS "Semester",
                s.student_batch AS "Batch"
            FROM mentors m
            INNER JOIN students s ON m.mentor_id = s.assigned_mentor
            ORDER BY m.mentor_department, m.mentor_name, s.student_usn
        """)
        mentor_wise_result = db.execute(mentor_wise_query).fetchall()
        df_mentor_wise = pd.DataFrame(mentor_wise_result)
        df_mentor_wise = df_mentor_wise.fillna("")
        assigned_count = len(df_mentor_wise)

        # --- 3. Summary (mentor count, assigned count, unassigned count) ---
        total_mentors = db.execute(text("SELECT COUNT(*) FROM mentors")).scalar() or 0
        summary_rows = [
            {"Metric": "Total Mentors", "Count": total_mentors},
            {"Metric": "Students Assigned to a Mentor", "Count": assigned_count},
            {"Metric": "Students NOT Assigned (No Mentor)", "Count": unassigned_count},
            {"Metric": "Total Students (Assigned + Unassigned)", "Count": assigned_count + unassigned_count},
        ]
        df_summary = pd.DataFrame(summary_rows)

        # --- Output file ---
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"mentor_wise_students_and_unassigned_{timestamp}.xlsx"
        if not output_filename.endswith(".xlsx"):
            output_filename += ".xlsx"

        print(f"Creating: {output_filename}")
        with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            df_mentor_wise.to_excel(writer, sheet_name="Mentor-wise Students", index=False)
            df_unassigned.to_excel(writer, sheet_name="Unassigned Students", index=False)

            wb = writer.book
            for sheet_name in ["Summary", "Mentor-wise Students", "Unassigned Students"]:
                ws = writer.sheets[sheet_name]
                for col in ws.columns:
                    ws.column_dimensions[col[0].column_letter].width = 18
                if sheet_name == "Summary":
                    ws.column_dimensions["A"].width = 40
                    ws.column_dimensions["B"].width = 12

        print(f"\nDone: {output_filename}")
        print(f"  Summary: {total_mentors} mentors, {assigned_count} assigned, {unassigned_count} unassigned")
        print(f"  Sheets: Summary | Mentor-wise Students | Unassigned Students")
        print("=" * 70)
        return output_filename

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    export_mentor_wise_and_unassigned(out)
