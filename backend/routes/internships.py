from fastapi import APIRouter, Depends, HTTPException, status, Query
from routes.utils import verify_token
from services.scraper_service import scraper_service
from services.supabase_service import supabase_service
from models.internship import InternshipResponse
from typing import Optional, List

router = APIRouter(prefix="/internships", tags=["Internships"])


@router.get("/search")
async def search_internships(
    role: str = Query(..., description="Internship role or title to search for"),
    location: Optional[str] = Query(None, description="Location filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    payload: dict = Depends(verify_token)
):
    """
    Search for internship listings using SerpAPI
    
    Args:
        role: Internship title or role (e.g., "Software Engineer Intern")
        location: Optional location filter
        limit: Maximum number of results (1-50)
    
    Returns:
        List of internship listings from LinkedIn/Google Jobs
    """
    
    try:
        # Search for internships
        internships = await scraper_service.search_internships(
            query=role,
            location=location,
            limit=limit
        )
        
        if not internships:
            return {
                "success": True,
                "internships": [],
                "message": "No internships found matching your criteria. Try different keywords."
            }
        
        # Save internships to database for future reference
        saved_internships = []
        for internship in internships:
            try:
                # Prepare internship data with new contact fields
                internship_data = {
                    "title": internship["title"],
                    "company": internship["company"],
                    "link": internship["link"],
                    "description": internship["description"],
                    "location": internship.get("location"),
                    "contact_email": internship.get("contact_email"),
                    "contact_phone": internship.get("contact_phone"),
                    "contact_website": internship.get("contact_website")
                }
                
                saved_internship = await supabase_service.save_internship(internship_data)
                
                if saved_internship:
                    saved_internships.append(saved_internship)
                else:
                    # If saving fails, still include in results
                    saved_internships.append(internship)
            except Exception as e:
                # Continue even if one internship fails to save
                print(f"Failed to save internship '{internship.get('title')}': {e}")
                saved_internships.append(internship)
        
        return {
            "success": True,
            "internships": saved_internships,
            "count": len(saved_internships)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internship search failed: {str(e)}"
        )


@router.get("/{internship_id}")
async def get_internship_details(
    internship_id: str,
    payload: dict = Depends(verify_token)
):
    """
    Get detailed information about a specific internship
    
    Args:
        internship_id: Internship ID from database
    
    Returns:
        Internship details
    """
    
    try:
        internship = await supabase_service.get_internship_by_id(internship_id)
        
        if not internship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Internship not found"
            )
        
        return {
            "success": True,
            "internship": internship
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch internship: {str(e)}"
        )


@router.get("/company/{company_name}")
async def search_internships_by_company(
    company_name: str,
    role: Optional[str] = Query(None, description="Specific role at the company"),
    payload: dict = Depends(verify_token)
):
    """
    Search for internships at a specific company
    
    Args:
        company_name: Name of the company
        role: Optional specific role filter
    
    Returns:
        List of internships at the company
    """
    
    try:
        internships = await scraper_service.search_by_company(
            company_name=company_name,
            role=role
        )
        
        return {
            "success": True,
            "internships": internships,
            "count": len(internships)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Company internship search failed: {str(e)}"
        )
