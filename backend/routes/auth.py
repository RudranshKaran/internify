from fastapi import APIRouter, Depends, HTTPException, status
from routes.utils import verify_token, extract_user_id, extract_user_email
from services.supabase_service import supabase_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/verify")
async def verify_auth_token(payload: dict = Depends(verify_token)):
    """
    Verify Supabase JWT token and return user info
    
    This endpoint validates the token and ensures the user exists in the database.
    If the user doesn't exist, it creates a new user record.
    """
    
    try:
        user_id = extract_user_id(payload)
        email = extract_user_email(payload)
        
        # Check if user exists in database
        user = await supabase_service.get_user_by_id(user_id)
        
        # Create user if doesn't exist
        if not user:
            name = payload.get("user_metadata", {}).get("name")
            user = await supabase_service.create_user(email=email, name=name)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user record"
                )
        
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": email,
                "name": user.get("name")
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication verification failed: {str(e)}"
        )


@router.get("/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    """
    Get current authenticated user's information
    """
    
    try:
        user_id = extract_user_id(payload)
        
        user = await supabase_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "success": True,
            "user": user
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user: {str(e)}"
        )
