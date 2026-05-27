from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from typing import List
from app.db.models.activities_tracking import ActivitiesTracking
from app.db.models.activity_submissions import ActivitySubmissions
from app.db.models.students import Student
from app.db.models.swot import SWOT
from app.db.models.activities import Activities
from app.schemas.activities import ActivitySubmissionsSchema, ActivityTrackingSchema
from app.services.s3bucket import s3_client, S3_BUCKET_NAME, S3_EXPIRATION
from app.utils.analysis import parse_activities
from datetime import datetime


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
        # Generate a presigned URL valid for 7 days
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": submission.proof},
            ExpiresIn=S3_EXPIRATION
        )

        return {
            "proof_url": presigned_url, 
            "submission_id": submission.submission_id,
            "status": submission.status  # Include status info in response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/submissions", response_model=List[ActivitySubmissionsSchema])
async def get_student_submissions(student_usn: str, db: Session = Depends(get_db)):
    submissions = db.query(ActivitySubmissions).filter(ActivitySubmissions.student_usn == student_usn).all()
    
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found for this student")

    return submissions

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
        # Activities already exist, return them
        return {
            "student_usn": activities.student_usn,
            "short_term": activities.short_term,
            "short_term1": activities.short_term1,
            "short_term2": activities.short_term2,
            "mid_term": activities.mid_term,
            "mid_term1": activities.mid_term1,
            "mid_term2": activities.mid_term2,
            "long_term": activities.long_term,
            "long_term1": activities.long_term1,
            "long_term2": activities.long_term2,
        }

    # Fetch SWOT analysis for the student
    swot = db.query(SWOT).filter(SWOT.student_usn == student_usn).first()
    if not swot:
        return {"message": f"No SWOT analysis or activities found for student USN {student_usn}"}

    # Parse activities from the SWOT analysis
    activities_data = parse_activities(swot.swot_analysis)

    # Create and save new activities
    new_activities = Activities(
        student_usn=student_usn,
        short_term=activities_data["short_term"][0],
        short_term1=activities_data["short_term"][1],
        short_term2=activities_data["short_term"][2],
        mid_term=activities_data["mid_term"][0],
        mid_term1=activities_data["mid_term"][1],
        mid_term2=activities_data["mid_term"][2],
        long_term=activities_data["long_term"][0],
        long_term1=activities_data["long_term"][1],
        long_term2=activities_data["long_term"][2],
    )
    db.add(new_activities)
    db.commit()

    return {
        "student_usn": student_usn,
        "short_term": activities_data["short_term"][0],
        "short_term1": activities_data["short_term"][1],
        "short_term2": activities_data["short_term"][2],
        "mid_term": activities_data["mid_term"][0],
        "mid_term1": activities_data["mid_term"][1],
        "mid_term2": activities_data["mid_term"][2],
        "long_term": activities_data["long_term"][0],
        "long_term1": activities_data["long_term"][1],
        "long_term2": activities_data["long_term"][2],
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
        # Generate a unique submission ID
        submission_id = f"SUB{datetime.now().strftime('%Y%m%d%H%M%S')}"
        file_extension = file.filename.split(".")[-1]
        s3_file_name = f"proofs/{student_usn}_{activity_id}_{submission_id}.{file_extension}"

        # Upload file to S3 (No Public Access)
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            s3_file_name,
            ExtraArgs={"ContentType": file.content_type}
        )

        # Validate activity
        activity = db.query(ActivitiesTracking).filter(ActivitiesTracking.id == activity_id).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Validate student
        student = db.query(Student).filter(Student.student_usn == student_usn).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Insert into `activity_submissions`
        new_submission = ActivitySubmissions(
            submission_id=submission_id,
            activity_id=activity_id,
            student_usn=student_usn,
            mentor_id=student.assigned_mentor,  # Fetch from Students table
            proof=s3_file_name,
            status="Pending"
        )
        db.add(new_submission)
        db.commit()

        return {"message": "File uploaded successfully", "file_key": s3_file_name, "submission_id": submission_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
