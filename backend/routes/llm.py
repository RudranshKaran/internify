from fastapi import APIRouter, Depends, HTTPException, status
from routes.utils import verify_token, extract_user_id
from services.llm_service import llm_service
from services.supabase_service import supabase_service
from models.email import EmailGenerateRequest
from pydantic import BaseModel

router = APIRouter(prefix="/llm", tags=["LLM"])


class EmailGenerateResponse(BaseModel):
    subject: str
    body: str
    success: bool


@router.post("/generate-email", response_model=EmailGenerateResponse)
async def generate_email(
    request: EmailGenerateRequest,
    payload: dict = Depends(verify_token)
):
    """
    Generate a personalized cold email using AI
    
    Args:
        request: Email generation request with job details and resume
    
    Returns:
        Generated email subject and body
    """
    
    try:
        user_id = extract_user_id(payload)
        
        # If resume_text is empty, fetch from database
        resume_text = request.resume_text
        if not resume_text or resume_text.strip() == "":
            resume = await supabase_service.get_latest_resume(user_id)
            
            if not resume:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No resume found. Please upload a resume first."
                )
            
            resume_text = resume["extracted_text"]
        
        # Generate email body using LLM
        email_body = await llm_service.generate_email(
            resume_text=resume_text,
            job_description=request.job_description,
            job_title=request.job_title,
            company_name=request.company_name
        )
        
        if not email_body:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate email. Please try again."
            )
        
        # Generate subject line
        subject = await llm_service.generate_subject_line(
            job_title=request.job_title,
            company_name=request.company_name
        )
        
        return EmailGenerateResponse(
            subject=subject,
            body=email_body,
            success=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email generation failed: {str(e)}"
        )


@router.post("/regenerate-email", response_model=EmailGenerateResponse)
async def regenerate_email(
    request: EmailGenerateRequest,
    payload: dict = Depends(verify_token)
):
    """
    Regenerate email with different variation
    
    This endpoint is identical to generate-email but can be used
    to regenerate if user is not satisfied with first version.
    """
    
    return await generate_email(request, payload)


@router.post("/improve-email")
async def improve_email(
    current_email: str,
    feedback: str,
    payload: dict = Depends(verify_token)
):
    """
    Improve an existing email based on user feedback
    
    Args:
        current_email: Current email text
        feedback: User feedback on what to improve
    
    Returns:
        Improved email text
    """
    
    try:
        # This is a simplified version - could be expanded
        # For now, we'll return a message indicating the feature
        
        return {
            "success": True,
            "message": "Email improvement feature coming soon!",
            "suggestion": "Try regenerating the email or manually editing it for now."
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email improvement failed: {str(e)}"
        )
