#!/usr/bin/env python3
"""
Export Mentor-Student Assignment Data to Excel
Groups students by mentor and department
"""

import sys
import os
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import database and models
from app.db.database import SessionLocal, DATABASE_URL
from app.db.models.mentors import Mentor
from app.db.models.students import Student
from sqlalchemy import func, text
import pandas as pd

def export_mentor_students_to_excel(output_filename=None):
    """
    Export mentor-student assignment data to Excel, grouped by department
    
    Args:
        output_filename: Optional filename for the Excel file. 
                        If None, generates a timestamped filename.
    """
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("EXPORTING MENTOR-STUDENT DATA TO EXCEL")
        print("=" * 80)
        print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '***'}")
        print()
        
        # Query 1: Students assigned to each mentor, grouped by department
        print("Fetching mentor-student assignment data...")
        query = text("""
            SELECT 
                m.mentor_department AS department,
                m.mentor_id,
                m.mentor_name,
                m.mentor_email,
                COUNT(s.student_usn) AS student_count
            FROM 
                mentors m
            LEFT JOIN 
                students s ON m.mentor_id = s.assigned_mentor
            GROUP BY 
                m.mentor_department, m.mentor_id, m.mentor_name, m.mentor_email
            ORDER BY 
                m.mentor_department, student_count DESC, m.mentor_name
        """)
        
        result = db.execute(query)
        mentor_data = result.fetchall()
        
        # Convert to DataFrame
        mentor_df = pd.DataFrame(mentor_data, columns=[
            'Department', 'Mentor ID', 'Mentor Name', 'Mentor Email', 'Student Count'
        ])
        
        # Query 2: Department-wise summary
        print("Fetching department-wise summary...")
        dept_query = text("""
            SELECT 
                m.mentor_department AS department,
                COUNT(DISTINCT m.mentor_id) AS total_mentors,
                COUNT(s.student_usn) AS total_students
            FROM 
                mentors m
            LEFT JOIN 
                students s ON m.mentor_id = s.assigned_mentor
            GROUP BY 
                m.mentor_department
            ORDER BY 
                total_students DESC
        """)
        
        dept_result = db.execute(dept_query)
        dept_data = dept_result.fetchall()
        
        dept_df = pd.DataFrame(dept_data, columns=[
            'Department', 'Total Mentors', 'Total Students'
        ])
        
        # Query 3: Detailed student list with mentor information
        print("Fetching detailed student list...")
        detail_query = text("""
            SELECT 
                m.mentor_department AS department,
                m.mentor_id,
                m.mentor_name AS mentor_name,
                s.student_usn,
                s.student_name,
                s.student_email,
                s.student_program,
                s.semester,
                s.student_batch
            FROM 
                mentors m
            INNER JOIN 
                students s ON m.mentor_id = s.assigned_mentor
            ORDER BY 
                m.mentor_department, m.mentor_name, s.student_usn
        """)
        
        detail_result = db.execute(detail_query)
        detail_data = detail_result.fetchall()
        
        detail_df = pd.DataFrame(detail_data, columns=[
            'Department', 'Mentor ID', 'Mentor Name', 'Student USN', 
            'Student Name', 'Student Email', 'Program', 'Semester', 'Batch'
        ])
        
        # Generate filename if not provided
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"mentor_students_by_department_{timestamp}.xlsx"
        
        # Ensure .xlsx extension
        if not output_filename.endswith('.xlsx'):
            output_filename += '.xlsx'
        
        print(f"\nCreating Excel file: {output_filename}")
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            # Sheet 1: Mentor Summary (by department)
            mentor_df.to_excel(writer, sheet_name='Mentor Summary', index=False)
            
            # Sheet 2: Department Summary
            dept_df.to_excel(writer, sheet_name='Department Summary', index=False)
            
            # Sheet 3: Detailed Student List
            detail_df.to_excel(writer, sheet_name='Student Details', index=False)
            
            # Get workbook and worksheets for formatting
            workbook = writer.book
            
            # Format Mentor Summary sheet
            mentor_sheet = writer.sheets['Mentor Summary']
            mentor_sheet.column_dimensions['A'].width = 25  # Department
            mentor_sheet.column_dimensions['B'].width = 20  # Mentor ID
            mentor_sheet.column_dimensions['C'].width = 30  # Mentor Name
            mentor_sheet.column_dimensions['D'].width = 35  # Mentor Email
            mentor_sheet.column_dimensions['E'].width = 15  # Student Count
            
            # Format Department Summary sheet
            dept_sheet = writer.sheets['Department Summary']
            dept_sheet.column_dimensions['A'].width = 25  # Department
            dept_sheet.column_dimensions['B'].width = 15  # Total Mentors
            dept_sheet.column_dimensions['C'].width = 15  # Total Students
            
            # Format Student Details sheet
            detail_sheet = writer.sheets['Student Details']
            detail_sheet.column_dimensions['A'].width = 25  # Department
            detail_sheet.column_dimensions['B'].width = 20  # Mentor ID
            detail_sheet.column_dimensions['C'].width = 30  # Mentor Name
            detail_sheet.column_dimensions['D'].width = 20  # Student USN
            detail_sheet.column_dimensions['E'].width = 30  # Student Name
            detail_sheet.column_dimensions['F'].width = 35  # Student Email
            detail_sheet.column_dimensions['G'].width = 20  # Program
            detail_sheet.column_dimensions['H'].width = 12  # Semester
            detail_sheet.column_dimensions['I'].width = 15  # Batch
        
        print(f"\n✓ Excel file created successfully: {output_filename}")
        print(f"\nSummary:")
        print(f"  - Total Departments: {len(dept_df)}")
        print(f"  - Total Mentors: {len(mentor_df)}")
        print(f"  - Total Students: {len(detail_df)}")
        print(f"  - Total Students (with assignments): {mentor_df['Student Count'].sum()}")
        print(f"\nSheets created:")
        print(f"  1. Mentor Summary - Students per mentor grouped by department")
        print(f"  2. Department Summary - Total mentors and students per department")
        print(f"  3. Student Details - Complete student list with mentor information")
        print("=" * 80)
        
        return output_filename
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Allow custom filename from command line
    output_file = None
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    export_mentor_students_to_excel(output_file)
