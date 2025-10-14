import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class SupabaseService:
    """Service for Supabase database, auth, and storage operations"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    # User Operations
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            result = self.client.table("users").select("*").eq("email", email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    async def create_user(self, email: str, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            result = self.client.table("users").insert({
                "email": email,
                "name": name
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    # Resume Operations
    async def save_resume(self, user_id: str, file_path: str, extracted_text: str) -> Optional[Dict[str, Any]]:
        """Save resume metadata to database"""
        try:
            result = self.client.table("resumes").insert({
                "user_id": user_id,
                "file_path": file_path,
                "extracted_text": extracted_text
            }).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error saving resume: {e}")
            return None
    
    async def get_latest_resume(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's latest resume"""
        try:
            result = self.client.table("resumes")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("uploaded_at", desc=True)\
                .limit(1)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching resume: {e}")
            return None
    
    # Job Operations
    async def save_job(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save job posting to database"""
        try:
            result = self.client.table("jobs").insert(job_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error saving job: {e}")
            return None
    
    async def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        try:
            result = self.client.table("jobs").select("*").eq("id", job_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching job: {e}")
            return None
    
    # Email Operations
    async def save_email(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save sent email to database"""
        try:
            result = self.client.table("emails").insert(email_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error saving email: {e}")
            return None
    
    async def get_user_emails(self, user_id: str, limit: int = 50) -> list:
        """Get user's email history"""
        try:
            result = self.client.table("emails")\
                .select("*, jobs(*)")\
                .eq("user_id", user_id)\
                .order("sent_at", desc=True)\
                .limit(limit)\
                .execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    # Storage Operations
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes) -> Optional[str]:
        """Upload file to Supabase Storage"""
        try:
            result = self.client.storage.from_(bucket).upload(file_path, file_data)
            return file_path
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    async def get_file_url(self, bucket: str, file_path: str) -> Optional[str]:
        """Get public URL for file"""
        try:
            result = self.client.storage.from_(bucket).get_public_url(file_path)
            return result
        except Exception as e:
            print(f"Error getting file URL: {e}")
            return None


# Singleton instance
supabase_service = SupabaseService()
