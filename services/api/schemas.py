from pydantic import BaseModel, ConfigDict
from services.api.models import Status, Term
from typing import List, Optional


class JobBase(BaseModel):
    title: str
    company: str
    status: Status
    term: Optional[Term] = None
    required_skills: List[str] = []
    url: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobCreate(BaseModel):
    """Payload for manually adding a posting. Only title + company are required."""

    title: str
    company: str
    status: Status = Status.SAVED
    term: Optional[Term] = None
    required_skills: List[str] = []
    url: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobRead(JobBase):
    id: int


class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    status: Status | None = None
    term: Term | None = None
    required_skills: List[str] | None = None
    url: str | None = None
    location: str | None = None
    source: str | None = None

    model_config = ConfigDict(from_attributes=True)
