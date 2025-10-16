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
            location: Location filter (e.g., "San Francisco, CA")
            limit: Maximum number of results to return
        
        Returns:
            List of internship dictionaries
        """
        
        try:
            # Build search query
            search_query = query
            if location:
                search_query += f" in {location}"
            
            params = {
                "engine": "google_jobs",
                "q": search_query,
                "api_key": self.api_key,
                "num": min(limit, 100),  # SerpAPI limit
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
            parsed_internship = {
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", ""),
                "description": job.get("description", ""),
                "link": job.get("share_url") or job.get("apply_link", ""),
                "posted_at": job.get("detected_extensions", {}).get("posted_at"),
                "job_type": ", ".join(job.get("detected_extensions", {}).get("schedule_type", [])),
                "salary": self._extract_salary(job),
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
        if "$" in description or "salary" in description:
            # Simple extraction - could be improved
            words = description.split()
            for i, word in enumerate(words):
                if "$" in word and i > 0:
                    return " ".join(words[max(0, i-1):min(len(words), i+3)])
        
        return None
    
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
