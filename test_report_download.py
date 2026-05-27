"""
Test script to check report download endpoint
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.db.models.students import Student
from app.db.models.competencies import Competencies

client = TestClient(app)

def test_report_download():
    """Test the report download endpoint"""
    print("=" * 60)
    print("TESTING REPORT DOWNLOAD ENDPOINT")
    print("=" * 60)
    
    # Get a student with competencies
    db = SessionLocal()
    try:
        # Find a student with competencies
        student = db.query(Student).join(Competencies, Student.student_usn == Competencies.student_usn).first()
        
        if not student:
            print("[ERROR] No student with competencies found in database")
            return
        
        student_usn = student.student_usn
        print(f"\n[INFO] Testing with student USN: {student_usn}")
        print(f"[INFO] Student name: {student.student_name}")
        
        # Check if competencies exist
        competencies = db.query(Competencies).filter(Competencies.student_usn == student_usn).first()
        if competencies:
            print(f"[OK] Competencies found for student")
            print(f"  - Active_Listening: {competencies.Active_Listening}")
            print(f"  - Building_Trust: {competencies.Building_Trust}")
        else:
            print("[ERROR] No competencies found")
            return
        
        # Test the endpoint
        print(f"\n[INFO] Calling endpoint: /student/{student_usn}/reportdownload")
        response = client.get(f"/student/{student_usn}/reportdownload")
        
        print(f"\n[RESPONSE] Status Code: {response.status_code}")
        print(f"[RESPONSE] Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            content_length = response.headers.get("content-length", "0")
            
            print(f"[OK] Response received successfully")
            print(f"  - Content-Type: {content_type}")
            print(f"  - Content-Length: {content_length} bytes")
            
            if "application/pdf" in content_type:
                pdf_content = response.content
                print(f"[OK] PDF content received: {len(pdf_content)} bytes")
                
                # Check if it's a valid PDF
                if pdf_content.startswith(b"%PDF"):
                    print("[OK] Valid PDF file (starts with %PDF)")
                else:
                    print("[WARNING] Response doesn't start with %PDF")
                    print(f"  First 100 bytes: {pdf_content[:100]}")
            else:
                print(f"[ERROR] Expected PDF, got: {content_type}")
                print(f"  Response content: {response.text[:500]}")
        else:
            print(f"[ERROR] Request failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"  Error detail: {error_detail}")
            except:
                print(f"  Error text: {response.text[:500]}")
                
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception occurred: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
    finally:
        db.close()

if __name__ == "__main__":
    test_report_download()






