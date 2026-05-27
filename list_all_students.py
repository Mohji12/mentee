#!/usr/bin/env python3
"""
List all students in database to verify what's actually there
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import all models to register them
from app.db.models import counseling, activities, query, mentors, admin, login, forgot_password, MCA_assignments, meetings, mentee_competency_report, psychometric_responses, report, swot, competencies, activities_tracking, activity_submissions, attendance

from app.db.database import SessionLocal
from app.db.models.students import Student

def list_students():
    """List all students"""
    db = SessionLocal()
    try:
        print("=" * 70)
        print("ALL STUDENTS IN DATABASE")
        print("=" * 70)
        
        students = db.query(Student).all()
        print(f"Total students: {len(students)}")
        print()
        
        if students:
            print(f"{'USN':<20} {'Email':<40} {'Email Length':<12}")
            print("-" * 70)
            for student in students:
                usn_display = repr(student.student_usn)  # Show whitespace
                email_display = repr(student.student_email)  # Show whitespace
                print(f"{usn_display:<20} {email_display:<40} {len(student.student_email):<12}")
        else:
            print("No students found in database")
        
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    list_students()

