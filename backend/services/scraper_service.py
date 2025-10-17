import os
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class ScraperService:
    """Service for scraping internship listings using SerpAPI"""
    
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not found in environment variables")
        
        self.base_url = "https://serpapi.com/search"
    
    async def search_internships(
        self,
        query: str,
        location: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for internship listings on LinkedIn via SerpAPI
        
        Args:
            query: Internship search query (e.g., "Software Engineer Intern")
            location: Location filter (e.g., "Bangalore, India")
            limit: Maximum number of results to return
        
        Returns:
            List of internship dictionaries
        """
        
        try:
            # Build search query with focus on India
            search_query = f"{query} internship"
            
            # If no location specified, default to India
            if not location:
                location = "India"
            
            # Ensure India is included in location
            if "India" not in location and "india" not in location.lower():
                location = f"{location}, India"
            
            search_query += f" in {location}"
            
            params = {
                "engine": "google_jobs",
                "q": search_query,
                "api_key": self.api_key,
                "num": min(limit, 100),  # SerpAPI limit
                "location": "India",  # Geographic targeting
                "google_domain": "google.co.in",  # Use Google India domain
                "gl": "in",  # Country code for India
                "hl": "en",  # Language
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse results
            internships = self._parse_internship_results(data)
            
            return internships[:limit]
        
        except Exception as e:
            print(f"Error searching internships: {e}")
            return []
    
    def _parse_internship_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse SerpAPI response into internship dictionaries"""
        
        internships = []
        
        if "jobs_results" not in data:
            return internships
        
        for job in data["jobs_results"]:
            # Extract contact information
            contact_info = self._extract_contact_info(job)
            
            parsed_internship = {
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", ""),
                "description": job.get("description", ""),
                "link": job.get("share_url") or job.get("apply_link", ""),
                "posted_at": job.get("detected_extensions", {}).get("posted_at"),
                "job_type": ", ".join(job.get("detected_extensions", {}).get("schedule_type", [])),
                "salary": self._extract_salary(job),
                "contact_email": contact_info.get("email"),
                "contact_phone": contact_info.get("phone"),
                "contact_website": contact_info.get("website"),
            }
            
            internships.append(parsed_internship)
        
        return internships
    
    def _extract_salary(self, job: Dict[str, Any]) -> Optional[str]:
        """Extract salary information from internship listing"""
        
        extensions = job.get("detected_extensions", {})
        
        # Check for salary in extensions
        if "salary" in extensions:
            return extensions["salary"]
        
        # Check in description
        description = job.get("description", "").lower()
        if "$" in description or "salary" in description or "₹" in description or "inr" in description:
            # Simple extraction - could be improved
            words = description.split()
            for i, word in enumerate(words):
                if ("$" in word or "₹" in word) and i > 0:
                    return " ".join(words[max(0, i-1):min(len(words), i+3)])
        
        return None
    
    def _extract_contact_info(self, job: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Extract contact information from job listing"""
        import re
        
        contact_info = {
            "email": None,
            "phone": None,
            "website": None
        }
        
        # Get description and other text fields
        description = job.get("description", "")
        title = job.get("title", "")
        company_name = job.get("company_name", "")
        
        # Combine all text for searching
        full_text = f"{description} {title} {company_name}"
        
        # Extract email using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, full_text)
        if emails:
            contact_info["email"] = emails[0]
        
        # Extract Indian phone numbers (various formats)
        # Matches: +91-XXXXXXXXXX, 91XXXXXXXXXX, 0XXXXXXXXXX, XXXXXXXXXX
        phone_pattern = r'(?:\+91|91)?[\s-]?(?:\d{5}[\s-]?\d{5}|\d{10}|\d{3}[\s-]?\d{3}[\s-]?\d{4})'
        phones = re.findall(phone_pattern, full_text)
        if phones:
            # Clean up the phone number
            phone = phones[0].strip()
            contact_info["phone"] = phone
        
        # Extract website/email from apply link
        apply_link = job.get("apply_link", "")
        if apply_link and "mailto:" in apply_link:
            email_from_link = apply_link.replace("mailto:", "").split("?")[0]
            if not contact_info["email"]:
                contact_info["email"] = email_from_link
        
        # Check for company website in related links
        related_links = job.get("related_links", [])
        for link in related_links:
            if isinstance(link, dict) and "link" in link:
                url = link.get("link", "")
                if "careers" in url or "jobs" in url or company_name.lower().replace(" ", "") in url.lower():
                    contact_info["website"] = url
                    break
        
        return contact_info
    
    async def get_internship_details(self, internship_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific internship
        
        Args:
            internship_id: SerpAPI internship ID
        
        Returns:
            Detailed internship dictionary or None
        """
        
        try:
            params = {
                "engine": "google_jobs_listing",
                "q": internship_id,
                "api_key": self.api_key,
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "apply_options" in data:
                return {
                    "title": data.get("title"),
                    "company": data.get("company_name"),
                    "location": data.get("location"),
                    "description": data.get("description"),
                    "apply_link": data.get("apply_options", [{}])[0].get("link"),
                }
            
            return None
        
        except Exception as e:
            print(f"Error fetching internship details: {e}")
            return None
    
    async def search_by_company(
        self,
        company_name: str,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for internships at a specific company
        
        Args:
            company_name: Name of the company
            role: Optional role filter
        
        Returns:
            List of internship dictionaries
        """
        
        query = f"{role + ' at ' if role else ''}{company_name}"
        return await self.search_internships(query)


# Singleton instance
scraper_service = ScraperService()
