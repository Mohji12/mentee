from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List
from app.db.models.activities_tracking import ActivitiesTracking
from app.db.models.activity_submissions import ActivitySubmissions
from app.db.models.students import Student
from app.db.models.swot import SWOT
from app.db.models.activities import Activities
from app.schemas.activities import ActivitySubmissionsSchema, ActivityTrackingSchema, StudentActivityRequest
from app.services.s3bucket import s3_client, get_document_url
from app.services.email_services import send_email
from app.utils.analysis import parse_activities
from app.utils.id_utils import generate_activity_id
from app.core.dependencies import get_current_student
from app.db.models.mentors import Mentor
from datetime import datetime, timedelta
import traceback


router = APIRouter()

@router.get("/logged_activities", response_model=dict)
async def get_student_activities(student_usn: str, db: Session = Depends(get_db)):
    activities = db.query(ActivitiesTracking).filter(ActivitiesTracking.student_usn == student_usn).all()

    # Prepare the activity list, even if it's empty
    activity_list = [
        ActivityTrackingSchema(
            activity_id=activity.id,
            activities=activity.activities,
            duration_type=activity.duration_type,
            deadline=activity.deadline,
            remarks=activity.remarks,
            completed_in=activity.completed_in,
            benefitted=activity.benefitted,
            percentage=activity.percentage,
            proof=activity.proof
        ).model_dump()  # Use model_dump() instead of .dict()
        for activity in activities
    ]

    # Always return the response with an empty or populated list
    return {"student_usn": student_usn, "activities": activity_list}

