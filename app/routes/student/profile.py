from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.db.models.students import Student
from app.db.models.mentors import Mentor
from app.schemas.students import StudentProfileSchema, StudentEditSchema
from app.services.cloudinary_service import upload_fileobj, delete_document
from datetime import datetime, timezone

ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/jpg", "image/png"}
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB

router = APIRouter()

@router.post("/createprofile")
def create_student_profile(student_usn: str, data: StudentProfileSchema, db: Session = Depends(get_db)):
    """
    Endpoint to create or update a student profile with calculated semester.
    All fields are required: name, program, batch, phone number, assigned_mentor, linkedin.
    """
    # Check if the student exists in the database
    student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

    # Ensure the student's profile is not already complete
    if student.student_name and student.student_program and student.student_batch:
        raise HTTPException(status_code=400, detail=f"Student with USN {student_usn} already has a profile")

    # Validate all required fields are provided and not empty
    if not data.student_name or not data.student_name.strip():
        raise HTTPException(status_code=400, detail="Student name is required and cannot be empty.")
    
    if not data.student_program or not data.student_program.strip():
        raise HTTPException(status_code=400, detail="Student program is required and cannot be empty.")
    
    if not data.student_batch or not data.student_batch.strip():
        raise HTTPException(status_code=400, detail="Student batch is required and cannot be empty.")
    
    if not data.student_phoneno or not data.student_phoneno.strip():
        raise HTTPException(status_code=400, detail="Phone number is required and cannot be empty.")
    
    if not data.mother_contact or not data.mother_contact.strip():
        raise HTTPException(status_code=400, detail="Mother contact is required and cannot be empty.")

    if not data.father_contact or not data.father_contact.strip():
        raise HTTPException(status_code=400, detail="Father contact is required and cannot be empty.")

    if not data.assigned_mentor or not data.assigned_mentor.strip():
        raise HTTPException(status_code=400, detail="Assigned mentor is required and cannot be empty.")
    
    if not data.linkedin or not data.linkedin.strip() or data.linkedin == 'https://linkedin.com/in/':
        raise HTTPException(status_code=400, detail="LinkedIn profile is required and cannot be empty.")

    # Calculate semester based on batch start year
    try:
        start_year = int(data.student_batch.split('-')[0])  # Extract batch start year
        current_date = datetime.now(tz=timezone.utc)  # Updated UTC time
        months_since_batch_start = (current_date.year - start_year) * 12 + current_date.month - 7  # July is assumed as start month
        semester = (months_since_batch_start // 6) + 1
        if semester > 8:
            semester = 8  # Cap the semester at 8
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid batch format. Expected format: 'YYYY-YYYY'.")

    # Validate phone number format
    if len(data.student_phoneno) != 10 or not data.student_phoneno.isdigit():
        raise HTTPException(status_code=400, detail="Invalid phone number. Must be a 10-digit numeric value.")

    mc = data.mother_contact.strip()
    if len(mc) != 10 or not mc.isdigit():
        raise HTTPException(status_code=400, detail="Mother contact must be a 10-digit numeric value.")

    fc = data.father_contact.strip()
    if len(fc) != 10 or not fc.isdigit():
        raise HTTPException(status_code=400, detail="Father contact must be a 10-digit numeric value.")

    # Verify mentor exists
    mentor = db.query(Mentor).filter_by(mentor_id=data.assigned_mentor).first()
    if not mentor:
        raise HTTPException(status_code=400, detail=f"Mentor with ID '{data.assigned_mentor}' not found.")

    # Update the student's profile
    student.student_name = data.student_name.strip()
    student.student_program = data.student_program.strip()
    student.student_batch = data.student_batch.strip()
    student.student_phoneno = data.student_phoneno.strip()
    student.semester = semester
    student.assigned_mentor = data.assigned_mentor.strip()
    student.linkedin = data.linkedin.strip()
    student.gender = data.gender.strip() if data.gender else None
    student.blood_group = data.blood_group.strip() if data.blood_group else None
    student.date_of_birth = data.date_of_birth
    student.parent_guardian_contact = data.parent_guardian_contact.strip() if data.parent_guardian_contact else None
    student.mother_contact = mc
    student.father_contact = fc

    # Commit changes to the database
    db.commit()

    return {"message": f"Profile updated successfully for Student USN {student_usn}"}

@router.get("/myprofile")
def get_student_profile(student_usn: str, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a student's profile by their USN.
    Includes mentor details if assigned.
    """
    # Fetch student details
    student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

    # Fetch mentor details
    mentor_name = "No Mentor Assigned"
    if student.assigned_mentor:
        mentor = db.query(Mentor).filter_by(mentor_id=student.assigned_mentor).first()
        if mentor:
            mentor_name = mentor.mentor_name

    # Construct and return the response
    return {
        "student_usn": student.student_usn,
        "student_name": student.student_name,
        "student_email": student.student_email,
        "student_phoneno": student.student_phoneno,
        "student_program": student.student_program,
        "student_batch": student.student_batch,
        "semester": student.semester,
        "assigned_mentor": mentor_name,
        "linkedin": student.linkedin,
        "gender": student.gender,
        "blood_group": student.blood_group,
        "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None,
        "parent_guardian_contact": student.parent_guardian_contact,
        "mother_contact": student.mother_contact,
        "father_contact": student.father_contact,
        "profile_photo_url": student.profile_photo_url,
    }

@router.put("/editprofile")
def edit_student_profile(student_usn: str, data: StudentEditSchema, db: Session = Depends(get_db)):
    """
    Endpoint to edit a student's profile.
    Fields allowed for update: name, phone, semester, gender, blood_group, date_of_birth, parent_guardian_contact, linkedin.
    """
    student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

    if data.student_name is not None:
        student.student_name = data.student_name.strip() if data.student_name else None
    if data.student_phoneno is not None:
        phoneno = data.student_phoneno.strip() if data.student_phoneno else None
        if phoneno and (len(phoneno) != 10 or not phoneno.isdigit()):
            raise HTTPException(status_code=400, detail="Invalid phone number. Must be a 10-digit numeric value.")
        student.student_phoneno = phoneno
    if data.semester is not None:
        if data.semester < 1 or data.semester > 8:
            raise HTTPException(status_code=400, detail="Semester must be between 1 and 8.")
        student.semester = data.semester
    if data.gender is not None:
        student.gender = data.gender.strip() if data.gender else None
    if data.blood_group is not None:
        student.blood_group = data.blood_group.strip() if data.blood_group else None
    if data.date_of_birth is not None:
        student.date_of_birth = data.date_of_birth
    if data.parent_guardian_contact is not None:
        pgc = data.parent_guardian_contact.strip() if data.parent_guardian_contact else None
        if pgc and (len(pgc) != 10 or not pgc.isdigit()):
            raise HTTPException(status_code=400, detail="Guardian contact must be a 10-digit numeric value.")
        student.parent_guardian_contact = pgc
    if data.mother_contact is not None:
        mc = data.mother_contact.strip() if data.mother_contact else None
        if mc and (len(mc) != 10 or not mc.isdigit()):
            raise HTTPException(status_code=400, detail="Mother contact must be a 10-digit numeric value.")
        student.mother_contact = mc
    if data.father_contact is not None:
        fc = data.father_contact.strip() if data.father_contact else None
        if fc and (len(fc) != 10 or not fc.isdigit()):
            raise HTTPException(status_code=400, detail="Father contact must be a 10-digit numeric value.")
        student.father_contact = fc
    if data.linkedin is not None:
        student.linkedin = data.linkedin.strip() if data.linkedin else None

    db.commit()
    return {"message": f"Profile updated successfully for Student USN {student_usn}"}


@router.post("/uploadphoto")
async def upload_profile_photo(student_usn: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload or update the student's profile photo.
    Accepts JPG, JPEG, PNG. Max size 5 MB.
    If a photo already exists, the old one is deleted from Cloudinary before uploading the new one.
    """
    student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

    if file.content_type not in ALLOWED_PHOTO_TYPES:
        raise HTTPException(status_code=400, detail="Invalid image format. Only JPG, JPEG, and PNG are allowed.")

    contents = await file.read()
    if len(contents) > MAX_PHOTO_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5 MB limit.")

    # Duplicate check: compute simple hash and compare with existing photo
    import hashlib
    new_hash = hashlib.md5(contents).hexdigest()
    if student.profile_photo_url:
        # Store hash in a predictable way — check if the same hash exists in the URL path
        if f"/{new_hash}" in student.profile_photo_url:
            raise HTTPException(status_code=400, detail="This photo is already uploaded.")

    # Delete old photo from Cloudinary if exists
    if student.profile_photo_url:
        delete_document(student.profile_photo_url)

    import io
    key = f"profile_photos/{student_usn}/{new_hash}"
    photo_url = upload_fileobj(
        io.BytesIO(contents),
        None,
        key,
        ExtraArgs={"ContentType": file.content_type},
    )

    student.profile_photo_url = photo_url
    db.commit()

    return {"message": "Profile photo uploaded successfully", "profile_photo_url": photo_url}


@router.delete("/deletephoto")
def delete_profile_photo(student_usn: str, db: Session = Depends(get_db)):
    """Delete the student's profile photo."""
    student = db.query(Student).filter_by(student_usn=student_usn.strip()).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN {student_usn} not found")

    if not student.profile_photo_url:
        raise HTTPException(status_code=400, detail="No profile photo to delete.")

    delete_document(student.profile_photo_url)
    student.profile_photo_url = None
    db.commit()

    return {"message": "Profile photo deleted successfully"}
