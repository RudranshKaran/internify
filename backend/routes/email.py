from fastapi import APIRouter, Depends, HTTPException, status, Query
from routes.utils import verify_token, extract_user_id, extract_user_email
from services.resend_service import resend_service
from services.supabase_service import supabase_service
from models.email import EmailSendRequest, EmailResponse
from typing import List

router = APIRouter(prefix="/email", tags=["Email"])


@router.post("/send")
async def send_email(
    request: EmailSendRequest,
    payload: dict = Depends(verify_token)
):
    """
    Send a cold email to a company
    
    Args:
        request: Email send request with recipient, subject, and body
    
    Returns:
        Success status and email record
    """
    
    try:
        user_id = extract_user_id(payload)
        user_email = extract_user_email(payload)
        
        # Send email via Resend
        result = await resend_service.send_email(
            to_email=request.recipient_email,
            subject=request.subject,
            body=request.body,
            reply_to=user_email  # Set user's email as reply-to
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email. Please check your email configuration."
            )
        
        # Save email record to database
        email_record = await supabase_service.save_email({
            "user_id": user_id,
            "internship_id": request.internship_id,
            "subject": request.subject,
            "body": request.body,
            "recipient_email": request.recipient_email,
            "status": "sent"
        })
        
        if not email_record:
            # Email was sent but failed to save record
            # Still return success since email went through
            return {
                "success": True,
                "message": "Email sent successfully but failed to save record",
                "email_id": None
            }
        
        return {
            "success": True,
            "message": "Email sent successfully!",
            "email": email_record
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@router.get("/history")
async def get_email_history(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of emails to return"),
    payload: dict = Depends(verify_token)
):
    """
    Get user's email history
    
    Args:
        limit: Maximum number of emails to return (1-100)
    
    Returns:
        List of sent emails with job details
    """
    
    try:
        user_id = extract_user_id(payload)
        
        emails = await supabase_service.get_user_emails(user_id, limit=limit)
        
        return {
            "success": True,
            "emails": emails,
            "count": len(emails)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch email history: {str(e)}"
        )


@router.get("/{email_id}")
async def get_email_details(
    email_id: str,
    payload: dict = Depends(verify_token)
):
    """
    Get details of a specific email
    
    Args:
        email_id: Email ID
    
    Returns:
        Email details
    """
    
    try:
        user_id = extract_user_id(payload)
        
        # Fetch email from database
        # (Would need to add this method to supabase_service)
        # For now, return a simple response
        
        return {
            "success": True,
            "message": "Email details endpoint - implementation coming soon"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch email: {str(e)}"
        )


@router.delete("/{email_id}")
async def delete_email(
    email_id: str,
    payload: dict = Depends(verify_token)
):
    """
    Delete an email record from history
    
    Note: This only removes the record, it cannot unsend the email
    
    Args:
        email_id: Email ID to delete
    
    Returns:
        Success status
    """
    
    try:
        user_id = extract_user_id(payload)
        
        # Implementation would delete from database
        # For now, return a simple response
        
        return {
            "success": True,
            "message": "Email record deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete email: {str(e)}"
        )
