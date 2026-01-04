from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Import routers
from routes import (
    auth_router,
    resume_router,
    internships_router,
    llm_router,
    email_router
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Internify API",
    description="Backend API for Internify - AI-Powered Internship Application Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
# Allow multiple origins including local development and production
origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://*.vercel.app",
    "https://internify.vercel.app",
    "https://internify-*.vercel.app",
]

# Get additional origins from environment variable
env_origins = os.getenv("CORS_ORIGINS", "")
if env_origins:
    origins.extend(env_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(internships_router)
app.include_router(llm_router)
app.include_router(email_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Internify API",
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
        "service": "Internify API"
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("ENVIRONMENT") == "development" else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 Internify API is starting up...")
    print(f"📝 Documentation available at: /docs")
    print(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'development')}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 Internify API is shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
