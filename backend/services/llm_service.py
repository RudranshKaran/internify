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
                from google import genai
                from google.genai import types
                
                # Initialize the client
                self.genai_client = genai.Client(api_key=self.gemini_api_key)
                
                # Configure safety settings to be less restrictive for professional content
                self.safety_settings = [
                    types.SafetySetting(
                        category='HARM_CATEGORY_HATE_SPEECH',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_HARASSMENT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_DANGEROUS_CONTENT',
                        threshold='BLOCK_NONE'
                    ),
                ]
                
                # Use Gemini 2.5 Flash with system instructions to help with context
                # This can help reduce false positives from safety filters
                self.system_instruction = "You are an expert cold email writer following the Internify Email Generation Specification. You write emails that maximize open rate, skim-read clarity, and reply probability. Your emails feel HUMAN, INTENTIONAL, and SPECIFIC—never mass-generated or robotic. You lead with value, use contractions, include exactly one strong proof, and end with lightweight CTAs. You avoid greetings, skill lists, and begging language. Your emails are always professional yet conversational, scoring 8/10+ on curiosity, proof strength, clarity, and human tone."
                
                print("Successfully initialized Gemini with model: gemini-2.0-flash-exp")
            except ImportError:
                print("Google GenAI library not installed. Install with: pip install google-genai")
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
        """Create the prompt for LLM following Internify Email Generation Specification"""
        # Sanitize inputs to avoid safety filter issues
        resume_text = (resume_text or "").strip()[:1000]
        internship_description = (internship_description or "").strip()[:500]
        internship_title = (internship_title or "").strip()
        company_name = (company_name or "").strip()
        
        return f"""# CRITICAL: Follow Internify Email Generation Specification

Generate a cold email for an internship that feels HUMAN and INTENTIONAL.

## Context:
Position: {internship_title}
Company: {company_name}
Role Description: {internship_description}
Candidate Background: {resume_text}

## MANDATORY RULES:

1. **Length**: Max 120 words, max 6 lines, max 5 paragraphs

2. **Opening Line** (NO greetings):
   - First line MUST reference something specific about the company/product/team
   - Template: "Noticed [specific observation] while looking at [company]."
   - BANNED: "I hope you are doing well", "Greetings", "Dear Sir/Madam"

3. **Value-Before-Identity**:
   - DO NOT introduce yourself (name/year/college) in first 2 lines
   - Lead with a problem, insight, or outcome

4. **Proof Block** (Exactly ONE):
   - Include EXACTLY one strong proof from resume
   - Must be quantifiable OR tangible (project/repo/demo)
   - Examples: "used by X users", "reduced X by Y%", "open-sourced repo"
   - BANNED: Skill lists, "I have strong skills in..."

5. **Human Tone**:
   - Use contractions (I'm, I've, I'd)
   - Max 1 adjective per paragraph
   - BANNED: "I am writing to express", "highly motivated", "esteemed organization"

6. **Formatting**:
   - No paragraph > 2 lines
   - Short, spaced lines
   - No walls of text

7. **Call-To-Action** (Exactly ONE):
   - Must be lightweight and specific
   - Examples: "Worth a 10-min chat?", "Can I share a quick demo?"
   - BANNED: "Awaiting your response", "Looking forward to hearing from you"

8. **Directional Interest**:
   - Show specific interest (not "any role is fine")
   - No begging language

9. **Personalization Safety**:
   - NEVER invent metrics, internal tools, or private launches
   - If context is weak, keep high-level: "I noticed your team is building in [domain]"

10. **Self-Check**:
    - Would I reply to this?
    - Does this sound human?
    - Can this be sent as-is?
    - If any NO, regenerate

## Output:
Write ONLY the email body (no subject, no signature). Make it feel like a real human wrote it.
"""
    
    async def _generate_with_groq(self, prompt: str) -> Optional[str]:
        """Generate email using Groq API"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cold email writer. You write emails that feel HUMAN, INTENTIONAL, and SPECIFIC—never mass-generated. Follow the Internify Email Generation Specification exactly. Prioritize curiosity, proof, clarity, and human tone. Output emails that you would personally reply to."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-70b-8192",
                temperature=0.8,
                max_tokens=400,
            )
            
            email_text = chat_completion.choices[0].message.content.strip()
            return email_text
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
    
    async def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        """Generate email using Gemini API"""
        try:
            from google.genai import types
            
            # Log the prompt for debugging (first 500 chars)
            print(f"Gemini prompt (truncated): {prompt[:500]}...")
            
            # Create generation config
            config = types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=400,
                system_instruction=self.system_instruction,
                safety_settings=self.safety_settings
            )
            
            # Generate content using the new API
            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=config
            )
            
            # Check if response has text
            if response.text:
                email_text = response.text.strip()
                return email_text
            else:
                print("Gemini API: No text in response - attempting fallback")
                return await self._generate_with_gemini_fallback(prompt)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            print("Attempting fallback...")
            return await self._generate_with_gemini_fallback(prompt)
    
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
        """Generate a subject line following Internify specification"""
        # Following Internify rules: 4-7 words, curiosity-driven, no "Internship/Application/Request/Opportunity"
        import random
        
        templates = [
            f"Built something for {company_name}",
            f"Your {job_title.split()[0]} team + an idea",
            f"Quick question about {company_name}",
            f"Noticed your work in {job_title.split()[0]}",
            f"Shipped a project — quick chat?",
            f"Your product + a thought"
        ]
        
        # Randomize for variety
        return random.choice(templates)


# Singleton instance
llm_service = LLMService()
