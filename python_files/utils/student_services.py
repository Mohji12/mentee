from sqlalchemy.orm import Session
from app.db.models.students import Student
import datetime

# Function to calculate semester
def calculate_semester(student_batch: str) -> int:
    start_year = int(student_batch.split('-')[0])
    current_date = datetime.utcnow()

    # Calculate months since the batch's start
    months_since_batch_start = (current_date.year - start_year) * 12 + current_date.month - 7  # Start month is July

    # Semester calculation
    semester = (months_since_batch_start // 6) + 1
    if semester > 8:  # Cap semester for a 4-year program
        semester = 8
    if semester < 1:
        semester = 1
    return semester

# Task to auto-update the semester for all students
def update_student_semesters(db: Session):
    students = db.query(Student).all()
    for student in students:
        updated_semester = calculate_semester(student.student_batch)
        student.semester = updated_semester
        db.add(student)
    db.commit()
    print("Student semesters updated.")
