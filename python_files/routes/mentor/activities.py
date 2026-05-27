from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.activities import Activities
from app.db.models.activities_tracking import ActivitiesTracking
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.activity_submissions import ActivitySubmissions
from app.db.models.students import Student
from app.db.database import get_db
from app.schemas.activities import UpdateActivityTrackingSchema, ActivityMSubmissionsSchema, ActivitySubmissionsSchema, ActivityReviewRequest
from app.utils.id_utils import generate_activity_id
from app.services.email_services import send_email
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.get("/activities")
def get_assigned_students_activities(mentor_id: str, db: Session = Depends(get_db)):
    # Fetch the mentor from the database
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()

    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    # Fetch all students assigned to this mentor, including their names
    assigned_students = db.query(Student).filter(Student.assigned_mentor == mentor_id).all()

    if not assigned_students:
        raise HTTPException(status_code=404, detail="No students assigned to this mentor")

    activities = []

    for student in assigned_students:
        # Collect existing tracked activities for the student
        tracked_activities = db.query(ActivitiesTracking).filter(
            ActivitiesTracking.student_usn == student.student_usn
        ).all()

        tracked_activity_values = {activity.activities for activity in tracked_activities}

        # Fetch student activities
        student_activities = db.query(Activities).filter(
            Activities.student_usn == student.student_usn
        ).first()

        if not student_activities:
            continue

        for activity_column, duration_type in [
            ("short_term", "Short Term"),
            ("short_term1", "Short Term"),
            ("short_term2", "Short Term"),
            ("mid_term", "Mid Term"),
            ("mid_term1", "Mid Term"),
            ("mid_term2", "Mid Term"),
            ("long_term", "Long Term"),
            ("long_term1", "Long Term"),
            ("long_term2", "Long Term")
        ]:
            activity_value = getattr(student_activities, activity_column)

            # Skip if the activity is already tracked
            if not activity_value or activity_value in tracked_activity_values:
                # If already tracked, show the existing activity
                existing_activity = next(
                    (activity for activity in tracked_activities if activity.activities == activity_value), None
                )
                if existing_activity:
                    activities.append({
                        "activity_id": existing_activity.id,
                        "student_usn": existing_activity.student_usn,
                        "student_name": student.student_name,  # Add student name here
                        "activities": existing_activity.activities,
                        "duration_type": existing_activity.duration_type,
                        "deadline": existing_activity.deadline,
                        "remarks": existing_activity.remarks,
                        "percentage": existing_activity.percentage,
                        "completed_in": existing_activity.completed_in,
                        "benefitted": existing_activity.benefitted,
                        "proof": existing_activity.proof,
                        "status":existing_activity.status,
                        "start_date": student_activities.generated_at  # 💫 NEW

                    })
                    continue

            # Generate a new activity ID
            activity_id = generate_activity_id()

            # Calculate the deadline based on duration type
            deadline = None
            if duration_type == "Short Term":
                deadline = datetime.utcnow() + timedelta(days=90)
            elif duration_type == "Mid Term":
                deadline = datetime.utcnow() + timedelta(days=182)
            elif duration_type == "Long Term":
                deadline = datetime.utcnow() + timedelta(days=365)

            # Create a new activity tracking entry
            activity_tracking = ActivitiesTracking(
                id=activity_id,
                student_usn=student.student_usn,
                activities=activity_value,
                duration_type=duration_type,
                deadline=deadline,
                remarks=None,
                percentage=None,
                completed_in=None,
                benefitted=None,
                status=None,
                proof=None
            )

            db.add(activity_tracking)

            activities.append({
                "activity_id": activity_id,
                "student_usn": student.student_usn,
                "student_name": student.student_name,  # Add student name here
                "activities": activity_value,
                "duration_type": duration_type,
                "deadline": deadline,
                "remarks": None,
                "completed_in": None,
                "percentage":None,
                "benefitted": None,
                "status":None,
                "proof": None,
                "start_date": student_activities.generated_at  # 💫 NEW

            })

    # Commit the session to save changes to the database
    db.commit()

    # If no activities were created or found, return a 404 error
    if not activities:
        raise HTTPException(status_code=404, detail="No activities available for the students")

    return activities

@router.put("/{activity_id}/update_activity")
def update_activity_tracking(
    mentor_id: str,
    activity_id: str,
    body: UpdateActivityTrackingSchema,
    db: Session = Depends(get_db)
):
    # Fetch the mentor
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")

    # Fetch the activity in activities_tracking table
    activity_tracking = db.query(ActivitiesTracking).filter(ActivitiesTracking.id == activity_id).first()

    if not activity_tracking:
        raise HTTPException(status_code=404, detail=f"No activity found with ID {activity_id}")
    
    # Update the activity details if provided
    if body.remarks is not None:
        activity_tracking.remarks = body.remarks
    if body.completed_in is not None:
        activity_tracking.completed_in = body.completed_in
    if body.benefitted is not None:
        activity_tracking.benefitted = body.benefitted
    if body.proof is not None:
        if not isinstance(body.proof, str) or not body.proof.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid proof link format")
        activity_tracking.proof = body.proof

    # Commit the changes to the database
    db.commit()

    # Fetch the student who this activity is assigned to
    student = db.query(Student).filter(Student.student_usn == activity_tracking.student_usn).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Send an email notification to the student about the updated activity
    subject = "Your Activity has been Updated"
    body_content = f"Dear {student.student_name},\n\nYour activity (ID: {activity_id}) has been updated by your mentor. Please check the system for the latest updates.\n\nBest regards,\nYour Mentor \n{student.assigned_mentor}"
    
    send_email(student.student_email, subject, body_content)
    
    return {
        "message": "Activity updated successfully.",
        "mentor_id": mentor_id,
        "activity_id": activity_id,
        "student_notified": student.student_email
    }

