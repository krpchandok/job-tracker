from typing import List
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
import models
import schemas
from fastapi import APIRouter
from db import get_db

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

@router.post("/jobs", response_model=List[schemas.AddJob])
def add_jobs(job: schemas.JobBase, db: Session = Depends(get_db)):
    new_job = models.JobPosting(**job.dict())
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return [new_job]

@router.get("/jobs", response_model=List[schemas.JobBase])
def get_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.JobPosting).all()

    return jobs

@router.patch("/jobs/{job_id}", response_model=JobBase)
def update_job(job_id: int, updated_job: )
