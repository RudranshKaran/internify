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
        request: Email generation request with internship details and resume
    
    Returns:
        Generated email subject and body
    """
    
    try:
        user_id = extract_user_id(payload)
        user_email = payload.get("email", "")
        candidate_name = payload.get("user_metadata", {}).get("full_name", "") or payload.get("email", "").split("@")[0]

        # Fetch resume from database — includes extracted_data if available
        resume_text = request.resume_text
        extracted_data = None

        if not resume_text or resume_text.strip() == "":
            print(f"[LLM] No resume_text in request, fetching from database for user: {user_id}")
            resume = await supabase_service.get_latest_resume(user_id)

            if not resume:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No resume found. Please upload a resume first."
                )

            resume_text = resume["extracted_text"]
            extracted_data = resume.get("extracted_data")
            print(f"[LLM] Fetched resume from database, length: {len(resume_text)} characters")
            if extracted_data:
                print(f"[LLM] Found pre-extracted structured data")
            else:
                print(f"[LLM] No pre-extracted data — falling back to deterministic parsing")
        else:
            print(f"[LLM] Using resume_text from request, length: {len(resume_text)} characters")

        print(f"[LLM] Candidate name: {candidate_name}")
        print(f"[LLM] ===== EMAIL GENERATION FLOW =====")

        # Generate email using LLM — returns dict with subject + body
        result = await llm_service.generate_email(
            resume_text=resume_text,
            internship_description=request.internship_description,
            internship_title=request.internship_title,
            company_name=request.company_name,
            extracted_data=extracted_data,
            candidate_name=candidate_name,
        )

        subject = (result.get("subject") or "").strip()
        body = (result.get("body") or "").strip()

        if not subject or not body:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="LLM provider returned an incomplete response."
            )

        print(f"[LLM] Email generated — subject: {len(subject)}ch, body: {len(body)}ch ({len(body.split())} words)")

        return EmailGenerateResponse(
            subject=subject,
            body=body,
            success=True
        )
    
    except HTTPException:
        raise
    except RuntimeError as e:
        # LLM provider errors (invalid key, quota, timeout) → 502 Bad Gateway
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )
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
