from pydantic import BaseModel
from services.api.models import Status, Term
from typing import List, Optional


class JobBase(BaseModel):
    title: str
    company: str
    status: Status
    term: Term
    required_skills: List[str]
    url: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None

    class Config:
        orm_mode = True


class AddJob(JobBase):
    class Config:
        orm_mode = True


class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    status: Status | None = None
    term: Term | None = None
    required_skills: List[str] | None = None
    url: str | None = None
    location: str | None = None
    source: str | None = None

    class Config:
        orm_mode = True
