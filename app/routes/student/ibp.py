from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.ibp_responses import IBPResponse
from app.schemas.ibp import (
    IBPFormSubmit,
    IBPFormResponse,
    IBPQuestionResponse,
    IBPLockStatus,
)
from app.core.dependencies import get_current_student
from app.utils.ibp_questions import get_all_questions
from app.utils.ibp_excel import generate_ibp_excel
import json

router = APIRouter()


@router.get("/ibp-form", response_model=IBPFormResponse)
def get_ibp_form(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Get all IBP questions and check if form is locked"""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")

    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing_response = (
        db.query(IBPResponse).filter(IBPResponse.student_usn == student_usn.strip()).first()
    )

    is_locked = existing_response is not None
    submitted_at = existing_response.submitted_at if existing_response else None

    # Parse responses if form is locked
    responses = None
    if existing_response and existing_response.responses:
        try:
            responses_dict = json.loads(existing_response.responses)
            # Keep keys as strings (JSON standard) but ensure values are integers
            responses = {str(k): int(v) for k, v in responses_dict.items()}
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing IBP responses: {e}")
            responses = None

    questions_data = get_all_questions()
    questions = [
        IBPQuestionResponse(
            question_number=q["question_number"],
            text=q["text"],
            options=q["options"],
        )
        for q in questions_data
    ]

    return IBPFormResponse(
        questions=questions,
        is_locked=is_locked,
        submitted_at=submitted_at,
        responses=responses,
    )


@router.get("/ibp-form/lock-status", response_model=IBPLockStatus)
def get_ibp_lock_status(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Check if IBP form is locked"""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")

    existing_response = (
        db.query(IBPResponse).filter(IBPResponse.student_usn == student_usn.strip()).first()
    )

    if existing_response:
        return IBPLockStatus(
            is_locked=True,
            submitted_at=existing_response.submitted_at,
            message=f"IBP form already submitted on {existing_response.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}. No further submissions allowed.",
        )
    return IBPLockStatus(
        is_locked=False,
        submitted_at=None,
        message="IBP form is available for submission.",
    )


@router.post("/ibp-form")
def submit_ibp_form(
    student_usn: str,
    form: IBPFormSubmit,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """Submit IBP form responses. Form is locked after first submission."""
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")

    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing_response = (
        db.query(IBPResponse).filter(IBPResponse.student_usn == student_usn.strip()).first()
    )

    if existing_response:
        raise HTTPException(
            status_code=400,
            detail=f"IBP form already submitted on {existing_response.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}. No further submissions allowed.",
        )

    if not form.responses:
        raise HTTPException(status_code=400, detail="No responses provided")

    for q_num, answer in form.responses.items():
        if answer not in (1, 2, 3, 4, 5):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer '{answer}' for question {q_num}. Must be 1, 2, 3, 4, or 5.",
            )

    # JSON keys will be strings when serializing int keys
    responses_json = json.dumps({str(k): v for k, v in form.responses.items()})

    new_response = IBPResponse(
        student_usn=student_usn.strip(),
        responses=responses_json,
    )

    db.add(new_response)
    db.commit()
    db.refresh(new_response)

    return {
        "message": "IBP form submitted successfully",
        "submitted_at": new_response.submitted_at.isoformat(),
    }


@router.get("/ibp-form/download")
def download_ibp_excel(
    student_usn: str,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """IBP Excel download is restricted to admin only. Mentees cannot download."""
    raise HTTPException(
        status_code=403,
        detail="Only admin can download IBP Excel reports. Please contact your administrator."
    )
