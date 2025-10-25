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
                
                # Store genai module for use in generation
                self.genai = genai
                
                # Configure safety settings to be less restrictive for professional content
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                
                # Store safety settings for use in generation calls
                self.safety_settings = {
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
                
                # Use Gemini 2.5 Flash with system instructions to help with context
                # This can help reduce false positives from safety filters
                system_instruction = "You are a professional career counselor and email writer specializing in helping students write internship and job application emails. Your responses are always professional, constructive, and appropriate for workplace communication."
                
                self.gemini_model = genai.GenerativeModel(
                    'gemini-2.5-flash',
                    safety_settings=self.safety_settings,
                    system_instruction=system_instruction
                )
                print("Successfully initialized Gemini with model: gemini-2.5-flash")
            except ImportError:
                print("Google Generative AI library not installed. Install with: pip install google-generativeai")
                self.use_gemini = False
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
                self.use_gemini = False
    
    async def generate_email(
        self,
        resume_text: str,
        internship_description: str,
        internship_title: str,
        company_name: str
    ) -> Optional[str]:
        """
        Generate a personalized cold email for internship application
        
        Args:
            resume_text: Extracted text from user's resume
            internship_description: Internship posting description
            internship_title: Title of the internship position
            company_name: Name of the company
        
        Returns:
            Generated email text or None if generation fails
        """
        
        prompt = self._create_prompt(resume_text, internship_description, internship_title, company_name)
        
        try:
            if self.use_groq:
                return await self._generate_with_groq(prompt)
            elif self.use_gemini:
                return await self._generate_with_gemini(prompt)
        except Exception as e:
            print(f"Error generating email: {e}")
            return None
    
    def _create_prompt(self, resume_text: str, internship_description: str, internship_title: str, company_name: str) -> str:
        """Create the prompt for LLM"""
        # Sanitize inputs to avoid safety filter issues
        resume_text = (resume_text or "").strip()[:800]
        internship_description = (internship_description or "").strip()[:400]
        internship_title = (internship_title or "").strip()
        company_name = (company_name or "").strip()
        
        # Simplified prompt that's less likely to trigger safety filters
        return f"""Write a professional internship application email.

Position: {internship_title}
Company: {company_name}

Role Description:
{internship_description}

Candidate Background:
{resume_text}

Guidelines:
- Write in a professional yet friendly tone
- Keep it 100-150 words
- Start with a greeting
- Express interest in the role
- Highlight 2-3 relevant skills that match the position
- End with a call to action
- Do NOT include subject line or signature
- Use "I" perspective (first person)

Write only the email body:"""
    
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
            # Log the prompt for debugging (first 500 chars)
            print(f"Gemini prompt (truncated): {prompt[:500]}...")
            
            # Add generation config for better control
            generation_config = {
                'temperature': 0.7,
                'max_output_tokens': 500,
            }
            
            # Try with safety settings passed explicitly
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            
            # Check if response was blocked by safety filters
            if not response.candidates:
                print("Gemini API: No candidates returned - attempting with simplified prompt")
                # Try with a simpler, more direct prompt
                return await self._generate_with_gemini_fallback(prompt)
            
            candidate = response.candidates[0]
            
            # Check finish reason
            # 0 = FINISH_REASON_UNSPECIFIED, 1 = STOP (success), 2 = SAFETY, 3 = RECITATION, 4 = OTHER
            if candidate.finish_reason == 2:  # SAFETY
                print(f"Gemini API: Response blocked by safety filters - attempting fallback")
                print(f"Safety ratings: {candidate.safety_ratings}")
                # Try fallback
                return await self._generate_with_gemini_fallback(prompt)
            elif candidate.finish_reason not in [0, 1]:  # Not STOP or UNSPECIFIED
                print(f"Gemini API: Unexpected finish reason: {candidate.finish_reason}")
                return None
            
            # Extract text safely
            if hasattr(response, 'text') and response.text:
                email_text = response.text.strip()
                return email_text
            else:
                print("Gemini API: No text in response")
                return None
                
        except ValueError as e:
            # Handle the specific ValueError for blocked responses
            if "finish_reason" in str(e):
                print(f"Gemini API: Response blocked - attempting fallback")
                return await self._generate_with_gemini_fallback(prompt)
            else:
                print(f"Gemini API error: {e}")
            return None
        except Exception as e:
            print(f"Gemini API error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _generate_with_gemini_fallback(self, original_prompt: str) -> Optional[str]:
        """Fallback method with a template-based approach to avoid safety filters"""
        try:
            # If Gemini keeps blocking, generate a basic template-based email
            print(f"Using template-based fallback for email generation")
            
            # Parse basic info from original prompt (this is a workaround)
            # Extract company and position if available in the prompt
            lines = original_prompt.split('\n')
            company = "your company"
            position = "this internship"
            
            for line in lines:
                if "Company:" in line:
                    company = line.split("Company:")[-1].strip()
                if "Position:" in line:
                    position = line.split("Position:")[-1].strip()
            
            # Generate a professional template email
            template_email = f"""Dear Hiring Team,

I am writing to express my strong interest in the {position} position at {company}. As a Computer Science student with hands-on experience in AI development, I am excited about the opportunity to contribute to your team.

My background includes working with Python, LLMs, and various AI frameworks, which aligns well with the requirements of this role. I am passionate about building innovative AI solutions and eager to apply my skills in a real-world setting.

I would welcome the opportunity to discuss how my experience and enthusiasm can contribute to your team. Thank you for considering my application.

Best regards"""
            
            return template_email
            
        except Exception as e:
            print(f"Template fallback error: {e}")
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
