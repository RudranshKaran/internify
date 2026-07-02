import os
import requests
from typing import Optional, List, Dict, Any, Set
import re
from urllib.parse import urlparse
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

    # ── Query variant generation ──────────────────────────────────────

    ROLE_SYNONYMS: Dict[str, List[str]] = {
        "engineer": ["developer", "software engineer", "swe", "programmer", "software developer"],
        "developer": ["engineer", "software engineer", "programmer", "software developer", "swe"],
        "intern": ["internship", "trainee", "apprentice", "graduate trainee"],
        "analyst": ["analytics", "business analyst", "data analyst", "insights"],
        "data scientist": ["ml engineer", "ai engineer", "machine learning engineer", "data analyst"],
        "designer": ["design", "ux designer", "product designer", "ui designer"],
        "product manager": ["pm", "product", "program manager", "technical product manager"],
        "marketing": ["growth", "digital marketing", "brand marketing", "content marketing"],
        "finance": ["financial analyst", "accounting", "investment banking", "corporate finance"],
        "consulting": ["strategy", "management consultant", "business consultant", "advisory"],
    }

    # Terms that get swapped for diversity rather than kept as-is
    _VARIANT_TEMPLATES = [
        "{role} intern",
        "{role} internship",
        "{role}",
        "intern {role_base}",
        "{alt_role} intern",
    ]

    @staticmethod
    def _tokenize(phrase: str) -> List[str]:
        """Split a phrase into lowercase tokens."""
        return phrase.lower().split()

    def _generate_query_variants(self, role: str) -> List[str]:
        """
        Generate 3–5 search query variants from a base role string.
        Uses synonym expansion so, for example, 'Software Engineer Intern'
        produces queries like 'Software Developer Intern', 'SWE Internship', etc.
        """
        role_lower = role.lower().strip()
        tokens = self._tokenize(role_lower)

        # Pick the first token that matches a synonym key
        base_key = None
        for token in tokens:
            if token in self.ROLE_SYNONYMS:
                base_key = token
                break

        variants: List[str] = []
        seen: Set[str] = set()

        # 1. Original query
        original = f"{role_lower} internship"
        variants.append(original)
        seen.add(original)

        # 2. Drop "intern" / "internship" suffix if present
        core_tokens = [t for t in tokens if t not in ("intern", "internship", "trainee", "apprentice")]
        core_role = " ".join(core_tokens) if core_tokens else role_lower

        # 3. Gerund variant: "Software Engineer" → "Software Engineering"
        gerund_role = re.sub(r'\bengineer\b', 'engineering', core_role)
        gerund_role = re.sub(r'\bdevelop\b', 'developing', gerund_role)
        gerund_query = f"{gerund_role} intern"
        if gerund_query not in seen:
            variants.append(gerund_query)
            seen.add(gerund_query)

        # 4. Synonym variant if we found a key
        if base_key and base_key in self.ROLE_SYNONYMS:
            for synonym in self.ROLE_SYNONYMS[base_key]:
                synonym_role = core_role.replace(base_key, synonym, 1)
                syn_query = f"{synonym_role} intern"
                if syn_query not in seen:
                    variants.append(syn_query)
                    seen.add(syn_query)
                    if len(variants) >= 5:
                        break

        # 5. Gerund + synonym combo
        if base_key and base_key in self.ROLE_SYNONYMS and len(variants) < 5:
            for synonym in self.ROLE_SYNONYMS[base_key]:
                syn_gerund = synonym.replace("engineer", "engineering").replace("developer", "developing")
                if syn_gerund == synonym:
                    continue
                syn_gerund_role = core_role.replace(base_key, syn_gerund, 1)
                sg_query = f"{syn_gerund_role} intern"
                if sg_query not in seen:
                    variants.append(sg_query)
                    seen.add(sg_query)
                    if len(variants) >= 5:
                        break

        # Ensure we have at least 3, pad with the original if needed
        while len(variants) < 3:
            pad = original if original not in seen else f"{role_lower} job"
            if pad not in seen:
                variants.append(pad)
                seen.add(pad)

        return variants[:5]

    # ── Multi-variant search ──────────────────────────────────────────

    async def search_all_variants(
        self,
        role: str,
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate query variants from *role*, fire one SerpAPI call per variant
        with ``num=100``, and return a deduplicated list (by company domain).

        Each search call costs the same as a 10-result call, so this is the
        most efficient way to maximise coverage per credit spent.
        """
        variants = self._generate_query_variants(role)
        print(f"[SCRAPER] Generated {len(variants)} variants: {variants}")

        seen_domains: Set[str] = set()
        combined: List[Dict[str, Any]] = []

        for i, variant in enumerate(variants):
            print(f"[SCRAPER] Variant {i+1}/{len(variants)}: '{variant}'")
            try:
                results = await self.search_internships(query=variant, location=location, limit=100)
            except Exception as e:
                print(f"[SCRAPER] Variant '{variant}' failed, skipping: {e}")
                continue

            for job in results:
                link = job.get("link") or ""
                domain = urlparse(link).netloc if link else None

                # Some results don't have a link — deduplicate by company name instead
                dedup_key = domain or job.get("company", "").lower().strip()

                if dedup_key and dedup_key not in seen_domains:
                    seen_domains.add(dedup_key)
                    # Tag which variant surfaced this company
                    job["_surfaced_by"] = variant
                    combined.append(job)

        print(f"[SCRAPER] Combined {len(combined)} unique companies across {len(variants)} variants")
        return combined
    
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
