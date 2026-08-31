from typing import List
from fastapi import HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
import services.api.models as models
import services.api.schemas as schemas
from services.api.db import get_db

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

@router.post("/jobs", response_model=schemas.AddJob)
def add_jobs(job: schemas.JobBase, db: Session = Depends(get_db)):
    # Dedup check: skip if a posting with this URL already exists
    if job.url:
        existing = db.query(models.JobPosting).filter(
            models.JobPosting.url == job.url
        ).first()
        if existing:
            return existing

    new_job = models.JobPosting(**job.model_dump())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job

@router.get("/jobs", response_model=List[schemas.JobBase])
def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.JobPosting).all()
    return jobs

@router.patch("/jobs/{job_id}", response_model=schemas.JobBase)
def update_job(job_id: int, updated_job: schemas.JobUpdate, db: Session = Depends(get_db)):
    original_job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not original_job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = updated_job.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "required_skills":
            # append rather than overwrite the skills list
            current_skills = getattr(original_job, "required_skills") or []
            setattr(original_job, key, current_skills + value)
        else:
            setattr(original_job, key, value)

    db.commit()
    db.refresh(original_job)
    return original_job