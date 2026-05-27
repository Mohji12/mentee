from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.admin import Admin
from app.db.models.students import Student
from app.db.models.ibp_responses import IBPResponse
from app.utils.ibp_excel import generate_ibp_excel
import json
import zipfile
from io import BytesIO
from typing import Optional

router = APIRouter()


def _apply_filters(query, program: Optional[str] = None, mentor: Optional[str] = None, status: Optional[str] = None):
    if program:
        query = query.filter(Student.student_program == program)
    if mentor:
        query = query.filter(Student.assigned_mentor == mentor)
    return query


@router.get("/ibp-form/download-all")
def download_all_ibp_zip(
    admin_id: str,
    db: Session = Depends(get_db),
):
    """Download all students' IBP responses as ZIP file"""
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    students_with_responses = db.query(Student, IBPResponse).join(
        IBPResponse, Student.student_usn == IBPResponse.student_usn
    ).all()

    if not students_with_responses:
        raise HTTPException(status_code=404, detail="No students have submitted IBP forms")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for student, response in students_with_responses:
            try:
                # Debug: Print raw response data
                print(f"Processing student {student.student_usn}: raw responses = {response.responses[:100] if response.responses else 'None'}...")
                responses_dict = json.loads(response.responses)
                print(f"Parsed responses dict for {student.student_usn}: {len(responses_dict)} entries, sample = {dict(list(responses_dict.items())[:3])}")
                if not responses_dict:
                    print(f"Warning: Empty responses dict for student {student.student_usn}")
                    continue
                excel_file = generate_ibp_excel(
                    student_usn=student.student_usn,
                    student_name=student.student_name or "N/A",
                    student_program=student.student_program or "N/A",
                    responses=responses_dict,
                    submitted_at=response.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                )
                filename = f"IBP_{student.student_usn}_{student.student_name or 'Student'}.xlsx"
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
        headers={"Content-Disposition": "attachment; filename=IBP_All_Students.zip"},
    )


@router.get("/ibp-form/download-filtered")
def download_filtered_ibp_zip(
    admin_id: str,
    program: Optional[str] = Query(None, description="Filter by program"),
    mentor: Optional[str] = Query(None, description="Filter by mentor ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """Download filtered students' IBP responses as ZIP file"""
    admin = db.query(Admin).filter(Admin.admin_id == admin_id.strip()).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    query = db.query(Student, IBPResponse).join(
        IBPResponse, Student.student_usn == IBPResponse.student_usn
    )
    query = _apply_filters(query, program=program, mentor=mentor, status=status)
    students_with_responses = query.all()

    if not students_with_responses:
        raise HTTPException(
            status_code=404,
            detail="No students match the filter criteria or have submitted IBP forms",
        )

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for student, response in students_with_responses:
            try:
                # Debug: Print raw response data
                print(f"Processing student {student.student_usn}: raw responses = {response.responses[:100] if response.responses else 'None'}...")
                responses_dict = json.loads(response.responses)
                print(f"Parsed responses dict for {student.student_usn}: {len(responses_dict)} entries, sample = {dict(list(responses_dict.items())[:3])}")
                if not responses_dict:
                    print(f"Warning: Empty responses dict for student {student.student_usn}")
                    continue
                excel_file = generate_ibp_excel(
                    student_usn=student.student_usn,
                    student_name=student.student_name or "N/A",
                    student_program=student.student_program or "N/A",
                    responses=responses_dict,
                    submitted_at=response.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                )
                filename = f"IBP_{student.student_usn}_{student.student_name or 'Student'}.xlsx"
                zip_file.writestr(filename, excel_file.read())
            except Exception as e:
                print(f"Error generating Excel for student {student.student_usn}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

    zip_buffer.seek(0)
    filter_parts = []
    if program:
        filter_parts.append(f"Program_{program}")
    if mentor:
        filter_parts.append(f"Mentor_{mentor}")
    if status:
        filter_parts.append(f"Status_{status}")
    zip_filename = f"IBP_Filtered_{'_'.join(filter_parts) if filter_parts else 'All'}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"},
    )
