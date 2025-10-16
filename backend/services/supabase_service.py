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
    
    async def create_user(self, email: str, name: Optional[str] = None, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            user_data = {
                "email": email,
                "name": name
            }
            # If user_id is provided (from auth), use it
            if user_id:
                user_data["id"] = user_id
            
            result = self.client.table("users").insert(user_data).execute()
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
    
    async def get_resume_by_id(self, resume_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get resume by ID for specific user"""
        try:
            result = self.client.table("resumes")\
                .select("*")\
                .eq("id", resume_id)\
                .eq("user_id", user_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching resume by ID: {e}")
            return None
    
    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """Delete resume from database"""
        try:
            result = self.client.table("resumes")\
                .delete()\
                .eq("id", resume_id)\
                .eq("user_id", user_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting resume: {e}")
            return False
    
    # Internship Operations
    async def save_internship(self, internship_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save internship posting to database"""
        try:
            result = self.client.table("internships").insert(internship_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error saving internship: {e}")
            return None
    
    async def get_internship_by_id(self, internship_id: str) -> Optional[Dict[str, Any]]:
        """Get internship by ID"""
        try:
            result = self.client.table("internships").select("*").eq("id", internship_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching internship: {e}")
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
                .select("*, internships(*)")\
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
            # Upload with explicit content type for PDF files
            file_options = {"content-type": "application/pdf"}
            result = self.client.storage.from_(bucket).upload(
                file_path, 
                file_data,
                file_options
            )
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
    
    async def delete_file(self, bucket: str, file_path: str) -> bool:
        """Delete file from Supabase Storage"""
        try:
            self.client.storage.from_(bucket).remove([file_path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


# Singleton instance
supabase_service = SupabaseService()
