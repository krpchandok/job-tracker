from enum import Enum, auto, unique
from db import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum

class Status(Enum):
    SAVED = auto()
    APPLIED = auto()
    INTERVIEWED = auto()
    OFFER = auto()
    REJECTED = auto()

    @property
    def is_complete(self):
        return self in (Status.OFFER, Status.REJECTED)

class Term(Enum):
    WINTER = "winter"
    SUMMER = "summer"
    FALL = "fall"

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    status = Column(Status, nullable=False, default=Status.SAVED)
    term = Column(Term, nullable=False)
    required_skills = Column(str[], nullable=False)
