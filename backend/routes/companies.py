from fastapi import APIRouter, Depends, HTTPException, status, Query
from routes.utils import verify_token, extract_user_id
from services.supabase_service import supabase_service
from typing import Optional

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/discovered")
async def get_discovered_companies(
    email_status: Optional[str] = Query(None, description="Filter by email status: not_found, found, verified"),
    limit: int = Query(50, ge=1, le=200, description="Number of results per page"),
    cursor: Optional[str] = Query(None, description="Opaque cursor from the previous page's response for cursor-based pagination"),
    payload: dict = Depends(verify_token)
):
    """
    Get companies discovered during internship searches for the authenticated user,
    with cursor-based pagination.

    The first request omits *cursor*.  Subsequent requests pass the
    ``next_cursor`` value returned in the previous response.  When
    ``next_cursor`` is ``null`` there are no more pages.
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
            detail=f"Failed to fetch discovered companies: {str(e)}"
        )


@router.get("/discovered/all")
async def get_all_discovered_companies(
    email_status: Optional[str] = Query(None, description="Filter by email status: not_found, found, verified"),
    payload: dict = Depends(verify_token)
):
    """
    Get **all** discovered companies at once (no pagination).

    Intended for small datasets or export.  For the dashboard list prefer
    the paginated ``GET /discovered`` endpoint instead.
    """
    try:
        user_id = extract_user_id(payload)
        companies = await supabase_service.get_discovered_companies(
            user_id=user_id,
            email_status=email_status,
            limit=5000,
        )

        return {
            "success": True,
            "companies": companies,
            "count": len(companies),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch discovered companies: {str(e)}"
        )


@router.patch("/discovered/{company_id}/email-status")
async def update_company_email_status(
    company_id: str,
    email_status: str = Query(..., description="New email status: not_found, found, verified"),
    payload: dict = Depends(verify_token)
):
    """
    Update the email discovery status for a company.
    """
    valid_statuses = {"not_found", "found", "verified"}
    if email_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email_status. Must be one of: {', '.join(valid_statuses)}"
        )

    try:
        user_id = extract_user_id(payload)
        result = await supabase_service.update_company_email_status(
            company_id=company_id,
            user_id=user_id,
            email_status=email_status
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found or not owned by this user"
            )

        return {
            "success": True,
            "company": result
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update email status: {str(e)}"
        )
