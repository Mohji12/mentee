#!/usr/bin/env python3
"""
Check how many students are assigned to each mentor and their details
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import all models to register them
from app.db.models import counseling, activities, query, mentors, admin, login, forgot_password, MCA_assignments, meetings, mentee_competency_report, psychometric_responses, report, swot, competencies, activities_tracking, activity_submissions, attendance, students

from app.db.database import SessionLocal, DATABASE_URL
from app.db.models.mentors import Mentor
from app.db.models.students import Student
from sqlalchemy import func

def check_mentor_students(mentor_emails):
    """Check students assigned to each mentor"""
    db = SessionLocal()
    try:
        print("=" * 80)
        print("MENTOR-STUDENT ASSIGNMENT REPORT")
        print("=" * 80)
        print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else '***'}")
        print()
        
        total_students = 0
        mentors_with_students = 0
        mentors_without_students = 0
        
        for email in mentor_emails:
            email = email.strip()
            if not email:
                continue
            
            # Find mentor
            mentor = db.query(Mentor).filter(Mentor.mentor_email == email).first()
            
            if not mentor:
                # Try case-insensitive
                mentor = db.query(Mentor).filter(
                    func.lower(Mentor.mentor_email) == func.lower(email)
                ).first()
            
            if not mentor:
                print(f"[NOT FOUND] Mentor: {email}")
                print("  No mentor record found in database")
                print()
                continue
            
            # Find students assigned to this mentor
            assigned_students = db.query(Student).filter(
                Student.assigned_mentor == mentor.mentor_id
            ).all()
            
            student_count = len(assigned_students)
            total_students += student_count
            
            print("=" * 80)
            try:
                print(f"MENTOR: {mentor.mentor_name}")
            except UnicodeEncodeError:
                print(f"MENTOR: {mentor.mentor_name.encode('ascii', 'ignore').decode('ascii')}")
            print("=" * 80)
            print(f"  Email: {mentor.mentor_email}")
            print(f"  ID: {mentor.mentor_id}")
            try:
                print(f"  Department: {mentor.mentor_department}")
            except UnicodeEncodeError:
                print(f"  Department: {mentor.mentor_department.encode('ascii', 'ignore').decode('ascii')}")
            print(f"  Phone: {mentor.mentor_phoneno}")
            print()
            print(f"  Total Students Assigned: {student_count}")
            print()
            
            if student_count > 0:
                mentors_with_students += 1
                print("  STUDENT DETAILS:")
                print("-" * 80)
                print(f"  {'USN':<20} {'Name':<30} {'Email':<35} {'Program':<20} {'Semester':<10}")
                print("-" * 80)
                
                for student in assigned_students:
                    try:
                        name = student.student_name or 'N/A'
                        program = student.student_program or 'N/A'
                        semester = str(student.semester) if student.semester else 'N/A'
                        
                        # Truncate long names/emails for display
                        name_display = name[:28] + '..' if len(name) > 30 else name
                        email_display = student.student_email[:33] + '..' if len(student.student_email) > 35 else student.student_email
                        program_display = program[:18] + '..' if len(program) > 20 else program
                        
                        print(f"  {student.student_usn:<20} {name_display:<30} {email_display:<35} {program_display:<20} {semester:<10}")
                    except UnicodeEncodeError:
                        # Handle Unicode characters
                        name = (student.student_name or 'N/A').encode('ascii', 'ignore').decode('ascii')
                        program = (student.student_program or 'N/A').encode('ascii', 'ignore').decode('ascii')
                        semester = str(student.semester) if student.semester else 'N/A'
                        
                        name_display = name[:28] + '..' if len(name) > 30 else name
                        email_display = student.student_email[:33] + '..' if len(student.student_email) > 35 else student.student_email
                        program_display = program[:18] + '..' if len(program) > 20 else program
                        
                        print(f"  {student.student_usn:<20} {name_display:<30} {email_display:<35} {program_display:<20} {semester:<10}")
                
                print()
                
                # Additional statistics
                programs = {}
                semesters = {}
                batches = {}
                
                for student in assigned_students:
                    # Count by program
                    program = student.student_program or 'Unknown'
                    programs[program] = programs.get(program, 0) + 1
                    
                    # Count by semester
                    semester = student.semester or 'Unknown'
                    semesters[semester] = semesters.get(semester, 0) + 1
                    
                    # Count by batch
                    batch = student.student_batch or 'Unknown'
                    batches[batch] = batches.get(batch, 0) + 1
                
                print("  STATISTICS:")
                print(f"    Programs: {', '.join([f'{k} ({v})' for k, v in sorted(programs.items())])}")
                # Sort semesters handling mixed types
                semester_items = sorted(semesters.items(), key=lambda x: (isinstance(x[0], str), str(x[0])))
                print(f"    Semesters: {', '.join([f'{k} ({v})' for k, v in semester_items])}")
                if batches:
                    print(f"    Batches: {', '.join([f'{k} ({v})' for k, v in sorted(batches.items())])}")
                print()
            else:
                mentors_without_students += 1
                print("  [NO STUDENTS ASSIGNED]")
                print()
        
        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total mentors checked: {len(mentor_emails)}")
        print(f"Mentors with students: {mentors_with_students}")
        print(f"Mentors without students: {mentors_without_students}")
        print(f"Total students assigned: {total_students}")
        print(f"Average students per mentor: {total_students / mentors_with_students if mentors_with_students > 0 else 0:.2f}")
        print("=" * 80)
        
        return mentors_with_students, mentors_without_students, total_students
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0, 0, 0
    finally:
        db.close()

if __name__ == "__main__":
    # List of mentor emails from previous check
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
    
    check_mentor_students(mentor_emails)

