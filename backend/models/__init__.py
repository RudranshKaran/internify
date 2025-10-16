# Backend Models Package
from .user import UserBase, UserCreate, UserResponse, UserAuth
from .internship import InternshipBase, InternshipCreate, InternshipResponse, InternshipSearchQuery
from .email import EmailBase, EmailCreate, EmailResponse, EmailGenerateRequest, EmailSendRequest
from .resume import ResumeBase, ResumeCreate, ResumeResponse, ResumeUploadResponse

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserAuth",
    "InternshipBase",
    "InternshipCreate",
    "InternshipResponse",
    "InternshipSearchQuery",
    "EmailBase",
    "EmailCreate",
    "EmailResponse",
    "EmailGenerateRequest",
    "EmailSendRequest",
    "ResumeBase",
    "ResumeCreate",
    "ResumeResponse",
    "ResumeUploadResponse",
]
