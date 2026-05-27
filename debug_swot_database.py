#!/usr/bin/env python3
"""
Debug script to check SWOT data in the database
Run this script to inspect what's stored in the swot and report tables
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from db.database import SessionLocal
from db.models.swot import SWOT
from db.models.report import Report
from db.models.students import Student

def debug_database():
    """Check what's in the SWOT and Report tables"""
    
    db = SessionLocal()
    
    try:
        print("🔍 Database Debug Information")
        print("=" * 50)
        
        # Check SWOT table
        print("\n📊 SWOT Table Contents:")
        print("-" * 30)
        swot_records = db.query(SWOT).all()
        print(f"Total SWOT records: {len(swot_records)}")
        
        for record in swot_records:
            print(f"\nStudent USN: {record.student_usn}")
            print(f"ID: {record.id}")
            print(f"Analysis Length: {len(record.swot_analysis) if record.swot_analysis else 0}")
            if record.swot_analysis:
                print(f"Analysis Preview: {record.swot_analysis[:200]}...")
            else:
                print("Analysis: None")
        
        # Check Report table
        print("\n📊 Report Table Contents:")
        print("-" * 30)
        report_records = db.query(Report).all()
        print(f"Total Report records: {len(report_records)}")
        
        for record in report_records:
            print(f"\nStudent USN: {record.student_usn}")
            print(f"ID: {record.id}")
            print(f"Strengths: {record.strengths[:50] if record.strengths else 'None'}...")
            print(f"Weaknesses: {record.weaknesses[:50] if record.weaknesses else 'None'}...")
            print(f"Opportunities: {record.opportunities[:50] if record.opportunities else 'None'}...")
            print(f"Threats: {record.threats[:50] if record.threats else 'None'}...")
        
        # Check for specific student if provided
        if len(sys.argv) > 1:
            student_usn = sys.argv[1]
            print(f"\n🎯 Specific Student Analysis: {student_usn}")
            print("-" * 40)
            
            # Check if student exists
            student = db.query(Student).filter_by(student_usn=student_usn).first()
            if not student:
                print(f"❌ Student {student_usn} not found in students table")
                return
            
            print(f"✅ Student found: {student.student_name}")
            
            # Check SWOT data
            swot_data = db.query(SWOT).filter_by(student_usn=student_usn).first()
            if swot_data:
                print(f"✅ SWOT data found")
                print(f"Analysis length: {len(swot_data.swot_analysis) if swot_data.swot_analysis else 0}")
            else:
                print("❌ No SWOT data found")
            
            # Check Report data
            report_data = db.query(Report).filter_by(student_usn=student_usn).first()
            if report_data:
                print(f"✅ Report data found")
                print(f"Strengths: {report_data.strengths}")
                print(f"Weaknesses: {report_data.weaknesses}")
                print(f"Opportunities: {report_data.opportunities}")
                print(f"Threats: {report_data.threats}")
            else:
                print("❌ No Report data found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_database()
