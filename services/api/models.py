from enum import Enum, auto
from services.api.db import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY


class Status(str, Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    INTERVIEWED = "INTERVIEWED"
    OFFER = "OFFER"
    REJECTED = "REJECTED"

    @property
    def is_complete(self):
        return self in (Status.OFFER, Status.REJECTED)


class Term(str, Enum):
    WINTER = "winter"
    SUMMER = "summer"
    FALL = "fall"


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    status = Column(SQLEnum(Status), nullable=False, default=Status.SAVED)
    term = Column(SQLEnum(Term), nullable=True)
    required_skills = Column(ARRAY(String), nullable=False, default=list)
    url = Column(String, unique=True, nullable=True, index=True)
    location = Column(String, nullable=True)
    source = Column(String, nullable=True)