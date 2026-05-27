#!/usr/bin/env python3
"""
Check if a student email exists in the database
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import all models to register them (required for relationships)
from app.db.models import counseling, activities, query, mentors, admin, login, forgot_password, MCA_assignments, meetings, mentee_competency_report, psychometric_responses, report, swot, competencies, activities_tracking, activity_submissions, attendance

from app.db.database import SessionLocal
from app.db.models.students import Student
from sqlalchemy import or_, func

def check_email(email):
    """Check if email or similar emails exist"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print(f"Checking email: {email}")
        print("=" * 60)
        print()
        
        # Exact match
        exact_match = db.query(Student).filter(Student.student_email == email).first()
        if exact_match:
            print(f"[FOUND] Exact match found:")
            print(f"  USN: {exact_match.student_usn}")
            print(f"  Email: {exact_match.student_email}")
            return True
        
        # Case-insensitive search
        from sqlalchemy import func
        case_insensitive = db.query(Student).filter(
            func.lower(Student.student_email) == func.lower(email)
        ).first()
        if case_insensitive:
            print(f"[FOUND] Case-insensitive match found:")
            print(f"  USN: {case_insensitive.student_usn}")
            print(f"  Email: {case_insensitive.student_email}")
            print(f"  Note: Email in DB has different case!")
            return True
        
        # Check for similar emails (with/without spaces)
        email_trimmed = email.strip()
        if email_trimmed != email:
            trimmed_match = db.query(Student).filter(Student.student_email == email_trimmed).first()
            if trimmed_match:
                print(f"[FOUND] Match found (with trimmed whitespace):")
                print(f"  USN: {trimmed_match.student_usn}")
                print(f"  Email: {trimmed_match.student_email}")
                return True
        
        print("[NOT FOUND] Email does not exist in database")
        print()
        print("Checking for similar emails...")
        
        # Show similar emails
        email_prefix = email.split('@')[0] if '@' in email else email
        similar = db.query(Student).filter(
            Student.student_email.like(f"%{email_prefix}%")
        ).limit(5).all()
        
        if similar:
            print(f"Found {len(similar)} similar email(s):")
            for student in similar:
                print(f"  - {student.student_email} (USN: {student.student_usn})")
        else:
            print("No similar emails found")
        
        return False
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    email = "mili.25008261@jainuniversity.ac.in"
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    exists = check_email(email)
    sys.exit(0 if not exists else 1)

