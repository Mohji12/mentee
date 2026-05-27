#!/usr/bin/env python3
"""
Delete a student record from the database
WARNING: This will permanently delete the record!
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import all models to register them
from app.db.models import counseling, activities, query, mentors, admin, login, forgot_password, MCA_assignments, meetings, mentee_competency_report, psychometric_responses, report, swot, competencies, activities_tracking, activity_submissions, attendance

from app.db.database import SessionLocal, DATABASE_URL
from app.db.models.students import Student

def delete_student(email=None, usn=None):
    """Delete student by email or USN"""
    db = SessionLocal()
    try:
        print("=" * 70)
        print("DELETE STUDENT RECORD")
        print("=" * 70)
        print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '***'}")
        print()
        
        if not email and not usn:
            print("[ERROR] Please provide either email or USN")
            return False
        
        # Find the student
        query_filter = None
        if email and usn:
            query_filter = db.query(Student).filter(
                (Student.student_email == email) | (Student.student_usn == usn)
            )
        elif email:
            query_filter = db.query(Student).filter(Student.student_email == email)
        elif usn:
            query_filter = db.query(Student).filter(Student.student_usn == usn)
        
        student = query_filter.first()
        
        if not student:
            print(f"[NOT FOUND] No student found with:")
            if email:
                print(f"  Email: '{email}'")
            if usn:
                print(f"  USN: '{usn}'")
            return False
        
        print(f"[FOUND] Student record:")
        print(f"  USN: '{student.student_usn}' (length: {len(student.student_usn)})")
        print(f"  Email: '{student.student_email}'")
        print()
        
        # Confirm deletion
        print("WARNING: This will permanently delete the student record!")
        response = input("Type 'DELETE' to confirm: ")
        
        if response != 'DELETE':
            print("[CANCELLED] Deletion cancelled")
            return False
        
        # Delete the student
        db.delete(student)
        db.commit()
        
        print()
        print("[SUCCESS] Student record deleted successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    email = None
    usn = None
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        usn = sys.argv[2]
    
    if not email and not usn:
        print("Usage: python delete_student_record.py <email> [usn]")
        print("Example: python delete_student_record.py mili.25008261@jainuniversity.ac.in")
        sys.exit(1)
    
    success = delete_student(email, usn)
    sys.exit(0 if success else 1)