@router.get("/submissions", response_model=List[ActivitySubmissionsSchema])
def get_submissions_by_mentor(mentor_id: str, db: Session = Depends(get_db)):
    submissions = db.query(ActivitySubmissions).filter(ActivitySubmissions.mentor_id == mentor_id).all()
    return submissions  # ← No 404 here

@router.get("/activities/submissions", response_model=List[ActivityMSubmissionsSchema])
async def get_mentor_submissions(mentor_id: str, db: Session = Depends(get_db)):
    submissions = (
        db.query(ActivitySubmissions)
        .join(Student, ActivitySubmissions.student_usn == Student.student_usn)
        .join(ActivitiesTracking, ActivitySubmissions.activity_id == ActivitiesTracking.id)
        .options(joinedload(ActivitySubmissions.student), joinedload(ActivitySubmissions.activity))
        .filter(ActivitySubmissions.mentor_id == mentor_id)
        .all()
    )

    # Just return empty list if no submissions
    return [
        {
            "submission_id": submission.submission_id,
            "activity_id": submission.activity_id,
            "activity_name": submission.activity.activities,
            "student_usn": submission.student_usn,
            "student_name": submission.student.student_name,
            "mentor_id": submission.mentor_id,
            "proof": submission.proof,
            "submitted_at": submission.submitted_at,
            "status": submission.status,
            "rejection_reason": submission.rejection_reason,
            "completed_in": submission.completed_in,
        }
        for submission in submissions
    ]

@router.put("/student/{student_usn}/activities/{activity_id}/review")
async def review_activity(
    mentor_id: str,
    student_usn: str,
    activity_id: str,
    review: ActivityReviewRequest,
    db: Session = Depends(get_db)
):
    # Verify student exists and mentor is assigned
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.assigned_mentor != mentor_id:
        raise HTTPException(status_code=403, detail="Unauthorized: You are not assigned to this student")

    # Get latest submission
    latest_submission = (
        db.query(ActivitySubmissions)
        .filter(
            ActivitySubmissions.student_usn == student_usn,
            ActivitySubmissions.activity_id == activity_id
        )
        .order_by(ActivitySubmissions.submitted_at.desc())
        .first()
    )

    if not latest_submission:
        raise HTTPException(status_code=404, detail="No submission found for this activity")

    if review.status not in ["Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'Approved' or 'Rejected'.")

    latest_submission.status = review.status

    if review.status == "Approved":
        if review.percentage is None or not (0 <= review.percentage <= 100):
            raise HTTPException(status_code=400, detail="Percentage must be between 0 and 100.")

        # Get the generated_at from Activities using student_usn
        activity_generated = (
            db.query(Activities)
            .filter(Activities.student_usn == student_usn)
            .order_by(Activities.generated_at.desc())  # Or whatever field makes it the right one
            .first()
        )

        if not activity_generated or not activity_generated.generated_at:
            raise HTTPException(status_code=404, detail="Generated date not found for student in Activities")

        generated_at = activity_generated.generated_at

        # Fetch all submissions for this activity to recalculate completed_in
        submissions = db.query(ActivitySubmissions).filter(
            ActivitySubmissions.student_usn == student_usn,
            ActivitySubmissions.activity_id == activity_id
        ).all()

        total_completed_days = 0
        for sub in submissions:
            if sub.submitted_at:
                days = (sub.submitted_at - generated_at).days
                sub.completed_in = max(0, days)
                total_completed_days += sub.completed_in or 0

        # Update tracking
        tracking = db.query(ActivitiesTracking).filter(
            ActivitiesTracking.id == activity_id,
            ActivitiesTracking.student_usn == student_usn
        ).first()

        if not tracking:
            raise HTTPException(status_code=404, detail="Activity tracking not found")

        tracking.percentage = review.percentage
        tracking.status = "Completed" if review.percentage == 100 else "In Progress"
        tracking.completed_in = total_completed_days

        latest_submission.percentage = review.percentage
        latest_submission.rejection_reason = None

    else:
        if not review.rejection_reason:
            raise HTTPException(status_code=400, detail="Rejection reason is required.")
        latest_submission.rejection_reason = review.rejection_reason

    db.commit()
    return {"message": f"Activity {review.status.lower()} successfully"}
