# Backend Routes Package
from .auth import router as auth_router
from .resume import router as resume_router
from .internships import router as internships_router
from .llm import router as llm_router
from .email import router as email_router

__all__ = [
    "auth_router",
    "resume_router",
    "internships_router",
    "llm_router",
    "email_router",
]
