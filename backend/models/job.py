from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class JobBase(BaseModel):
    title: str
    company: str
    link: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    posted_at: Optional[datetime] = None


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobSearchQuery(BaseModel):
    role: str
    location: Optional[str] = None
    limit: int = 10
