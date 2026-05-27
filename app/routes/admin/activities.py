from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.models.admin import Admin
from app.db.database import get_db
from app.db.models.activities import Activities
from app.db.models.students import Student

router = APIRouter()

@router.get("/activities")
def get_all_students_activities(admin_id: str, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail=f"Admin with ID {admin_id} not found")

    # Optimized query: Load student and mentor data in one go using joinedload
    student_activities = db.query(Activities).options(
        joinedload(Activities.student).joinedload(Student.mentor)  # Eager loading
    ).all()

    activities = []
    for activity in student_activities:
        student = activity.student
        if not student:  # Should ideally not happen due to ForeignKey constraint
            continue

        mentor = student.mentor
        mentor_name = mentor.mentor_name if mentor else "Unknown"

        for activity_column, duration_type in [
            ("short_term", "Short Term"),
            ("short_term1", "Short Term"),
            ("short_term2", "Short Term"),
            ("mid_term", "Mid Term"),
            ("mid_term1", "Mid Term"),
            ("mid_term2", "Mid Term"),
            ("long_term", "Long Term"),
            ("long_term1", "Long Term"),
            ("long_term2", "Long Term"),
        ]:
            activity_value = getattr(activity, activity_column)
            if activity_value:
                activities.append({
                    "student_usn": student.student_usn,
                    "student_name": student.student_name,
                    "student_program": student.student_program,
                    "assigned_mentor": mentor_name,
                    "activity": activity_value,
                    "duration_type": duration_type,
                    "generated_at": activity.generated_at
                })

    if not activities:
        raise HTTPException(status_code=404, detail="No activities found for any students")

    return {
        "admin_id": admin_id,
        "activities": activities
    }