@router.get("/activities/{activity_id}/proof")
async def get_proof(student_usn: str, activity_id: str, db: Session = Depends(get_db)):
    # Get latest submission for the given student & activity (no status filter)
    submission = (
        db.query(ActivitySubmissions)
        .filter(ActivitySubmissions.student_usn == student_usn, 
                ActivitySubmissions.activity_id == activity_id)
        .order_by(ActivitySubmissions.submitted_at.desc())  # Get the latest submission
        .first()
    )

    if not submission or not submission.proof:
        raise HTTPException(status_code=404, detail="No proof found")

    try:
        # Return public S3 URL (file is public via bucket policy)
        public_url = get_document_url(submission.proof)
        return {
            "proof_url": public_url, 
            "submission_id": submission.submission_id,
            "status": submission.status  # Include status info in response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/submissions")
async def get_student_submissions(student_usn: str, db: Session = Depends(get_db)):
    submissions = (
        db.query(ActivitySubmissions, ActivitiesTracking.activities)
        .outerjoin(ActivitiesTracking, ActivitySubmissions.activity_id == ActivitiesTracking.id)
        .filter(ActivitySubmissions.student_usn == student_usn)
        .order_by(ActivitySubmissions.submitted_at.desc())
        .all()
    )
    out = []
    for sub, activity_name in submissions:
        out.append({
            "submission_id": sub.submission_id,
            "activity_id": sub.activity_id,
            "activity_name": activity_name or sub.activity_id,
            "student_usn": sub.student_usn,
            "mentor_id": sub.mentor_id,
            "proof": sub.proof,
            "submitted_at": sub.submitted_at,
            "status": sub.status,
            "rejection_reason": sub.rejection_reason,
            "percentage": sub.percentage,
            "completed_in": sub.completed_in,
        })
    return out

@router.get("/progress")
async def get_student_progress(student_usn: str, db: Session = Depends(get_db)):
    # Fetch all activities for the student
    activities = db.query(ActivitiesTracking).filter(ActivitiesTracking.student_usn == student_usn).all()

    if not activities:
        raise HTTPException(status_code=404, detail="No activities found for this student")

    # Extract the percentage of each activity
    total_percentage = sum(activity.percentage for activity in activities if activity.percentage is not None)
    total_activities = len(activities)

    if total_activities == 0:
        return {"student_usn": student_usn, "progress": 0, "rank": "Rookie Ranger"}

    # Normalize to 100
    normalized_progress = round(total_percentage / total_activities)

    # Assign rank based on progress
    if normalized_progress == 0:
        rank = "A Dormant Dreamer"
    elif 0 < normalized_progress <= 15:
        rank = "An Awakening Seeker"
    elif 16 <= normalized_progress <= 30:
        rank = "An Emerging Learner"
    elif 31 <= normalized_progress <= 50:
        rank = "An Empowered Doer"
    elif 51 <= normalized_progress <= 70:
        rank = "A Resilient Achiever"
    elif 71 <= normalized_progress <= 85:
        rank = "A Purposeful Visionary"
    elif 86 <= normalized_progress <= 99:
        rank = "An Enlightened Trailblazer"
    else:
        rank = "A Transcendent Luminary"

    return {"student_usn": student_usn, "progress": normalized_progress, "rank": rank}

@router.get("/activities")
def get_or_create_activities(student_usn: str, db: Session = Depends(get_db)):
    # Fetch the student's semester
    student = db.query(Student).filter(Student.student_usn == student_usn).first()
    if not student:
        return {"message": f"No student found with USN {student_usn}"}

    # Check if activities for this semester already exist for the student
    activities = db.query(Activities).filter(Activities.student_usn == student_usn).first()

    if activities:
        # Activities already exist, return only the first activity of each type
        return {
            "student_usn": activities.student_usn,
            "short_term": activities.short_term,
            "mid_term": activities.mid_term,
            "long_term": activities.long_term,
        }

    # Fetch SWOT analysis for the student
    swot = db.query(SWOT).filter(SWOT.student_usn == student_usn).first()
    if not swot:
        return {"message": f"No SWOT analysis or activities found for student USN {student_usn}"}

    # Parse activities from the SWOT analysis
    activities_data = parse_activities(swot.swot_analysis)

    # Create and save new activities - only use the first activity of each type
    new_activities = Activities(
        student_usn=student_usn,
        short_term=activities_data["short_term"][0],
        short_term1=None,
        short_term2=None,
        mid_term=activities_data["mid_term"][0],
        mid_term1=None,
        mid_term2=None,
        long_term=activities_data["long_term"][0],
        long_term1=None,
        long_term2=None,
    )
    db.add(new_activities)
    db.commit()

    return {
        "student_usn": student_usn,
        "short_term": activities_data["short_term"][0],
        "mid_term": activities_data["mid_term"][0],
        "long_term": activities_data["long_term"][0],
    }

# ✅ Upload proof to S3 and store in `activity_submissions`
@router.post("/activities/{activity_id}/upload_proof")
async def upload_proof(
    student_usn: str,
    activity_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Generate a unique submission ID
        submission_id = f"SUB{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Handle file extension safely
        if "." in file.filename:
            file_extension = file.filename.rsplit(".", 1)[-1].lower()
        else:
            file_extension = "bin"
        
        s3_file_name = f"proofs/{student_usn}_{activity_id}_{submission_id}.{file_extension}"

        # Validate activity
        activity = db.query(ActivitiesTracking).filter(ActivitiesTracking.id == activity_id).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Validate student
        student = db.query(Student).filter(Student.student_usn == student_usn).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Upload file to Cloudinary
        try:
            file_url = s3_client.upload_fileobj(
                file.file,
                None,
                s3_file_name,
                ExtraArgs={
                    "ContentType": file.content_type or "application/octet-stream"
                }
            )
        except Exception as upload_error:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(upload_error)}")

        # Insert into `activity_submissions`
        try:
            new_submission = ActivitySubmissions(
                submission_id=submission_id,
                activity_id=activity_id,
                student_usn=student_usn,
                mentor_id=student.assigned_mentor,  # Fetch from Students table
                proof=file_url,
                status="Pending"
            )
            db.add(new_submission)
            db.commit()
        except Exception as db_error:
            # If database operation fails, try to delete the uploaded file from S3
            try:
                s3_client.delete_object(Key=file_url)
            except:
                pass
            raise HTTPException(status_code=500, detail=f"Failed to save submission to database: {str(db_error)}")

        return {"message": "File uploaded successfully", "file_key": file_url, "submission_id": submission_id,
                "public_url": file_url}

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Unexpected error in upload_proof: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/request-activity")
async def request_activity(
    student_usn: str,
    request: StudentActivityRequest,
    current: dict = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Student can request/create a new activity that will be visible to their mentor"""
    # Verify student authentication
    if current.get("student_usn") != student_usn:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Verify student exists
    student = db.query(Student).filter(Student.student_usn == student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"No student found with USN {student_usn}")
    
    # Check if student has an assigned mentor
    if not student.assigned_mentor:
        raise HTTPException(
            status_code=400,
            detail="You don't have an assigned mentor. Please contact your administrator."
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
    
    # Create new activity tracking entry (mentee requested)
    new_activity = ActivitiesTracking(
        id=activity_id,
        student_usn=student_usn.strip(),
        activities=request.activities.strip(),
        duration_type=request.duration_type,
        deadline=deadline,
        remarks=request.remarks.strip() if request.remarks else None,
        percentage=None,
        completed_in=None,
        benefitted=None,
        status="Pending",
        proof=None,
        requested_by="mentee"
    )
    
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    
    # Send email notification to mentor
    try:
        mentor = db.query(Mentor).filter(Mentor.mentor_id == student.assigned_mentor).first()
        if mentor and mentor.mentor_email:
            subject = "New Activity Requested by Your Mentee"
            body_content = f"Dear {mentor.mentor_name},\n\n"
            body_content += f"Your mentee {student.student_name} ({student_usn}) has requested a new activity:\n\n"
            body_content += f"Activity: {request.activities.strip()}\n"
            body_content += f"Duration Type: {request.duration_type}\n"
            body_content += f"Deadline: {deadline.strftime('%Y-%m-%d') if deadline else 'Not specified'}\n"
            if request.remarks:
                body_content += f"\nStudent's Notes: {request.remarks.strip()}\n"
            body_content += f"\nPlease log in to your dashboard to review and approve this activity.\n\n"
            body_content += f"Best regards,\nMentee Tracker System"
            
            send_email(mentor.mentor_email, subject, body_content)
    except Exception as e:
        print(f"Warning: Failed to send email notification to mentor: {str(e)}")
        # Don't fail the request if email fails
    
    return {
        "message": "Activity requested successfully. Your mentor will be notified.",
        "activity_id": activity_id,
        "student_usn": student_usn,
        "activities": request.activities.strip(),
        "duration_type": request.duration_type,
        "deadline": deadline,
        "status": "Pending",
        "email_sent": True
    }
