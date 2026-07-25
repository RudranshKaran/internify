import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime, timezone

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
            print(f"[SUPABASE] Fetching user by ID: {user_id}")
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            if result.data:
                print(f"[SUPABASE] User found: {result.data[0].get('email')}")
                return result.data[0]
            else:
                print(f"[SUPABASE] No user found with ID: {user_id}")
                return None
        except Exception as e:
            print(f"[SUPABASE] Error fetching user by ID: {e}")
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
        """Create a new user or return existing user if already exists"""
        try:
            user_data = {
                "email": email,
                "name": name
            }
            # If user_id is provided (from auth), use it
            if user_id:
                user_data["id"] = user_id
            
            print(f"[SUPABASE] Creating user with data: {user_data}")
            
            # Try insert first
            result = self.client.table("users").insert(user_data).execute()
            
            if result.data:
                print(f"[SUPABASE] User created successfully: {result.data[0]}")
                return result.data[0]
            else:
                print(f"[SUPABASE] No data returned from user creation")
                return None
        except Exception as e:
            error_str = str(e)
            print(f"[SUPABASE] Error creating user: {type(e).__name__}: {error_str}")
            
            # Check if it's a duplicate key error (user already exists)
            if "duplicate key" in error_str.lower() or "already exists" in error_str.lower() or "unique" in error_str.lower():
                print(f"[SUPABASE] User already exists, attempting to fetch existing user")
                # User already exists, try to fetch it
                if user_id:
                    existing = await self.get_user_by_id(user_id)
                    if existing:
                        print(f"[SUPABASE] Found existing user: {existing}")
                        return existing
                # Try by email
                existing = await self.get_user_by_email(email)
                if existing:
                    print(f"[SUPABASE] Found existing user by email: {existing}")
                    return existing
            
            import traceback
            print(f"[SUPABASE] Full traceback: {traceback.format_exc()}")
            return None
    
    # Resume Operations
    async def save_resume(self, user_id: str, file_path: str, extracted_text: str) -> Optional[Dict[str, Any]]:
        """Save resume metadata to database"""
        try:
            print(f"[SUPABASE] Attempting to save resume for user_id: {user_id}")
            print(f"[SUPABASE] File path: {file_path}")
            print(f"[SUPABASE] Extracted text length: {len(extracted_text)}")
            
            # First verify user exists by trying to query users table
            try:
                user_check = self.client.table("users").select("id").eq("id", user_id).execute()
                if not user_check.data:
                    print(f"[SUPABASE] WARNING: User {user_id} not found in users table!")
                    print(f"[SUPABASE] Attempting to insert user first...")
                    # Try to insert user directly as last resort
                    try:
                        self.client.table("users").insert({
                            "id": user_id,
                            "email": "temp@temp.com",  # Temporary
                            "name": "User"
                        }).execute()
                        print(f"[SUPABASE] Emergency user creation successful")
                    except Exception as ue:
                        print(f"[SUPABASE] Emergency user creation failed: {ue}")
                else:
                    print(f"[SUPABASE] User verification passed")
            except Exception as check_error:
                print(f"[SUPABASE] User check error: {check_error}")
            
            result = self.client.table("resumes").insert({
                "user_id": user_id,
                "file_path": file_path,
                "extracted_text": extracted_text
            }).execute()
            
            print(f"[SUPABASE] Resume save result: {result}")
            
            if result.data:
                print(f"[SUPABASE] Resume saved successfully with id: {result.data[0].get('id')}")
                return result.data[0]
            else:
                print(f"[SUPABASE] No data returned from insert")
                return None
        except Exception as e:
            error_msg = str(e)
            print(f"[SUPABASE] Error saving resume: {type(e).__name__}: {error_msg}")
            
            # Check for specific error types
            if "foreign key" in error_msg.lower():
                print(f"[SUPABASE] FOREIGN KEY CONSTRAINT ERROR - User {user_id} does not exist in users table")
            elif "permission denied" in error_msg.lower() or "policy" in error_msg.lower():
                print(f"[SUPABASE] RLS POLICY ERROR - Check RLS policies in Supabase dashboard")
            elif "violates not-null" in error_msg.lower():
                print(f"[SUPABASE] NULL VALUE ERROR - Check required fields")
                
            import traceback
            print(f"[SUPABASE] Full traceback: {traceback.format_exc()}")
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

    async def update_resume_extracted_data(self, resume_id: str, extracted_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update the extracted_data JSONB column for a resume row."""
        try:
            result = self.client.table("resumes")\
                .update({"extracted_data": extracted_data})\
                .eq("id", resume_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[SUPABASE] Error updating resume extracted_data: {e}")
            return None
    
    # Internship Operations
    async def save_internship(self, internship_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save internship posting to database"""
        try:
            result = self.client.table("internships").insert(internship_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            error_msg = str(e)
            # Check if it's a schema cache error
            if "PGRST205" in error_msg or "schema cache" in error_msg:
                print(f"Error saving internship: Internships table not found in schema cache.")
                print(f"Please run the database migration: docs/database/migration_add_contact_info.sql")
            else:
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
        """Upload file to Supabase Storage, overwriting if file already exists."""
        try:
            file_options = {"content-type": "application/pdf"}
            try:
                self.client.storage.from_(bucket).upload(
                    file_path,
                    file_data,
                    file_options
                )
            except Exception as e:
                error_str = str(e).lower()
                if "duplicate" in error_str or "already exists" in error_str:
                    print(f"[SUPABASE] File exists at {file_path}, updating...")
                    self.client.storage.from_(bucket).update(
                        file_path,
                        file_data,
                        file_options
                    )
                else:
                    raise
            return file_path
        except Exception as e:
            print(f"[SUPABASE] Error uploading file: {e}")
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


    # Discovered Company Operations
    async def upsert_discovered_company(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Upsert a discovered company record.

        On conflict of (user_id, domain, role_title) when domain is known,
        or (user_id, company_name, role_title) when domain is null,
        this updates last_seen_at and source_query instead of duplicating.
        """
        try:
            user_id = data.get("user_id")
            company_name = data.get("company_name")
            domain = data.get("domain")
            role_title = data.get("role_title")

            if not all([user_id, company_name, role_title]):
                print(f"[SUPABASE] Missing required fields for discovered_company upsert")
                return None

            # Build match criteria using the same logic as our partial unique indexes
            match = {"user_id": user_id, "role_title": role_title}
            if domain:
                match["domain"] = domain
            else:
                match["company_name"] = company_name

            # Try to find existing row
            query = self.client.table("discovered_companies").select("id").eq("user_id", user_id).eq("role_title", role_title)

            if domain:
                query = query.eq("domain", domain)
            else:
                query = query.eq("company_name", company_name).is_("domain", "null")

            existing = query.execute()

            if existing.data:
                # Update — refresh last_seen_at and optionally source_query/snippet
                row_id = existing.data[0]["id"]
                update_fields = {"last_seen_at": datetime.now(timezone.utc).isoformat()}
                if data.get("source_query"):
                    update_fields["source_query"] = data["source_query"]
                if data.get("job_description_snippet"):
                    update_fields["job_description_snippet"] = data["job_description_snippet"]

                result = self.client.table("discovered_companies")\
                    .update(update_fields)\
                    .eq("id", row_id)\
                    .execute()
                print(f"[SUPABASE] Updated discovered_company {row_id}: {data.get('company_name')} / {data.get('role_title')}")
                return result.data[0] if result.data else None
            else:
                # Insert
                insert_data = {
                    "user_id": user_id,
                    "company_name": company_name,
                    "domain": domain,
                    "role_title": role_title,
                    "location": data.get("location"),
                    "job_description_snippet": data.get("job_description_snippet"),
                    "source_url": data.get("source_url"),
                    "source_query": data.get("source_query"),
                    "email_status": data.get("email_status", "not_found"),
                }
                result = self.client.table("discovered_companies").insert(insert_data).execute()
                print(f"[SUPABASE] Inserted discovered_company: {data.get('company_name')} / {data.get('role_title')}")
                return result.data[0] if result.data else None

        except Exception as e:
            print(f"[SUPABASE] Error upserting discovered_company: {e}")
            return None

    async def get_discovered_companies(
        self,
        user_id: str,
        email_status: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """Get discovered companies for a user, optionally filtered by email_status."""
        try:
            query = self.client.table("discovered_companies")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("last_seen_at", desc=True)\
                .limit(limit)

            if email_status:
                query = query.eq("email_status", email_status)

            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[SUPABASE] Error fetching discovered companies: {e}")
            return []

    async def get_discovered_companies_paginated(
        self,
        user_id: str,
        email_status: Optional[str] = None,
        limit: int = 50,
        cursor: Optional[str] = None,
    ) -> dict:
        """
        Cursor-paginated version of get_discovered_companies.

        *cursor* is an opaque string encoding ``last_seen_at|id`` so the
        frontend only has to pass one value.  Returns items strictly older
        than the cursor (or earlier in insertion order when timestamps tie),
        plus a ``next_cursor`` for the subsequent page.
        """
        try:
            query = self.client.table("discovered_companies")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("last_seen_at", desc=True)\
                .order("id", desc=True)\
                .limit(limit)

            if email_status:
                query = query.eq("email_status", email_status)

            if cursor:
                parts = cursor.split("|", 1)
                if len(parts) == 2:
                    cursor_ts, cursor_id = parts
                    # last_seen_at < cursor_ts  OR (last_seen_at == cursor_ts AND id < cursor_id)
                    query = query.or_(
                        f"last_seen_at.lt.{cursor_ts},"
                        f"and(last_seen_at.eq.{cursor_ts},id.lt.{cursor_id})"
                    )

            result = query.execute()
            data = result.data if result.data else []

            next_cursor = None
            if len(data) == limit:
                last = data[-1]
                ts = last.get("last_seen_at", "")
                lid = last.get("id", "")
                next_cursor = f"{ts}|{lid}"

            return {
                "data": data,
                "next_cursor": next_cursor,
            }

        except Exception as e:
            print(f"[SUPABASE] Error fetching discovered companies (paginated): {e}")
            return {"data": [], "next_cursor": None}

    async def update_company_email_status(
        self,
        company_id: str,
        user_id: str,
        email_status: str
    ) -> Optional[Dict[str, Any]]:
        """Update the email_status for a discovered company row."""
        try:
            result = self.client.table("discovered_companies")\
                .update({"email_status": email_status})\
                .eq("id", company_id)\
                .eq("user_id", user_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[SUPABASE] Error updating company email status: {e}")
            return None


# Singleton instance
supabase_service = SupabaseService()
