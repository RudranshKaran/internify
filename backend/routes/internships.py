from fastapi import APIRouter, Depends, HTTPException, status, Query
from routes.utils import verify_token, extract_user_id
from services.scraper_service import scraper_service
from services.supabase_service import supabase_service
from typing import Optional
from urllib.parse import urlparse
import asyncio

router = APIRouter(prefix="/internships", tags=["Internships"])


@router.get("")
async def list_discovered_companies(
    email_status: Optional[str] = Query(None, description="Filter by email status: not_found, found, verified"),
    limit: int = Query(50, ge=1, le=200, description="Results per page"),
    cursor: Optional[str] = Query(None, description="Opaque cursor from previous page for pagination"),
    payload: dict = Depends(verify_token)
):
    """
    List companies discovered during searches — reads from the
    ``discovered_companies`` table.  Never calls SerpAPI.

    Ordered by ``last_seen_at`` descending so the freshest discoveries
    appear first.  Supports cursor-based pagination: omit *cursor* on
    the first request, then pass the ``next_cursor`` from the response.
    When ``next_cursor`` is ``null`` there are no more pages.
    """
    try:
        user_id = extract_user_id(payload)
        result = await supabase_service.get_discovered_companies_paginated(
            user_id=user_id,
            email_status=email_status,
            limit=limit,
            cursor=cursor,
        )

        return {
            "success": True,
            "companies": result["data"],
            "count": len(result["data"]),
            "next_cursor": result["next_cursor"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list companies: {str(e)}"
        )


# ── Background pipeline ──────────────────────────────────────────

async def _run_discovery_pipeline(
    user_id: str,
    role: str,
    location: Optional[str],
) -> None:
    """
    Fire SerpAPI variants and upsert results into discovered_companies.
    Runs as a fire-and-forget background task so the endpoint returns
    immediately.  Every per-item error is caught so a single failure
    never cancels the rest of the pipeline.
    """
    try:
        all_results = await scraper_service.search_all_variants(
            role=role,
            location=location,
        )
    except Exception as e:
        print(f"[DISCOVERY] Fatal error in SerpAPI phase: {e}")
        return

    upserted = 0
    for job in all_results:
        try:
            link = job.get("link") or ""
            domain = None
            if link:
                parsed = urlparse(link)
                domain = parsed.netloc or None

            company_data = {
                "user_id": user_id,
                "company_name": job.get("company", ""),
                "domain": domain,
                "role_title": job.get("title", ""),
                "location": job.get("location"),
                "job_description_snippet": (job.get("description") or "")[:500],
                "source_url": link,
                "source_query": job.get("_surfaced_by", role),
            }
            await supabase_service.upsert_discovered_company(company_data)
            upserted += 1
        except Exception as e:
            print(f"[DISCOVERY] Failed to upsert company '{job.get('company')}': {e}")

    print(f"[DISCOVERY] Pipeline finished — {upserted} companies upserted for user {user_id}")


@router.get("/search")
async def search_internships(
    role: str = Query(..., description="Internship role or title to search for"),
    location: Optional[str] = Query(None, description="Location filter"),
    payload: dict = Depends(verify_token)
):
    """
    Search for internship listings using multiple SerpAPI query variants.

    Generates 3–5 varied queries from the *role* string (synonym expansion,
    gerund forms, etc.), then kicks off the full pipeline — SerpAPI calls,
    deduplication, and upserts to ``discovered_companies`` — as a **background
    task** so this endpoint returns immediately.

    The frontend can poll ``GET /internships`` (the dashboard list endpoint)
    to see results as they arrive.  If a single variant or upsert fails it
    does **not** stop the others.
    """
    try:
        user_id = extract_user_id(payload)

        # Fire-and-forget: the pipeline runs in a separate asyncio task
        asyncio.create_task(
            _run_discovery_pipeline(
                user_id=user_id,
                role=role,
                location=location,
            )
        )

        return {
            "success": True,
            "message": "Search started — results will appear in the company list as they arrive.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start search: {str(e)}"
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
