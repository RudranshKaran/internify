from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from routes.utils import verify_token, extract_user_id
from services.supabase_service import supabase_service
from services.llm_service import llm_service
from models.resume import ResumeUploadResponse
import PyPDF2
import io
from datetime import datetime
import asyncio

router = APIRouter(prefix="/resume", tags=["Resume"])


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text content from PDF file
    
    Args:
        file_content: PDF file bytes
    
    Returns:
        Extracted text content
    """
    
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    payload: dict = Depends(verify_token)
):
    """
    Upload resume PDF and extract text content
    
    Args:
        file: PDF file upload
        payload: Authenticated user token
    
    Returns:
        Resume upload response with extracted text
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    try:
        user_id = extract_user_id(payload)
        user_email = payload.get("email", "")
        
        print(f"[RESUME] Upload request from user_id: {user_id}, email: {user_email}")
        
        # Try to ensure user exists - but don't fail if we can't create/fetch
        # The resume table might not have user_id as required foreign key
        try:
            existing_user = await supabase_service.get_user_by_id(user_id)
            if not existing_user:
                print(f"[RESUME] User {user_id} not found, attempting to create...")
                await supabase_service.create_user(
                    email=user_email, 
                    name=user_email.split('@')[0] if user_email else "User",
                    user_id=user_id
                )
                print(f"[RESUME] User creation attempted")
            else:
                print(f"[RESUME] User exists: {existing_user.get('email')}")
        except Exception as e:
            print(f"[RESUME] User check/creation error (continuing anyway): {e}")
            # Continue anyway - the resume save might still work
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_content)
        
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from PDF. Please ensure the file is not encrypted."
            )
        
        # Generate unique file path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = f"{user_id}/resumes/resume_{timestamp}.pdf"
        
        # Upload to Supabase Storage
        uploaded_path = await supabase_service.upload_file(
            bucket="resumes",
            file_path=file_path,
            file_data=file_content
        )
        
        if not uploaded_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload resume to storage"
            )
        
        print(f"[RESUME] File uploaded to storage successfully: {uploaded_path}")
        
        # Save resume metadata to database
        print(f"[RESUME] Saving resume metadata to database for user: {user_id}")
        resume = await supabase_service.save_resume(
            user_id=user_id,
            file_path=file_path,
            extracted_text=extracted_text
        )
        
        if not resume:
            # Try to get more specific error from logs
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save resume metadata to database. Please check if your user account exists in the database and try again. Check server logs for details."
            )

        # Fire-and-forget: extract structured data via Gemini in the background
        resume_id = resume["id"]

        async def _extract_and_store():
            try:
                structured = await llm_service.extract_structured_resume(extracted_text)
                if structured:
                    await supabase_service.update_resume_extracted_data(resume_id, structured)
                    print(f"[RESUME] Structured extraction saved for resume {resume_id}")
                else:
                    print(f"[RESUME] Structured extraction returned None for resume {resume_id}")
            except Exception as e:
                print(f"[RESUME] Background extraction failed for resume {resume_id}: {e}")

        asyncio.create_task(_extract_and_store())

        return ResumeUploadResponse(
            id=resume_id,
            file_path=file_path,
            extracted_text=extracted_text,
            uploaded_at=resume["uploaded_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume upload failed: {str(e)}"
        )


@router.get("/latest")
async def get_latest_resume(payload: dict = Depends(verify_token)):
    """
    Get user's most recently uploaded resume
    
    Returns:
        Latest resume data including extracted text
    """
    
    try:
        user_id = extract_user_id(payload)
        
        resume = await supabase_service.get_latest_resume(user_id)
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found. Please upload a resume first."
            )
        
        return {
            "success": True,
            "resume": resume
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resume: {str(e)}"
        )


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, payload: dict = Depends(verify_token)):
    """
    Delete a resume from storage and database
    
    Args:
        resume_id: Resume ID to delete
        payload: Authenticated user token
    
    Returns:
        Success confirmation
    """
    
    try:
        user_id = extract_user_id(payload)
        
        # Get resume to verify ownership and get file path
        resume = await supabase_service.get_resume_by_id(resume_id, user_id)
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or you don't have permission to delete it"
            )
        
        # Delete from storage
        file_path = resume.get("file_path")
        if file_path:
            await supabase_service.delete_file(bucket="resumes", file_path=file_path)
        
        # Delete from database
        deleted = await supabase_service.delete_resume(resume_id, user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete resume"
            )
        
        return {
            "success": True,
            "message": "Resume deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete resume: {str(e)}"
        )
