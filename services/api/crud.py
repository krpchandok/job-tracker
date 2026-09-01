from typing import List, Optional
from fastapi import HTTPException, Depends, status, APIRouter, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
import services.api.models as models
import services.api.schemas as schemas
from services.api.db import get_db
import services.api.mock_data as mock_data

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@router.post("/jobs", response_model=schemas.JobRead, status_code=status.HTTP_201_CREATED)
def add_jobs(job: schemas.JobCreate, db: Session = Depends(get_db)):
    # Dedup check: skip if a posting with this URL already exists
    if job.url:
        existing = db.query(models.JobPosting).filter(
            models.JobPosting.url == job.url
        ).first()
        if existing:
            return existing

    data = job.model_dump()
    data["source"] = data.get("source") or "manual"

    new_job = models.JobPosting(**data)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get("/jobs", response_model=List[schemas.JobRead])
def get_all_jobs(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="search in title / company"),
    status: Optional[schemas.Status] = None,
    term: Optional[schemas.Term] = None,
    company: Optional[str] = None,
    source: Optional[str] = None,
):
    query = db.query(models.JobPosting)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.JobPosting.title.ilike(like),
                models.JobPosting.company.ilike(like),
            )
        )
    if status is not None:
        query = query.filter(models.JobPosting.status == status)
    if term is not None:
        query = query.filter(models.JobPosting.term == term)
    if company:
        query = query.filter(models.JobPosting.company.ilike(f"%{company}%"))
    if source:
        query = query.filter(models.JobPosting.source.ilike(f"%{source}%"))

    return query.order_by(models.JobPosting.id.desc()).all()


@router.patch("/jobs/{job_id}", response_model=schemas.JobRead)
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


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()


@router.get("/mock_jobs", response_model=List[schemas.JobBase])
def get_mock_jobs():
    """Return a small set of mock job postings for frontend development.

    This endpoint does not hit the database and is safe to use from a local React app.
    """
    return mock_data.MOCK_JOBS
