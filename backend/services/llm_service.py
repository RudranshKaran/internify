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
                
                # Use Gemini with system instructions for professional, project-centric emails
                self.system_instruction = "You are an expert at writing professional cold emails for internships. Your PRIMARY RULE: ALWAYS use SPECIFIC, ACTUAL details from the candidate's resume. You MUST extract and use real project names, real technologies, and concrete achievements from resumes. You NEVER write generic emails. You NEVER use phrases like 'various projects', 'multiple technologies', 'several tools', or 'a recent project'. Every single email you write must mention at least ONE specific project by its ACTUAL NAME from the resume, and at least TWO specific technologies by their ACTUAL NAMES. If you cannot find specific details in the resume, you explicitly state what you found. You maintain a professional yet human tone and always end with 'I've attached my resume below for more details on the project and related work.'"
                
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
        """Create the prompt for LLM following Internify Project-First Email Generation Rules"""
        # Sanitize inputs
        resume_text = (resume_text or "").strip()[:1500]
        internship_description = (internship_description or "").strip()[:600]
        internship_title = (internship_title or "").strip()
        company_name = (company_name or "").strip()
        
        # Log what we're using
        print(f"[PROMPT] Creating prompt with resume length: {len(resume_text)}")
        print(f"[PROMPT] Resume text preview: {resume_text[:150]}...")
        print(f"[PROMPT] Position: {internship_title} at {company_name}")
        
        return f"""You are writing a professional cold email for an internship application. You MUST use ACTUAL, SPECIFIC details from the candidate's resume.

## STEP 1: EXTRACT FROM RESUME (MANDATORY)
Read the resume below and extract:
- Name (if present)
- At least ONE specific project name
- At least TWO specific technologies/tools
- Any metrics, achievements, or outcomes

## CANDIDATE'S RESUME:
{resume_text}

## JOB DETAILS:
Position: {internship_title}
Company: {company_name}
Description: {internship_description}

## STEP 2: WRITE EMAIL (140-180 words)

### CRITICAL REQUIREMENTS:

1. **Opening (1 line)**: Reference {company_name}'s work in a specific domain
   - Example: "I've been following {company_name}'s work in embedded systems."

2. **Brief Intro (1 line)**: Simple self-introduction
   - Example: "I'm a computer science student who builds practical tools."

3. **PROJECT SECTION (50%+ of email - 3-4 lines - MOST IMPORTANT)**:
   - YOU MUST use an ACTUAL project name from the resume above
   - Explain: what it does, how you built it (using ACTUAL tech from resume), why it's relevant
   - Example structure: "One project I've spent time on is [ACTUAL PROJECT NAME FROM RESUME], [description]. While building this, I worked with [ACTUAL TECHNOLOGIES FROM RESUME]—skills that translate to [connection to role]."
   - If you use generic phrases like "a recent project" or "various projects", you have FAILED

4. **Connection (1-2 lines)**: Link the project to the company's needs
   - Example: "Designing this required balancing [skill] with [skill], important for [company's domain]."

5. **CTA (1 line)**: Lightweight ask
   - "I'd be happy to walk through the project if helpful."

6. **MANDATORY CLOSING (exact line)**:
   - "I've attached my resume below for more details on the project and related work."

## EXAMPLE OF GOOD OUTPUT (using actual details):
"I've been following Controlytics AI's work in embedded systems.

I'm an electronics engineering student who builds edge AI solutions.

One project I've spent significant time on is SmartSense, a real-time sensor fusion system for industrial monitoring. While building this, I worked extensively with STM32 microcontrollers, FreeRTOS, and TensorFlow Lite—skills that translate well to the embedded systems work your team focuses on.

Designing SmartSense required balancing power efficiency with real-time performance, something equally important when building production-grade embedded solutions.

I'd be happy to walk through the project if helpful.

I've attached my resume below for more details on the project and related work."

## EXAMPLE OF BAD OUTPUT (generic - DO NOT DO THIS):
"I'm interested in the position at your company.

I have experience with various technologies and have worked on multiple projects. I'm passionate about learning and contributing to your team.

I would be grateful for the opportunity to discuss this role."

## NOW WRITE THE EMAIL:
Use ACTUAL project names and technologies from the resume. Do NOT invent anything. Write ONLY the email body (no subject, no signature).
"""
    
    async def _generate_with_groq(self, prompt: str) -> Optional[str]:
        """Generate email using Groq API"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing professional cold emails for internships. You ALWAYS use SPECIFIC details from candidates' resumes—actual project names, real technologies, concrete achievements. You NEVER use generic phrases like 'various projects' or 'multiple technologies'. Every email must reference at least ONE specific project by its actual name from the resume."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-70b-8192",
                temperature=0.75,
                max_tokens=600,
            )
            
            email_text = chat_completion.choices[0].message.content.strip()
            
            # Validate output is not too generic
            if self._is_too_generic(email_text):
                print("[GROQ] Output too generic, attempting fallback")
                return None
            
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
                temperature=0.75,
                max_output_tokens=600,
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
                
                # Validate output is not too generic
                if self._is_too_generic(email_text):
                    print("[GEMINI] Output too generic, using fallback")
                    return await self._generate_with_gemini_fallback(prompt)
                
                return email_text
            else:
                print("Gemini API: No text in response - attempting fallback")
                return await self._generate_with_gemini_fallback(prompt)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            print("Attempting fallback...")
            return await self._generate_with_gemini_fallback(prompt)
    
    def _is_too_generic(self, email_text: str) -> bool:
        """Check if email output is too generic and lacks specific details"""
        email_lower = email_text.lower()
        
        # Red flags that indicate generic content
        generic_phrases = [
            "various projects",
            "multiple projects",
            "several projects",
            "many projects",
            "various technologies",
            "multiple technologies",
            "several technologies",
            "different technologies",
            "a recent project",
            "one of my projects",
            "some projects",
            "i have experience",
            "i am passionate",
            "highly motivated",
            "dear hiring",
            "i am writing to",
            "i would be grateful"
        ]
        
        # Count how many generic phrases appear
        generic_count = sum(1 for phrase in generic_phrases if phrase in email_lower)
        
        # If 2+ generic phrases, it's too generic
        if generic_count >= 2:
            print(f"[VALIDATION] Email is too generic ({generic_count} generic phrases found)")
            return True
        
        # Check if email is too short (less than 100 words suggests lack of detail)
        word_count = len(email_text.split())
        if word_count < 100:
            print(f"[VALIDATION] Email is too short ({word_count} words)")
            return True
        
        return False
    
    async def _generate_with_gemini_fallback(self, original_prompt: str) -> Optional[str]:
        """Fallback method with aggressive resume detail extraction"""
        try:
            print(f"[FALLBACK] Using enhanced fallback with resume detail extraction")
            
            # Parse info from prompt
            lines = original_prompt.split('\n')
            company = "the company"
            position = "this role"
            resume_text = ""
            
            # Extract sections
            in_resume = False
            resume_lines = []
            
            for i, line in enumerate(lines):
                if "Company:" in line:
                    company = line.split("Company:")[-1].strip()
                if "Position:" in line:
                    position = line.split("Position:")[-1].strip()
                if "CANDIDATE'S RESUME:" in line or "Candidate Resume" in line:
                    in_resume = True
                    continue
                if in_resume:
                    if line.strip() and not line.startswith("##") and "JOB DETAILS" not in line:
                        resume_lines.append(line.strip())
                    if "## JOB DETAILS" in line or "## STEP 2" in line:
                        break
            
            resume_text = " ".join(resume_lines)
            print(f"[FALLBACK] Extracted resume text length: {len(resume_text)}")
            
            # Extract domain from position
            domain = "technology"
            domain_adj = "technical"
            
            position_lower = position.lower()
            if "ai" in position_lower or "ml" in position_lower or "machine learning" in position_lower:
                domain = "AI and machine learning"
                domain_adj = "AI"
            elif "embedded" in position_lower or "hardware" in position_lower or "iot" in position_lower:
                domain = "embedded systems and IoT"
                domain_adj = "embedded"
            elif "data" in position_lower:
                domain = "data science"
                domain_adj = "data"
            elif "backend" in position_lower or "server" in position_lower:
                domain = "backend development"
                domain_adj = "backend"
            elif "frontend" in position_lower or "ui" in position_lower or "ux" in position_lower:
                domain = "frontend development"
                domain_adj = "frontend"
            elif "full stack" in position_lower or "fullstack" in position_lower:
                domain = "full-stack development"
                domain_adj = "full-stack"
            
            # AGGRESSIVE technology extraction
            tech_stack = []
            resume_lower = resume_text.lower()
            
            # Comprehensive tech list
            tech_patterns = {
                "Python": ["python"],
                "JavaScript": ["javascript", "js"],
                "TypeScript": ["typescript", "ts"],
                "React": ["react", "reactjs"],
                "Node.js": ["node", "nodejs", "node.js"],
                "Django": ["django"],
                "Flask": ["flask"],
                "FastAPI": ["fastapi", "fast api"],
                "TensorFlow": ["tensorflow", "tf"],
                "PyTorch": ["pytorch", "torch"],
                "C++": ["c++", "cpp"],
                "C": [" c ", "c programming"],
                "Java": ["java"],
                "SQL": ["sql", "mysql", "postgresql"],
                "MongoDB": ["mongodb", "mongo"],
                "Docker": ["docker"],
                "Kubernetes": ["kubernetes", "k8s"],
                "AWS": ["aws", "amazon web services"],
                "Git": ["git", "github"],
                "Linux": ["linux", "ubuntu"],
                "Arduino": ["arduino"],
                "Raspberry Pi": ["raspberry pi", "raspi"],
                "STM32": ["stm32", "stm"],
                "ESP32": ["esp32", "esp"],
                "FreeRTOS": ["freertos", "rtos"],
                "TensorFlow Lite": ["tensorflow lite", "tflite"],
                "MQTT": ["mqtt"],
                "REST API": ["rest", "restful", "rest api"],
                "Next.js": ["next.js", "nextjs"],
                "Tailwind": ["tailwind"],
                "Vue": ["vue", "vuejs"],
                "Angular": ["angular"],
                "Express": ["express", "expressjs"],
                "Redis": ["redis"],
                "Supabase": ["supabase"],
                "Firebase": ["firebase"],
                "LLM": ["llm", "large language model"],
                "OpenAI": ["openai", "gpt"],
                "Gemini": ["gemini"],
                "NLP": ["nlp", "natural language"],
                "Computer Vision": ["computer vision", "cv", "image processing"]
            }
            
            for tech_name, patterns in tech_patterns.items():
                for pattern in patterns:
                    if pattern in resume_lower:
                        if tech_name not in tech_stack:
                            tech_stack.append(tech_name)
                        break
            
            print(f"[FALLBACK] Extracted technologies: {tech_stack[:5]}")
            
            # AGGRESSIVE project name extraction
            project_name = None
            project_desc = None
            
            # Look for capitalized words that might be project names
            words = resume_text.split()
            potential_projects = []
            
            # Common project keywords
            project_indicators = ["project", "built", "developed", "created", "designed", "implemented"]
            
            for i, word in enumerate(words):
                # Look for capitalized multi-word sequences (likely project names)
                if word and len(word) > 3 and word[0].isupper():
                    # Skip common words
                    if word not in ["I", "The", "A", "An", "In", "On", "At", "For", "With", "This", "That", company, "Professional", "Education", "Experience", "Skills"]:
                        # Check if it's near a project indicator
                        context = " ".join(words[max(0,i-5):min(len(words),i+5)]).lower()
                        if any(indicator in context for indicator in project_indicators):
                            potential_projects.append(word)
            
            if potential_projects:
                project_name = potential_projects[0]
                print(f"[FALLBACK] Found potential project: {project_name}")
            
            # Build specific project description based on tech and domain
            if not project_name:
                project_name = "a specialized project"
            
            if not project_desc:
                if tech_stack:
                    primary_tech = tech_stack[0]
                    project_desc = f"a {domain_adj} solution built with {primary_tech}"
                else:
                    project_desc = f"a tool focused on {domain}"
            
            # Generate highly specific email
            tech_line = ""
            if len(tech_stack) >= 3:
                tech_line = f"{tech_stack[0]}, {tech_stack[1]}, and {tech_stack[2]}"
            elif len(tech_stack) == 2:
                tech_line = f"{tech_stack[0]} and {tech_stack[1]}"
            elif len(tech_stack) == 1:
                tech_line = tech_stack[0]
            else:
                tech_line = "modern technologies"
            
            # Craft project-focused email
            email = f"""I've been following {company}'s work in {domain}.

I'm an engineering student who builds practical solutions in {domain_adj} systems.

One project I've spent significant time on is {project_name}, {project_desc}. While building this, I worked extensively with {tech_line}—skills that directly translate to the {domain_adj} work your team focuses on.

Designing {project_name} required balancing functionality with real-world constraints, something equally important when building production-grade solutions at scale.

I'd be happy to walk through the project if helpful.

I've attached my resume below for more details on the project and related work."""
            
            print(f"[FALLBACK] Generated email with {len(email.split())} words")
            return email
            
        except Exception as e:
            print(f"Fallback error: {e}")
            return None
    
    def _get_connection_to_role(self, tech_stack: list, domain: str, position: str) -> str:
        """Generate a connecting sentence based on actual tech stack"""
        if tech_stack:
            # Use actual technologies from resume
            tech_mention = tech_stack[0] if len(tech_stack) == 1 else f"{tech_stack[0]} and {tech_stack[1]}"
            return f"My recent work with {tech_mention} taught me that good code solves problems—even when it breaks at first."
        else:
            return "I like building things that people actually use—even when they break at first."
    
    async def generate_subject_line(self, job_title: str, company_name: str) -> str:
        """Generate a subject line following Internify project-first specification"""
        # Following new rules: 5-8 words, specific, avoid formal application language
        import random
        
        templates = [
            f"Built Internify — relevant to your team",
            f"Applying AI to {job_title.split()[0].lower()} problems",
            f"A project aligned with {company_name}",
            f"Built a tool for {job_title.split()[0].lower()}",
            f"Project relevant to your hiring focus",
            f"How I built an AI tool"
        ]
        
        # Randomize for variety
        return random.choice(templates)


# Singleton instance
llm_service = LLMService()
