from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.pf16_responses import PF16Response
from app.schemas.pf16 import PF16FormSubmit, PF16FormResponse, PF16QuestionResponse, PF16LockStatus
from app.core.dependencies import get_current_student
from app.utils.pf16_questions import get_all_questions
from app.utils.pf16_excel import generate_pf16_excel
import json

router = APIRouter()


@router.get("/pf16-form", response_model=PF16FormResponse)
def get_pf16_form(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Get all 16PF questions and check if form is locked"""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already submitted
    existing_response = db.query(PF16Response).filter(
        PF16Response.student_usn == student_usn.strip()
    ).first()
    
    is_locked = existing_response is not None
    submitted_at = existing_response.submitted_at if existing_response else None
    
    # Parse responses if form is locked
    responses = None
    if existing_response and existing_response.responses:
        try:
            responses_dict = json.loads(existing_response.responses)
            # Keep keys as strings (JSON standard) - frontend will handle conversion
            responses = {str(k): v for k, v in responses_dict.items()}
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing PF16 responses: {e}")
            responses = None
    
    # Get all questions
    questions_data = get_all_questions()
    questions = [
        PF16QuestionResponse(
            question_number=q["question_number"],
            text=q["text"],
            options=q["options"]
        )
        for q in questions_data
    ]
    
    return PF16FormResponse(
        questions=questions,
        is_locked=is_locked,
        submitted_at=submitted_at,
        responses=responses
    )


@router.get("/pf16-form/lock-status", response_model=PF16LockStatus)
def get_pf16_lock_status(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Check if 16PF form is locked"""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    existing_response = db.query(PF16Response).filter(
        PF16Response.student_usn == student_usn.strip()
    ).first()
    
    if existing_response:
        return PF16LockStatus(
            is_locked=True,
            submitted_at=existing_response.submitted_at,
            message=f"16PF form already submitted on {existing_response.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}. No further submissions allowed."
        )
    else:
        return PF16LockStatus(
            is_locked=False,
            submitted_at=None,
            message="16PF form is available for submission."
        )


@router.post("/pf16-form")
def submit_pf16_form(
    student_usn: str,
    form: PF16FormSubmit,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Submit 16PF form responses. Form is locked after first submission."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if already submitted
    existing_response = db.query(PF16Response).filter(
        PF16Response.student_usn == student_usn.strip()
    ).first()
    
    if existing_response:
        raise HTTPException(
            status_code=400,
            detail=f"16PF form already submitted on {existing_response.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}. No further submissions allowed."
        )
    
    # Validate responses
    if not form.responses:
        raise HTTPException(status_code=400, detail="No responses provided")
    
    # Validate all answers are a, b, or c
    for q_num, answer in form.responses.items():
        if answer not in ["a", "b", "c"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer '{answer}' for question {q_num}. Must be 'a', 'b', or 'c'."
            )
    
    # Store responses as JSON string
    responses_json = json.dumps(form.responses)
    
    # Create new response record
    new_response = PF16Response(
        student_usn=student_usn.strip(),
        responses=responses_json
    )
    
    db.add(new_response)
    db.commit()
    db.refresh(new_response)
    
    return {
        "message": "16PF form submitted successfully",
        "submitted_at": new_response.submitted_at.isoformat()
    }


@router.get("/pf16-form/download")
def download_pf16_excel(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """16PF Excel download is restricted to admin only. Mentees cannot download."""
    raise HTTPException(
        status_code=403,
        detail="Only admin can download 16PF Excel reports. Please contact your administrator."
    )
