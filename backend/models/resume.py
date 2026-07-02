from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime


class ResumeBase(BaseModel):
    file_path: str
    extracted_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class ResumeCreate(ResumeBase):
    user_id: str


class ResumeResponse(ResumeBase):
    id: str
    user_id: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ResumeUploadResponse(BaseModel):
    id: str
    file_path: str
    extracted_text: str
    uploaded_at: datetime
    extracted_data: Optional[Dict[str, Any]] = None
