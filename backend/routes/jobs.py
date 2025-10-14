from fastapi import APIRouter, Depends, HTTPException, status, Query
from routes.utils import verify_token
from services.scraper_service import scraper_service
from services.supabase_service import supabase_service
from models.job import JobResponse
from typing import Optional, List

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/search")
async def search_jobs(
    role: str = Query(..., description="Job role or title to search for"),
    location: Optional[str] = Query(None, description="Location filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    payload: dict = Depends(verify_token)
):
    """
    Search for job listings using SerpAPI
    
    Args:
        role: Job title or role (e.g., "Software Engineer Intern")
        location: Optional location filter
        limit: Maximum number of results (1-50)
    
    Returns:
        List of job listings from LinkedIn/Google Jobs
    """
    
    try:
        # Search for jobs
        jobs = await scraper_service.search_linkedin_jobs(
            query=role,
            location=location,
            limit=limit
        )
        
        if not jobs:
            return {
                "success": True,
                "jobs": [],
                "message": "No jobs found matching your criteria. Try different keywords."
            }
        
        # Save jobs to database for future reference
        saved_jobs = []
        for job in jobs:
            try:
                saved_job = await supabase_service.save_job({
                    "title": job["title"],
                    "company": job["company"],
                    "link": job["link"],
                    "description": job["description"],
                    "location": job.get("location")
                })
                
                if saved_job:
                    saved_jobs.append(saved_job)
                else:
                    # If saving fails, still include in results
                    saved_jobs.append(job)
            except:
                # Continue even if one job fails to save
                saved_jobs.append(job)
        
        return {
            "success": True,
            "jobs": saved_jobs,
            "count": len(saved_jobs)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job search failed: {str(e)}"
        )


@router.get("/{job_id}")
async def get_job_details(
    job_id: str,
    payload: dict = Depends(verify_token)
):
    """
    Get detailed information about a specific job
    
    Args:
        job_id: Job ID from database
    
    Returns:
        Job details
    """
    
    try:
        job = await supabase_service.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return {
            "success": True,
            "job": job
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch job: {str(e)}"
        )


@router.get("/company/{company_name}")
async def search_jobs_by_company(
    company_name: str,
    role: Optional[str] = Query(None, description="Specific role at the company"),
    payload: dict = Depends(verify_token)
):
    """
    Search for jobs at a specific company
    
    Args:
        company_name: Name of the company
        role: Optional specific role filter
    
    Returns:
        List of jobs at the company
    """
    
    try:
        jobs = await scraper_service.search_by_company(
            company_name=company_name,
            role=role
        )
        
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Company job search failed: {str(e)}"
        )
