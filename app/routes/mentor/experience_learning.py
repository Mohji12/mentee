from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.mentors import Mentor
from app.db.models.experience_learning import ExperienceLearning
from app.schemas.experience_learning import (
    ExperienceLearningCreate,
    ExperienceLearningUpdate,
    ExperienceLearningResponse,
)
from app.core.dependencies import get_current_mentor
from app.services.s3bucket import s3_client, get_document_url
from datetime import datetime
from typing import List
import traceback

router = APIRouter()


@router.get("/experience-learning", response_model=List[ExperienceLearningResponse])
async def get_experience_learning_entries(
    mentor_id: str,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Get all experience learning entries for a mentor"""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    entries = (
        db.query(ExperienceLearning)
        .filter(ExperienceLearning.mentor_id == mentor_id.strip())
        .order_by(ExperienceLearning.created_at.desc())
        .all()
    )

    result = []
    for entry in entries:
        entry_dict = {
            "id": entry.id,
            "student_usn": entry.student_usn,
            "mentor_id": entry.mentor_id,
            "title": entry.title,
            "detailed_explanation": entry.detailed_explanation,
            "proof_file_path": entry.proof_file_path,
            "proof_url": None,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }

        # Generate proof URL if proof exists
        if entry.proof_file_path:
            try:
                proof_url = get_document_url(entry.proof_file_path)
                entry_dict["proof_url"] = proof_url
            except Exception:
                pass

        result.append(ExperienceLearningResponse(**entry_dict))

    return result


@router.post("/experience-learning", response_model=ExperienceLearningResponse)
async def create_experience_learning_entry(
    mentor_id: str,
    data: ExperienceLearningCreate,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Create a new experience learning entry"""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Validate mentor exists
    mentor = db.query(Mentor).filter(Mentor.mentor_id == mentor_id.strip()).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    # Validate input
    if not data.title or not data.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    if not data.detailed_explanation or not data.detailed_explanation.strip():
        raise HTTPException(status_code=400, detail="Detailed explanation is required")

    # Create new entry
    new_entry = ExperienceLearning(
        mentor_id=mentor_id.strip(),
        title=data.title.strip(),
        detailed_explanation=data.detailed_explanation.strip(),
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return ExperienceLearningResponse(
        id=new_entry.id,
        student_usn=new_entry.student_usn,
        mentor_id=new_entry.mentor_id,
        title=new_entry.title,
        detailed_explanation=new_entry.detailed_explanation,
        proof_file_path=new_entry.proof_file_path,
        proof_url=None,
        created_at=new_entry.created_at,
        updated_at=new_entry.updated_at,
    )


@router.put("/experience-learning/{entry_id}", response_model=ExperienceLearningResponse)
async def update_experience_learning_entry(
    mentor_id: str,
    entry_id: int,
    data: ExperienceLearningUpdate,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Update an experience learning entry"""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get entry and verify ownership
    entry = (
        db.query(ExperienceLearning)
        .filter(
            ExperienceLearning.id == entry_id,
            ExperienceLearning.mentor_id == mentor_id.strip(),
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Experience learning entry not found")

    # Update fields if provided
    if data.title is not None:
        if not data.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        entry.title = data.title.strip()
    if data.detailed_explanation is not None:
        if not data.detailed_explanation.strip():
            raise HTTPException(status_code=400, detail="Detailed explanation cannot be empty")
        entry.detailed_explanation = data.detailed_explanation.strip()

    db.commit()
    db.refresh(entry)

    # Generate proof URL if exists
    proof_url = None
    if entry.proof_file_path:
        try:
            proof_url = get_document_url(entry.proof_file_path)
        except Exception:
            pass

    return ExperienceLearningResponse(
        id=entry.id,
        student_usn=entry.student_usn,
        mentor_id=entry.mentor_id,
        title=entry.title,
        detailed_explanation=entry.detailed_explanation,
        proof_file_path=entry.proof_file_path,
        proof_url=proof_url,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.delete("/experience-learning/{entry_id}")
async def delete_experience_learning_entry(
    mentor_id: str,
    entry_id: int,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Delete an experience learning entry"""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get entry and verify ownership
    entry = (
        db.query(ExperienceLearning)
        .filter(
            ExperienceLearning.id == entry_id,
            ExperienceLearning.mentor_id == mentor_id.strip(),
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Experience learning entry not found")

    # Delete proof file from S3 if exists
    if entry.proof_file_path:
        try:
            s3_client.delete_object(Key=entry.proof_file_path)
        except Exception as e:
            print(f"Warning: Failed to delete proof file from S3: {str(e)}")

    db.delete(entry)
    db.commit()

    return {"message": "Experience learning entry deleted successfully"}


@router.post("/experience-learning/{entry_id}/upload-proof")
async def upload_proof(
    mentor_id: str,
    entry_id: int,
    file: UploadFile = File(...),
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Upload proof file for an experience learning entry"""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        # Validate file size (max 10MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

        # Validate file type
        allowed_extensions = {
            "jpg",
            "jpeg",
            "png",
            "gif",
            "pdf",
            "doc",
            "docx",
            "txt",
            "zip",
        }
        if "." in file.filename:
            file_extension = file.filename.rsplit(".", 1)[-1].lower()
        else:
            file_extension = "bin"

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}",
            )

        # Get entry and verify ownership
        entry = (
            db.query(ExperienceLearning)
            .filter(
                ExperienceLearning.id == entry_id,
                ExperienceLearning.mentor_id == mentor_id.strip(),
            )
            .first()
        )

        if not entry:
            raise HTTPException(status_code=404, detail="Experience learning entry not found")

        # Delete old proof file if exists
        if entry.proof_file_path:
            try:
                s3_client.delete_object(Key=entry.proof_file_path)
            except Exception as e:
                print(f"Warning: Failed to delete old proof file: {str(e)}")

        # Generate storage path
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        s3_file_name = f"experience-learning/mentor/{mentor_id.strip()}/{entry_id}_{timestamp}.{file_extension}"

        try:
            file_url = s3_client.upload_fileobj(
                file.file,
                None,
                s3_file_name,
                ExtraArgs={
                    "ContentType": file.content_type or "application/octet-stream"
                },
            )
        except Exception as upload_error:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload file: {str(upload_error)}"
            )

        try:
            entry.proof_file_path = file_url
            db.commit()
            db.refresh(entry)
        except Exception as db_error:
            try:
                s3_client.delete_object(Key=file_url)
            except:
                pass
            raise HTTPException(
                status_code=500, detail=f"Failed to save proof path to database: {str(db_error)}"
            )

        return {
            "message": "Proof file uploaded successfully",
            "file_key": file_url,
            "proof_url": file_url,
        }

    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Unexpected error in upload_proof: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/experience-learning/{entry_id}/proof")
async def get_proof(
    mentor_id: str,
    entry_id: int,
    current: dict = Depends(get_current_mentor),
    db: Session = Depends(get_db),
):
    """Get proof file URL for an experience learning entry"""
    if current.get("mentor_id") != mentor_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get entry and verify ownership
    entry = (
        db.query(ExperienceLearning)
        .filter(
            ExperienceLearning.id == entry_id,
            ExperienceLearning.mentor_id == mentor_id.strip(),
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Experience learning entry not found")

    if not entry.proof_file_path:
        raise HTTPException(status_code=404, detail="No proof file found for this entry")

    try:
        proof_url = get_document_url(entry.proof_file_path)
        return {"proof_url": proof_url, "entry_id": entry_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
