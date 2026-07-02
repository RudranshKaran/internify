from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


EmailStatus = Literal["not_found", "found", "verified"]


class DiscoveredCompanyBase(BaseModel):
    company_name: str
    domain: Optional[str] = None
    role_title: str
    location: Optional[str] = None
    job_description_snippet: Optional[str] = None
    source_url: Optional[str] = None
    source_query: Optional[str] = None


class DiscoveredCompanyCreate(DiscoveredCompanyBase):
    user_id: str
    email_status: EmailStatus = "not_found"


class DiscoveredCompanyUpdate(BaseModel):
    email_status: Optional[EmailStatus] = None
    domain: Optional[str] = None
    job_description_snippet: Optional[str] = None
    source_query: Optional[str] = None


class DiscoveredCompanyResponse(DiscoveredCompanyBase):
    id: str
    user_id: str
    email_status: EmailStatus
    discovered_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True
