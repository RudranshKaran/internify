from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class InternshipBase(BaseModel):
    title: str
    company: str
    link: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    posted_at: Optional[datetime] = None


class InternshipCreate(InternshipBase):
    pass


class InternshipResponse(InternshipBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class InternshipSearchQuery(BaseModel):
    role: str
    location: Optional[str] = None
    limit: int = 10
