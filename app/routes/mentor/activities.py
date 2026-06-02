from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.activities import Activities
from app.db.models.activities_tracking import ActivitiesTracking
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.db.models.activity_submissions import ActivitySubmissions
from app.db.models.students import Student
from app.db.database import get_db
from app.schemas.activities import UpdateActivityTrackingSchema, ActivityMSubmissionsSchema, ActivitySubmissionsSchema, ActivityReviewRequest, MentorActivityRequest
from app.core.dependencies import get_current_mentor
from app.utils.alumni import active_students_filter
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
    assigned_students = active_students_filter(
        db.query(Student).filter(Student.assigned_mentor == mentor_id)
    ).all()

    if not assigned_students:
        raise HTTPException(status_code=404, detail="No students assigned to this mentor")

    activities = []

    for student in assigned_students:
        # Collect ALL existing tracked activities for the student (including student-requested ones)
        tracked_activities = db.query(ActivitiesTracking).filter(
            ActivitiesTracking.student_usn == student.student_usn
        ).all()

        # First, add all existing tracked activities (including student-requested ones)
        for tracked_activity in tracked_activities:
            # Get start_date from Activities table if available, otherwise use current date
            student_activities = db.query(Activities).filter(
                Activities.student_usn == student.student_usn
            ).first()
            
            start_date = student_activities.generated_at if student_activities else datetime.utcnow()
            
            activities.append({
                "activity_id": tracked_activity.id,
                "student_usn": tracked_activity.student_usn,
                "student_name": student.student_name,
                "activities": tracked_activity.activities,
                "duration_type": tracked_activity.duration_type,
                "deadline": tracked_activity.deadline,
                "remarks": tracked_activity.remarks,
                "percentage": tracked_activity.percentage,
                "completed_in": tracked_activity.completed_in,
                "benefitted": tracked_activity.benefitted,
                "proof": tracked_activity.proof,
                "status": tracked_activity.status,
                "start_date": start_date,
                "requested_by": getattr(tracked_activity, "requested_by", None)
            })

        # Fetch student activities from Activities table (SWOT-generated)
        student_activities = db.query(Activities).filter(
            Activities.student_usn == student.student_usn
        ).first()

        if not student_activities:
            continue

        # Track which duration types already exist in ActivitiesTracking
        existing_duration_types = {activity.duration_type for activity in tracked_activities}

        # Only process activities from Activities table that don't already exist in ActivitiesTracking
        for activity_column, duration_type in [
            ("short_term", "Short Term"),
            ("mid_term", "Mid Term"),
            ("long_term", "Long Term")
        ]:
            # Skip if we already have an activity of this duration type
            if duration_type in existing_duration_types:
                continue

            activity_value = getattr(student_activities, activity_column)

            # Skip if no activity value
            if not activity_value:
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
                status="Pending",
                proof=None
            )

            db.add(activity_tracking)

            activities.append({
                "activity_id": activity_id,
                "student_usn": student.student_usn,
                "student_name": student.student_name,
                "activities": activity_value,
                "duration_type": duration_type,
                "deadline": deadline,
                "requested_by": None,
                "remarks": None,
                "completed_in": None,
                "percentage": None,
                "benefitted": None,
                "status": "Pending",
                "proof": None,
                "start_date": student_activities.generated_at
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
    if body.proof is not None and (isinstance(body.proof, str) and body.proof.strip()):
        if not body.proof.strip().startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid proof link format")
        activity_tracking.proof = body.proof.strip()

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

@router.post("/request-activity")
async def request_activity(
    mentor_id: str,
    request: MentorActivityRequest,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db)
):
    """Mentor can request/create a new activity for an assigned student"""
    # Verify mentor authentication
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Verify mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail=f"No mentor found with ID {mentor_id}")
    
    # Verify student exists and is assigned to this mentor
    student = db.query(Student).filter(Student.student_usn == request.student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student.assigned_mentor != mentor_id:
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized: You are not assigned to this student"
        )
    
    # Validate duration type
    valid_duration_types = ["Short Term", "Mid Term", "Long Term"]
    if request.duration_type not in valid_duration_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid duration_type. Must be one of: {', '.join(valid_duration_types)}"
        )
    
    # Validate activity description
    if not request.activities or not request.activities.strip():
        raise HTTPException(status_code=400, detail="Activity description is required")
    
    # Calculate deadline if not provided
    deadline = request.deadline
    if not deadline:
        if request.duration_type == "Short Term":
            deadline = datetime.utcnow() + timedelta(days=90)
        elif request.duration_type == "Mid Term":
            deadline = datetime.utcnow() + timedelta(days=182)
        elif request.duration_type == "Long Term":
            deadline = datetime.utcnow() + timedelta(days=365)
    
    # Generate a new activity ID
    activity_id = generate_activity_id()
    
    # Create new activity tracking entry (mentor requested)
    new_activity = ActivitiesTracking(
        id=activity_id,
        student_usn=request.student_usn.strip(),
        activities=request.activities.strip(),
        duration_type=request.duration_type,
        deadline=deadline,
        remarks=request.remarks.strip() if request.remarks else None,
        percentage=None,
        completed_in=None,
        benefitted=None,
        status="Pending",
        proof=None,
        requested_by="mentor"
    )
    
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    
    # Send email notification to student
    try:
        subject = "New Activity Assigned by Your Mentor"
        body_content = f"Dear {student.student_name},\n\nYour mentor has assigned you a new activity:\n\n"
        body_content += f"Activity: {request.activities.strip()}\n"
        body_content += f"Duration Type: {request.duration_type}\n"
        body_content += f"Deadline: {deadline.strftime('%Y-%m-%d') if deadline else 'Not specified'}\n"
        if request.remarks:
            body_content += f"\nRemarks: {request.remarks.strip()}\n"
        body_content += f"\nPlease log in to your dashboard to view and submit this activity.\n\n"
        body_content += f"Best regards,\nYour Mentor"
        
        send_email(student.student_email, subject, body_content)
    except Exception as e:
        print(f"Warning: Failed to send email notification: {str(e)}")
        # Don't fail the request if email fails
    
    return {
        "message": "Activity requested successfully",
        "activity_id": activity_id,
        "student_usn": request.student_usn,
        "student_name": student.student_name,
        "activities": request.activities.strip(),
        "duration_type": request.duration_type,
        "deadline": deadline,
        "status": "Pending",
        "email_sent": True
    }
