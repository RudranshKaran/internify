from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class EmailBase(BaseModel):
    subject: str
    body: str
    recipient_email: EmailStr


class EmailCreate(EmailBase):
    user_id: str
    job_id: Optional[str] = None


class EmailResponse(EmailBase):
    id: str
    user_id: str
    job_id: Optional[str] = None
    sent_at: datetime
    status: str = "sent"

    class Config:
        from_attributes = True


class EmailGenerateRequest(BaseModel):
    job_description: str
    resume_text: str
    job_title: str
    company_name: str


class EmailSendRequest(BaseModel):
    job_id: str
    recipient_email: EmailStr
    subject: str
    body: str
