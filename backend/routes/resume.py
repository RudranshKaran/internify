from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from routes.utils import verify_token, extract_user_id
from services.supabase_service import supabase_service
from models.resume import ResumeUploadResponse
import PyPDF2
import io
from datetime import datetime

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
        
        # Save resume metadata to database
        resume = await supabase_service.save_resume(
            user_id=user_id,
            file_path=file_path,
            extracted_text=extracted_text
        )
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save resume metadata"
            )
        
        return ResumeUploadResponse(
            id=resume["id"],
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
