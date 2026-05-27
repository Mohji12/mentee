from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models.admin import Admin
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.pf16_responses import PF16Response
# Admin routes don't use get_current_admin - they use admin_id from path
from app.utils.pf16_excel import generate_pf16_excel
import json
import zipfile
from io import BytesIO
from typing import Optional

router = APIRouter()


def _apply_filters(query, program: Optional[str] = None, mentor: Optional[str] = None, status: Optional[str] = None):
    """Apply filters to student query"""
    if program:
        query = query.filter(Student.student_program == program)
    if mentor:
        query = query.filter(Student.assigned_mentor == mentor)
    # Status filter would need to check various conditions - simplified for now
    return query


@router.get("/pf16-form/download-all")
def download_all_pf16_zip(
    admin_id: str,
    db: Session = Depends(get_db),
):
    """Download all students' 16PF responses as ZIP file"""
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Get all students with PF16 responses
    students_with_responses = db.query(Student, PF16Response).join(
        PF16Response, Student.student_usn == PF16Response.student_usn
    ).all()
    
    if not students_with_responses:
        raise HTTPException(status_code=404, detail="No students have submitted 16PF forms")
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for student, response in students_with_responses:
            try:
                # Debug: Print raw response data
                print(f"Processing student {student.student_usn}: raw responses = {response.responses[:100] if response.responses else 'None'}...")
                responses_dict = json.loads(response.responses)
                print(f"Parsed responses dict for {student.student_usn}: {len(responses_dict)} entries, sample = {dict(list(responses_dict.items())[:3])}")
                if not responses_dict:
                    print(f"Warning: Empty responses dict for student {student.student_usn}")
                    continue
                
                # Generate Excel for this student
                excel_file = generate_pf16_excel(
                    student_usn=student.student_usn,
                    student_name=student.student_name or "N/A",
                    student_program=student.student_program or "N/A",
                    responses=responses_dict,
                    submitted_at=response.submitted_at.strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # Add to ZIP
                filename = f"16PF_{student.student_usn}_{student.student_name or 'Student'}.xlsx"
                zip_file.writestr(filename, excel_file.read())
            except Exception as e:
                print(f"Error generating Excel for student {student.student_usn}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=16PF_All_Students.zip"}
    )


@router.get("/pf16-form/download-filtered")
def download_filtered_pf16_zip(
    admin_id: str,
    program: Optional[str] = Query(None, description="Filter by program"),
    mentor: Optional[str] = Query(None, description="Filter by mentor ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """Download filtered students' 16PF responses as ZIP file"""
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Start with base query
    query = db.query(Student, PF16Response).join(
        PF16Response, Student.student_usn == PF16Response.student_usn
    )
    
    # Apply filters
    query = _apply_filters(query, program=program, mentor=mentor, status=status)
    
    students_with_responses = query.all()
    
    if not students_with_responses:
        raise HTTPException(
            status_code=404,
            detail="No students match the filter criteria or have submitted 16PF forms"
        )
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for student, response in students_with_responses:
            try:
                # Debug: Print raw response data
                print(f"Processing student {student.student_usn}: raw responses = {response.responses[:100] if response.responses else 'None'}...")
                responses_dict = json.loads(response.responses)
                print(f"Parsed responses dict for {student.student_usn}: {len(responses_dict)} entries, sample = {dict(list(responses_dict.items())[:3])}")
                if not responses_dict:
                    print(f"Warning: Empty responses dict for student {student.student_usn}")
                    continue
                
                # Generate Excel for this student
                excel_file = generate_pf16_excel(
                    student_usn=student.student_usn,
                    student_name=student.student_name or "N/A",
                    student_program=student.student_program or "N/A",
                    responses=responses_dict,
                    submitted_at=response.submitted_at.strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # Add to ZIP
                filename = f"16PF_{student.student_usn}_{student.student_name or 'Student'}.xlsx"
                zip_file.writestr(filename, excel_file.read())
            except Exception as e:
                print(f"Error generating Excel for student {student.student_usn}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

    zip_buffer.seek(0)
    
    # Build filename with filter info
    filter_parts = []
    if program:
        filter_parts.append(f"Program_{program}")
    if mentor:
        filter_parts.append(f"Mentor_{mentor}")
    if status:
        filter_parts.append(f"Status_{status}")
    
    zip_filename = f"16PF_Filtered_{'_'.join(filter_parts) if filter_parts else 'All'}.zip"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )
