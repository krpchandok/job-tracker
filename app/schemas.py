from pydantic import BaseModel
from models import Status, Term
from typing import List

class JobBase(BaseModel):
    title: str
    company: str
    status: Status
    term: Term
    required_skills: List[str]

    class Config:
        orm_mode = True

class AddJob(JobBase):
    class Config:
        orm_mode = True
    
