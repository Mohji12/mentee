#!/usr/bin/env python3
"""
Verify student data in database - check exact matches, case sensitivity, etc.
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import all models to register them (required for relationships)
from app.db.models import counseling, activities, query, mentors, admin, login, forgot_password, MCA_assignments, meetings, mentee_competency_report, psychometric_responses, report, swot, competencies, activities_tracking, activity_submissions, attendance

from app.db.database import SessionLocal, DATABASE_URL
from app.db.models.students import Student
from sqlalchemy import or_, func, text

def verify_student(email, usn=None):
    """Verify student data with detailed checks"""
    db = SessionLocal()
    try:
        print("=" * 70)
        print("VERIFYING STUDENT DATA IN DATABASE")
        print("=" * 70)
        print(f"Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '***'}")
        print()
        
        print(f"Searching for:")
        print(f"  Email: '{email}'")
        if usn:
            print(f"  USN: '{usn}'")
        print()
        
        # Check 1: Exact email match
        print("Check 1: Exact email match (case-sensitive)")
        exact_email = db.query(Student).filter(Student.student_email == email).first()
        if exact_email:
            print(f"  [FOUND] Email exists exactly as provided")
            print(f"    USN: '{exact_email.student_usn}'")
            print(f"    Email: '{exact_email.student_email}'")
            print(f"    Email length: {len(exact_email.student_email)}")
            print(f"    Input length: {len(email)}")
        else:
            print(f"  [NOT FOUND] No exact email match")
        
        print()
        
        # Check 2: Case-insensitive email match
        print("Check 2: Case-insensitive email match")
        case_insensitive = db.query(Student).filter(
            func.lower(Student.student_email) == func.lower(email)
        ).first()
        if case_insensitive and not exact_email:
            print(f"  [FOUND] Email exists with different case")
            print(f"    USN: '{case_insensitive.student_usn}'")
            print(f"    Email in DB: '{case_insensitive.student_email}'")
            print(f"    Your input: '{email}'")
        elif case_insensitive:
            print(f"  [SAME] Case-insensitive match (same as exact match)")
        else:
            print(f"  [NOT FOUND] No case-insensitive match")
        
        print()
        
        # Check 3: USN if provided
        if usn:
            print(f"Check 3: USN match")
            exact_usn = db.query(Student).filter(Student.student_usn == usn).first()
            if exact_usn:
                print(f"  [FOUND] USN exists")
                print(f"    USN: '{exact_usn.student_usn}'")
                print(f"    Email: '{exact_usn.student_email}'")
            else:
                print(f"  [NOT FOUND] USN does not exist")
            print()
        
        # Check 4: OR query (what the signup endpoint uses)
        print("Check 4: OR query (email OR USN) - This is what signup endpoint uses")
        if usn:
            or_query = db.query(Student).filter(
                or_(Student.student_email == email, Student.student_usn == usn)
            ).first()
        else:
            or_query = db.query(Student).filter(Student.student_email == email).first()
        
        if or_query:
            print(f"  [FOUND] Student found by OR query")
            print(f"    USN: '{or_query.student_usn}'")
            print(f"    Email: '{or_query.student_email}'")
            if or_query.student_email == email:
                print(f"    Match reason: EMAIL matches")
            elif usn and or_query.student_usn == usn:
                print(f"    Match reason: USN matches")
            else:
                print(f"    Match reason: UNKNOWN")
        else:
            print(f"  [NOT FOUND] No student found by OR query")
        
        print()
        
        # Check 5: Show all students with similar email
        print("Check 5: All students with similar email pattern")
        email_prefix = email.split('@')[0] if '@' in email else email
        similar = db.query(Student).filter(
            Student.student_email.like(f"%{email_prefix}%")
        ).limit(10).all()
        
        if similar:
            print(f"  Found {len(similar)} student(s) with similar email:")
            for student in similar:
                match_type = ""
                if student.student_email == email:
                    match_type = " [EXACT MATCH]"
                elif student.student_email.lower() == email.lower():
                    match_type = " [CASE DIFFERENCE]"
                print(f"    - USN: '{student.student_usn}' | Email: '{student.student_email}'{match_type}")
        else:
            print(f"  No similar emails found")
        
        print()
        
        # Check 6: Raw SQL query
        print("Check 6: Raw SQL query to verify")
        result = db.execute(text(
            "SELECT student_usn, student_email, LENGTH(student_email) as email_len FROM students WHERE student_email = :email"
        ), {"email": email})
        rows = result.fetchall()
        if rows:
            print(f"  [FOUND] Raw SQL found {len(rows)} row(s):")
            for row in rows:
                print(f"    USN: '{row[0]}' | Email: '{row[1]}' | Length: {row[2]}")
        else:
            print(f"  [NOT FOUND] Raw SQL found no rows")
        
        print()
        print("=" * 70)
        
        return or_query is not None
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    email = "mili.25008261@jainuniversity.ac.in"
    usn = None
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        usn = sys.argv[2]
    
    exists = verify_student(email, usn)
    print(f"\nResult: Email/USN {'EXISTS' if exists else 'DOES NOT EXIST'} in database")
    sys.exit(0 if not exists else 1)

