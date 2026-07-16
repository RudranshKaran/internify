import logging
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from dotenv import load_dotenv

# Configure logging to stdout so platform logs capture everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger("internflow")

# Import routers
from routes import (
    auth_router,
    resume_router,
    internships_router,
    llm_router,
    email_router,
    companies_router,
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="InternFlow API",
    description="Backend API for InternFlow - AI-Powered Internship Application Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
# Allow multiple origins including local development and production.
# Production origins must be supplied via CORS_ORIGINS (comma-separated).
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Get additional origins from environment variable
env_origins = os.getenv("CORS_ORIGINS", "")
if env_origins:
    origins.extend([o.strip() for o in env_origins.split(",") if o.strip()])

# allow_credentials=True requires an explicit origin list - never "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(internships_router)
app.include_router(llm_router)
app.include_router(email_router)
app.include_router(companies_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to InternFlow API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "InternFlow API"
    }


# Error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """HTTPException handler — preserves status code and detail JSON body"""
    logger.warning(f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all for unhandled exceptions"""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    detail = str(exc) if os.getenv("ENVIRONMENT") == "development" else "An unexpected error occurred"
    return JSONResponse(
        status_code=500,
        content={"detail": detail},
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("InternFlow API is starting up...")
    print(f"Documentation available at: /docs")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("InternFlow API is shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
