import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    """Service for AI email generation using Groq or Gemini"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Determine which service to use
        self.use_groq = bool(self.groq_api_key)
        self.use_gemini = bool(self.gemini_api_key)
        
        if not self.use_groq and not self.use_gemini:
            raise ValueError("No LLM API key found. Please set GROQ_API_KEY or GEMINI_API_KEY")
        
        # Initialize clients
        if self.use_groq:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
            except ImportError:
                print("Groq library not installed. Install with: pip install groq")
                self.use_groq = False
        
        if self.use_gemini and not self.use_groq:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
            except ImportError:
                print("Google Generative AI library not installed. Install with: pip install google-generativeai")
                self.use_gemini = False
    
    async def generate_email(
        self,
        resume_text: str,
        job_description: str,
        job_title: str,
        company_name: str
    ) -> Optional[str]:
        """
        Generate a personalized cold email for job application
        
        Args:
            resume_text: Extracted text from user's resume
            job_description: Job posting description
            job_title: Title of the position
            company_name: Name of the company
        
        Returns:
            Generated email text or None if generation fails
        """
        
        prompt = self._create_prompt(resume_text, job_description, job_title, company_name)
        
        try:
            if self.use_groq:
                return await self._generate_with_groq(prompt)
            elif self.use_gemini:
                return await self._generate_with_gemini(prompt)
        except Exception as e:
            print(f"Error generating email: {e}")
            return None
    
    def _create_prompt(self, resume_text: str, job_description: str, job_title: str, company_name: str) -> str:
        """Create the prompt for LLM"""
        return f"""You are a professional email writer helping someone apply for an internship or job.

Generate a concise, personalized cold email for a job application.

**Job Details:**
- Position: {job_title}
- Company: {company_name}
- Job Description: {job_description[:500]}

**Candidate Resume Summary:**
{resume_text[:800]}

**Requirements:**
1. Professional yet friendly tone
2. 100-150 words maximum
3. Include:
   - Brief greeting mentioning the company
   - 1-2 sentences about why the candidate is interested
   - 2-3 sentences highlighting relevant skills/experience from resume that match the job
   - Clear call-to-action (requesting interview/opportunity to discuss)
4. Do NOT include:
   - Subject line (only body)
   - Signature/closing (will be added separately)
   - Placeholders like [Your Name]
5. Be specific and genuine, not generic

Generate ONLY the email body text, nothing else."""
    
    async def _generate_with_groq(self, prompt: str) -> Optional[str]:
        """Generate email using Groq API"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email writer specializing in job applications."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-70b-8192",  # or "llama3-8b-8192" for faster responses
                temperature=0.7,
                max_tokens=500,
            )
            
            email_text = chat_completion.choices[0].message.content.strip()
            return email_text
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
    
    async def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        """Generate email using Gemini API"""
        try:
            response = self.gemini_model.generate_content(prompt)
            email_text = response.text.strip()
            return email_text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    async def generate_subject_line(self, job_title: str, company_name: str) -> str:
        """Generate a subject line for the email"""
        # Simple template-based subject line
        templates = [
            f"Application for {job_title} Position at {company_name}",
            f"Interested in {job_title} Role at {company_name}",
            f"{job_title} Application - Enthusiastic Candidate",
            f"Passionate Candidate for {job_title} at {company_name}"
        ]
        
        # Return first template for consistency, or could randomize
        return templates[0]


# Singleton instance
llm_service = LLMService()
