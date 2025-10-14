# Backend Models Package
from .user import UserBase, UserCreate, UserResponse, UserAuth
from .job import JobBase, JobCreate, JobResponse, JobSearchQuery
from .email import EmailBase, EmailCreate, EmailResponse, EmailGenerateRequest, EmailSendRequest
from .resume import ResumeBase, ResumeCreate, ResumeResponse, ResumeUploadResponse

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserAuth",
    "JobBase",
    "JobCreate",
    "JobResponse",
    "JobSearchQuery",
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
