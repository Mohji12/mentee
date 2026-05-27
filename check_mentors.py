#!/usr/bin/env python3
"""
Check if mentor emails exist in the database
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import all models to register them
from app.db.models import counseling, activities, query, mentors, admin, login, forgot_password, MCA_assignments, meetings, mentee_competency_report, psychometric_responses, report, swot, competencies, activities_tracking, activity_submissions, attendance, students

from app.db.database import SessionLocal, DATABASE_URL
from app.db.models.mentors import Mentor
from sqlalchemy import func

def check_mentors(emails):
    """Check which mentor emails exist in database"""
    db = SessionLocal()
    try:
        print("=" * 70)
        print("CHECKING MENTORS IN DATABASE")
        print("=" * 70)
        print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '***'}")
        print()
        
        results = []
        found_count = 0
        not_found_count = 0
        
        for email in emails:
            email = email.strip()
            if not email:
                continue
                
            # Exact match
            mentor = db.query(Mentor).filter(Mentor.mentor_email == email).first()
            
            if mentor:
                found_count += 1
                results.append({
                    'email': email,
                    'found': True,
                    'mentor_id': mentor.mentor_id,
                    'name': mentor.mentor_name,
                    'department': mentor.mentor_department,
                    'phone': mentor.mentor_phoneno
                })
            else:
                # Try case-insensitive
                mentor_ci = db.query(Mentor).filter(
                    func.lower(Mentor.mentor_email) == func.lower(email)
                ).first()
                
                if mentor_ci:
                    found_count += 1
                    results.append({
                        'email': email,
                        'found': True,
                        'mentor_id': mentor_ci.mentor_id,
                        'name': mentor_ci.mentor_name,
                        'department': mentor_ci.mentor_department,
                        'phone': mentor_ci.mentor_phoneno,
                        'note': f'Case difference: DB has "{mentor_ci.mentor_email}"'
                    })
                else:
                    not_found_count += 1
                    results.append({
                        'email': email,
                        'found': False
                    })
        
        # Print results
        print(f"Total emails checked: {len(emails)}")
        print(f"Found: {found_count}")
        print(f"Not found: {not_found_count}")
        print()
        print("=" * 70)
        print("DETAILED RESULTS")
        print("=" * 70)
        print()
        
        # Group by found/not found
        found_mentors = [r for r in results if r['found']]
        not_found_mentors = [r for r in results if not r['found']]
        
        if found_mentors:
            print("[FOUND] Mentors present in database:")
            print("-" * 70)
            for r in found_mentors:
                try:
                    print(f"  [OK] {r['email']}")
                    print(f"    ID: {r['mentor_id']}")
                    print(f"    Name: {r['name']}")
                    print(f"    Department: {r['department']}")
                    print(f"    Phone: {r['phone']}")
                    if 'note' in r:
                        print(f"    Note: {r['note']}")
                    print()
                except UnicodeEncodeError:
                    # Handle Unicode characters that can't be printed
                    print(f"  [OK] {r['email']}")
                    print(f"    ID: {r['mentor_id']}")
                    print(f"    Name: {r['name'].encode('ascii', 'ignore').decode('ascii')}")
                    print(f"    Department: {r['department'].encode('ascii', 'ignore').decode('ascii')}")
                    print(f"    Phone: {r['phone']}")
                    if 'note' in r:
                        print(f"    Note: {r['note']}")
                    print()
        
        if not_found_mentors:
            print("[NOT FOUND] Mentors NOT in database:")
            print("-" * 70)
            for r in not_found_mentors:
                print(f"  [NOT FOUND] {r['email']}")
            print()
        
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Found: {found_count}/{len(emails)}")
        print(f"Not Found: {not_found_count}/{len(emails)}")
        
        return found_count, not_found_count
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0, 0
    finally:
        db.close()

if __name__ == "__main__":
    # List of mentor emails from the image
    mentor_emails = [
        'satarupa.anderson@jainuniversity.ac.in',
        'dhivya.v@jainuniversity.ac.in',
        'richa.singh@jainuniversity.ac.in',
        't.gokul@jainuniversity.ac.in',
        'as.greesha@jainuniversity.ac.in',
        'd.kunal@jainuniversity.ac.in',
        'santosh.sc@jainuniversity.ac.in',
        'anjo.george@jainuniversity.ac.in',
        'manjushab@jainuniversity.ac.in',
        'pramod.t@jainuniversity.ac.in',
        'b.nayana@jainuniversity.ac.in',
        'w.wakeel@jainuniversity.ac.in',
        'mohith.s.yadav@jainuniversity.ac.in',
        'sharonjohn@jainuniversity.ac.in'
    ]
    
    # Allow custom emails from command line
    if len(sys.argv) > 1:
        mentor_emails = sys.argv[1:]
    
    found, not_found = check_mentors(mentor_emails)
    sys.exit(0 if not_found == 0 else 1)

