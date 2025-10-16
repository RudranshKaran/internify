from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class EmailBase(BaseModel):
    subject: str
    body: str
    recipient_email: EmailStr


class EmailCreate(EmailBase):
    user_id: str
    internship_id: Optional[str] = None


class EmailResponse(EmailBase):
    id: str
    user_id: str
    internship_id: Optional[str] = None
    sent_at: datetime
    status: str = "sent"

    class Config:
        from_attributes = True


class EmailGenerateRequest(BaseModel):
    internship_description: str
    resume_text: str
    internship_title: str
    company_name: str


class EmailSendRequest(BaseModel):
    internship_id: str
    recipient_email: EmailStr
    subject: str
    body: str
