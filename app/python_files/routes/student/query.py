from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.students import Student
from app.db.models.query import Query
from app.utils.id_utils import generate_query_id
from app.services.email_services import send_email
from app.schemas.query import QueryWithUSN, QueryResponse, QueryNewStudent

router = APIRouter()

@router.post("/submit-query/with-usn", response_model=QueryResponse)
def submit_query_with_usn(query_data: QueryWithUSN, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_usn == query_data.usn).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # If student name is missing, update it
    if not student.student_name:
        if not query_data.name:  # Ensure name is provided by user
            raise HTTPException(status_code=400, detail="Student name is missing. Please provide it.")
        student.student_name = query_data.name
        db.commit()

    # Generate query ID and create new query
    query_id = generate_query_id(db)
    new_query = Query(
        id=query_id,
        usn=query_data.usn,
        name=student.student_name,
        email=student.student_email,
        phoneno=student.student_phoneno,
        program=student.student_program,
        ass_mentor=student.assigned_mentor,
        query_issue=query_data.query_issue
    )

    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    # Prepare and send the email
    subject = f"Confirmation of Your Query Submission – Query ID: {query_id}"
    body = f"""
    Dear {student.student_name},

    Thank you for reaching out to us. Your query has been successfully submitted, and our team will review it shortly. Below are the details of your submission:

    Query Details:
    - Query ID: {query_id}
    - USN: {query_data.usn}
    - Name: {student.student_name}
    - Email: {student.student_email}
    - Query Issue: {query_data.query_issue}

    Our support team will get back to you as soon as possible with a resolution or further updates. If you have any additional information to provide, please reply to this email.

    Best regards,
    Support Team
    Mentee Tracker Team
    """

    send_email(student.student_email, subject, body)

    return new_query


@router.post("/submit-query/new-student", response_model=QueryResponse)
def submit_query_new_student(query_data: QueryNewStudent, db: Session = Depends(get_db)):
    # Ensure all required fields are present except USN (which can be empty)
    if not (query_data.name and query_data.email and query_data.phoneno and query_data.program):
        raise HTTPException(status_code=400, detail="Missing required details for a new student")

    # Generate query ID
    query_id = generate_query_id(db)

    # Create new query entry (USN can be empty)
    new_query = Query(
        id=query_id,
        usn=query_data.usn if query_data.usn else None,  # Allow NULL USN
        name=query_data.name,
        email=query_data.email,
        phoneno=query_data.phoneno,
        program=query_data.program,
        query_issue=query_data.query_issue
    )

    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    # Prepare and send the email
    subject = f"Confirmation of Your Query Submission – Query ID: {query_id}"
    body = f"""
    Dear {query_data.name},

    Thank you for reaching out to us. Your query has been successfully submitted, and our team will review it shortly. Below are the details of your submission:

    Query Details:
    - Query ID: {query_id}
    - USN: {query_data.usn if query_data.usn else 'N/A'}
    - Name: {query_data.name}
    - Query Issue: {query_data.query_issue}

    Our support team will get back to you as soon as possible with a resolution or further updates. If you have any additional information to provide, please reply to this email.

    Best regards,
    Support Team
    Mentee Tracker Team
    """

    send_email(query_data.email, subject, body)

    return new_query


@router.get("/check-usn")
def check_usn(usn: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_usn == usn).first()
    if student:
        return {"exists": True, "name": student.student_name,"email": student.student_email,"phoneno": student.student_phoneno,"program": student.student_program,"batch": student.student_batch,"semester": student.semester}
    return {"exists": False}