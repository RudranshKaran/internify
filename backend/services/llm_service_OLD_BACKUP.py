import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
import re
import json

load_dotenv()


class LLMService:
    """
    Service for AI email generation using Groq or Gemini
    
    ANTI-CONTAMINATION ARCHITECTURE:
    - Every request is stateless with NO memory of previous resumes
    - 3-Phase pipeline enforces resume boundary
    - Validation prevents hallucination and generic output
    """
    
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
                
                # Configure safety settings
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
                
                # ANTI-CONTAMINATION SYSTEM INSTRUCTION
                # Explicitly states no memory, no examples, no cached context
                self.system_instruction = """You are a professional email generation system with STRICT RULES:

1. MEMORY ISOLATION: You have NO memory of previous resumes, candidates, or examples. Every request is independent.
2. RESUME BOUNDARY: You are FORBIDDEN from mentioning ANY project, technology, or achievement that does NOT appear in the current resume text.
3. NO HALLUCINATION: If the resume lacks relevant experience, you acknowledge the gap—you NEVER fabricate projects or skills.
4. PROJECT-FIRST: At least 50% of the email must focus on ONE specific, real project from the resume that matches the job.
5. ANTI-GENERIC: You NEVER use phrases like "various projects", "multiple technologies", "passionate", "highly motivated".

You follow a 3-phase pipeline:
PHASE 1: Extract job requirements (domain, skills, tools)
PHASE 2: Filter resume for ONLY matching content
PHASE 3: Generate email using ONLY Phase 2 approved data

Every output ends with: "I've attached my resume below for more details on the project and related work."
"""
                
                print("Successfully initialized Gemini with anti-contamination system")
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
        Generate a personalized cold email using 3-PHASE PIPELINE
        
        ANTI-CONTAMINATION FLOW:
        Phase 1: Job Requirement Extraction (deterministic)
        Phase 2: Resume Filtering (strict matching only)
        Phase 3: Email Generation (using only Phase 2 data)
        
        Args:
            resume_text: Extracted text from user's resume (CURRENT REQUEST ONLY)
            internship_description: Internship posting description
            internship_title: Title of the internship position
            company_name: Name of the company
        
        Returns:
            Generated email text or None if generation fails
        """
        
        print(f"\n{'='*60}")
        print(f"[PIPELINE] Starting 3-Phase Email Generation")
        print(f"[PIPELINE] Job: {internship_title} at {company_name}")
        print(f"[PIPELINE] Resume length: {len(resume_text)} chars")
        print(f"{'='*60}\n")
        
        # PHASE 1: Extract job requirements (deterministic)
        print("[PHASE 1] Extracting job requirements...")
        job_requirements = self._extract_job_requirements(
            internship_description, 
            internship_title
        )
        print(f"[PHASE 1] ✓ Detected domain: {job_requirements['domain']}")
        print(f"[PHASE 1] ✓ Required skills: {', '.join(job_requirements['required_skills'][:5])}")
        
        # PHASE 2: Filter resume for matching content (strict boundary)
        print("\n[PHASE 2] Filtering resume for job-relevant content...")
        resume_match = self._filter_resume_by_job(resume_text, job_requirements)
        print(f"[PHASE 2] ✓ Found {len(resume_match['projects'])} relevant project(s)")
        print(f"[PHASE 2] ✓ Found {len(resume_match['technologies'])} matching technologies")
        
        if not resume_match['technologies']:
            print(f"[PHASE 2] ⚠ WARNING: No matching technologies found!")
        
        # PHASE 3: Generate email using only approved data
        print("\n[PHASE 3] Generating email with filtered data...")
        prompt = self._create_3phase_prompt(
            job_requirements,
            resume_match,
            company_name,
            internship_title
        )
        
        try:
            if self.use_groq:
                email = await self._generate_with_groq(prompt)
            elif self.use_gemini:
                email = await self._generate_with_gemini(prompt)
            else:
                return None
            
            # VALIDATION: Check for contamination
            if email:
                validation_result = self._validate_email(email, resume_match)
                if not validation_result['valid']:
                    print(f"\n[VALIDATION] ❌ Email failed validation: {validation_result['reason']}")
                    return None
                print(f"[VALIDATION] ✓ Email passed all validation checks")
            
            print(f"\n{'='*60}")
            print(f"[PIPELINE] Email generation complete")
            print(f"{'='*60}\n")
            
            return email
            
        except Exception as e:
            print(f"[PIPELINE] ❌ Error in generation: {e}")
            return None
    
    
    def _extract_job_requirements(self, job_description: str, job_title: str) -> Dict:
        """
        PHASE 1: Extract job requirements (deterministic, non-creative)
        
        Returns structured job requirements WITHOUT generating text
        """
        combined_text = (job_title + " " + job_description).lower()
        
        # Domain detection (hierarchical - most specific first)
        domain = "software development"
        domain_keywords = []
        required_skills = []
        work_type = "development"
        
        # Embedded Systems / Firmware
        if any(word in combined_text for word in [
            "embedded", "firmware", "microcontroller", "arm", "cortex", 
            "bare-metal", "rtos", "freertos", "hardware", "pcb"
        ]):
            domain = "embedded systems and firmware"
            domain_keywords = ["embedded", "firmware", "hardware", "microcontroller"]
            required_skills = ["C", "C++", "embedded", "microcontroller", "ARM", "firmware", "RTOS"]
            work_type = "firmware development"
        
        # AI/ML
        elif any(word in combined_text for word in [
            "machine learning", "deep learning", "neural network", "ai", 
            "nlp", "computer vision", "llm", "transformer"
        ]):
            domain = "AI and machine learning"
            domain_keywords = ["ai", "ml", "machine learning"]
            required_skills = ["Python", "TensorFlow", "PyTorch", "ML", "AI", "neural networks"]
            work_type = "AI/ML development"
        
        # Data Science / Analytics
        elif any(word in combined_text for word in [
            "data scien", "data analy", "analytics", "data engineer", 
            "etl", "pipeline", "dashboard"
        ]):
            domain = "data science and analytics"
            domain_keywords = ["data", "analytics", "pipeline"]
            required_skills = ["Python", "SQL", "Pandas", "data analysis", "visualization"]
            work_type = "data analysis"
        
        # Backend Development
        elif any(word in combined_text for word in [
            "backend", "api", "server", "database", "microservice", "rest"
        ]):
            domain = "backend development"
            domain_keywords = ["backend", "api", "server"]
            required_skills = ["Python", "Node.js", "SQL", "API", "backend", "database"]
            work_type = "backend development"
        
        # Frontend Development
        elif any(word in combined_text for word in [
            "frontend", "react", "vue", "angular", "ui", "ux"
        ]):
            domain = "frontend development"
            domain_keywords = ["frontend", "ui", "web"]
            required_skills = ["React", "JavaScript", "TypeScript", "CSS", "HTML"]
            work_type = "frontend development"
        
        # Full-Stack
        elif any(word in combined_text for word in [
            "full stack", "fullstack", "mern", "mean", "full-stack"
        ]):
            domain = "full-stack development"
            domain_keywords = ["full-stack", "web", "backend", "frontend"]
            required_skills = ["JavaScript", "React", "Node.js", "database", "API"]
            work_type = "full-stack development"
        
        # Extract specific technologies mentioned in job
        tech_mentions = []
        tech_patterns = {
            "C": r"\b[cC]\b(?! *\+)",
            "C++": r"c\+\+|cpp",
            "Python": r"python",
            "JavaScript": r"javascript|js\b",
            "TypeScript": r"typescript|ts\b",
            "React": r"react",
            "Node.js": r"node\.?js",
            "Django": r"django",
            "Flask": r"flask",
            "FastAPI": r"fastapi",
            "TensorFlow": r"tensorflow",
            "PyTorch": r"pytorch",
            "SQL": r"\bsql\b|mysql|postgresql",
            "MongoDB": r"mongodb|mongo\b",
            "Docker": r"docker",
            "Kubernetes": r"kubernetes|k8s",
            "AWS": r"aws|amazon web services",
            "ARM": r"\barm\b|cortex",
            "RTOS": r"rtos|freertos",
            "Git": r"git\b|github",
        }
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, combined_text, re.IGNORECASE):
                if tech not in tech_mentions:
                    tech_mentions.append(tech)
        
        # Merge with domain defaults
        all_required_skills = list(set(required_skills + tech_mentions))
        
        return {
            "domain": domain,
            "domain_keywords": domain_keywords,
            "required_skills": all_required_skills,
            "work_type": work_type,
            "raw_job_text": job_description[:500]  # Limited context
        }
    
    def _filter_resume_by_job(self, resume_text: str, job_requirements: Dict) -> Dict:
        """
        PHASE 2: Filter resume for ONLY job-relevant content (strict matching)
        
        This enforces the RESUME BOUNDARY - only extracts what exists in resume
        AND matches job requirements. Zero hallucination.
        """
        resume_lower = resume_text.lower()
        domain_keywords = job_requirements['domain_keywords']
        required_skills = job_requirements['required_skills']
        
        # Extract matching technologies (STRICT: must be in resume AND in job requirements)
        matching_technologies = []
        
        tech_patterns = {
            "C": {"patterns": [r"\b[cC]\b(?! *\+)", " c ", "c programming", " c,"], "domain": "embedded"},
            "C++": {"patterns": ["c++", "cpp", "c/c++"], "domain": "embedded"},
            "Python": {"patterns": ["python"], "domain": "backend"},
            "JavaScript": {"patterns": ["javascript", " js ", "js,"], "domain": "web"},
            "TypeScript": {"patterns": ["typescript", " ts "], "domain": "web"},
            "React": {"patterns": ["react", "reactjs"], "domain": "frontend"},
            "Node.js": {"patterns": ["node", "nodejs", "node.js"], "domain": "backend"},
            "Next.js": {"patterns": ["next.js", "nextjs"], "domain": "frontend"},
            "Django": {"patterns": ["django"], "domain": "backend"},
            "Flask": {"patterns": ["flask"], "domain": "backend"},
            "FastAPI": {"patterns": ["fastapi"], "domain": "backend"},
            "TensorFlow": {"patterns": ["tensorflow", " tf "], "domain": "ai"},
            "PyTorch": {"patterns": ["pytorch", "torch"], "domain": "ai"},
            "SQL": {"patterns": ["sql", "mysql", "postgresql", "postgres"], "domain": "backend"},
            "MongoDB": {"patterns": ["mongodb", "mongo"], "domain": "backend"},
            "Docker": {"patterns": ["docker"], "domain": "devops"},
            "AWS": {"patterns": ["aws", "amazon web services"], "domain": "cloud"},
            "ARM": {"patterns": ["arm", "cortex"], "domain": "embedded"},
            "STM32": {"patterns": ["stm32"], "domain": "embedded"},
            "ESP32": {"patterns": ["esp32", "esp8266"], "domain": "embedded"},
            "Arduino": {"patterns": ["arduino"], "domain": "embedded"},
            "RTOS": {"patterns": ["rtos", "freertos"], "domain": "embedded"},
            "Git": {"patterns": ["git", "github", "version control"], "domain": "all"},
        }
        
        # Only extract technologies that are BOTH in resume AND in job requirements
        for tech_name, tech_info in tech_patterns.items():
            # Check if job requires this tech
            if tech_name in required_skills or tech_name.lower() in [s.lower() for s in required_skills]:
                # Check if resume contains this tech
                for pattern in tech_info["patterns"]:
                    if isinstance(pattern, str):
                        if pattern in resume_lower:
                            matching_technologies.append(tech_name)
                            break
                    else:  # regex pattern
                        if re.search(pattern, resume_lower, re.IGNORECASE):
                            matching_technologies.append(tech_name)
                            break
        
        # Extract projects (look for capitalized terms near domain keywords)
        projects = []
        words = resume_text.split()
        
        # Domain-relevant context words
        if "embedded" in domain_keywords:
            context_words = ["firmware", "microcontroller", "iot", "sensor", "control", "embedded", "hardware", "device", "pcb"]
        elif "ai" in domain_keywords or "ml" in domain_keywords:
            context_words = ["model", "prediction", "classification", "detection", "nlp", "vision", "learning", "neural"]
        elif "data" in domain_keywords:
            context_words = ["analysis", "analytics", "dashboard", "visualization", "pipeline", "etl", "data"]
        elif "backend" in domain_keywords or "api" in domain_keywords:
            context_words = ["api", "server", "database", "backend", "service", "platform", "endpoint"]
        elif "frontend" in domain_keywords or "ui" in domain_keywords:
            context_words = ["app", "website", "ui", "interface", "dashboard", "portal", "component"]
        else:
            context_words = ["project", "system", "application", "tool", "platform", "built", "developed"]
        
        # Look for project names (capitalized sequences near relevant context)
        skip_words = {
            "I", "The", "A", "An", "In", "On", "At", "For", "With", "This", "That",
            "Professional", "Education", "Experience", "Skills", "Project", "Projects",
            "Work", "Using", "Built", "Technologies", "Tools", "And", "Or"
        }
        
        for i, word in enumerate(words):
            if len(word) > 3 and word[0].isupper() and word not in skip_words:
                # Check surrounding context (10 words before and after)
                context_start = max(0, i - 10)
                context_end = min(len(words), i + 10)
                context = " ".join(words[context_start:context_end]).lower()
                
                # Is this near relevant domain keywords?
                if any(ctx_word in context for ctx_word in context_words):
                    # Extract project description from context
                    description_words = []
                    for j in range(i+1, min(i+15, len(words))):
                        if words[j][0].isupper() and words[j] not in skip_words:
                            break
                        description_words.append(words[j])
                    
                    project_desc = " ".join(description_words[:10])
                    projects.append({
                        "name": word,
                        "context": project_desc,
                        "full_context": context[:200]
                    })
        
        # Remove duplicate projects
        seen_names = set()
        unique_projects = []
        for proj in projects:
            if proj["name"] not in seen_names:
                seen_names.add(proj["name"])
                unique_projects.append(proj)
        
        return {
            "technologies": matching_technologies[:5],  # Top 5 matching technologies
            "projects": unique_projects[:2],  # Top 2 relevant projects
            "has_relevant_experience": len(matching_technologies) > 0 or len(unique_projects) > 0
        }
        """Create the prompt for LLM following InternFlow Project-First Email Generation Rules"""
        # Sanitize inputs
        resume_text = (resume_text or "").strip()[:2000]  # Increased to get more details
        internship_description = (internship_description or "").strip()[:800]  # Increased for full job details
        internship_title = (internship_title or "").strip()
        company_name = (company_name or "").strip()
        
        # Log what we're using
        print(f"[PROMPT] Creating prompt with resume length: {len(resume_text)}")
        print(f"[PROMPT] Resume text preview: {resume_text[:150]}...")
        print(f"[PROMPT] Position: {internship_title} at {company_name}")
        print(f"[PROMPT] Job description: {internship_description[:200]}...")
        
        return f"""You are writing a professional cold email for an internship application. You MUST use ACTUAL, SPECIFIC details from the candidate's resume that are RELEVANT to the job requirements.

## JOB DETAILS (READ THIS FIRST):
Position: {internship_title}
Company: {company_name}
Description: {internship_description}

## STEP 1: ANALYZE JOB REQUIREMENTS
From the job description above, identify:
1. Required technical skills (e.g., C/C++, ARM, Python, etc.)
2. Key domains (e.g., embedded systems, firmware, web development, AI/ML, etc.)
3. Specific tools or frameworks mentioned (e.g., FreeRTOS, React, TensorFlow, etc.)
4. Type of work (e.g., firmware development, backend APIs, data analysis, etc.)

## STEP 2: MATCH WITH CANDIDATE'S RESUME
CANDIDATE'S RESUME:
{resume_text}

From the resume, find and extract ONLY what matches the job requirements:
- Projects that involve the SAME or SIMILAR technical domains
- Technologies/languages that match what the job requires
- Relevant experience that demonstrates capability for THIS specific role

CRITICAL: If the job requires C/C++ and embedded systems, DO NOT mention Python web projects. If the job is about web development, DO NOT mention hardware projects. ONLY use relevant matches.

CRITICAL: If the job requires C/C++ and embedded systems, DO NOT mention Python web projects. If the job is about web development, DO NOT mention hardware projects. ONLY use relevant matches.

## STEP 3: WRITE EMAIL (140-180 words)

### EMAIL STRUCTURE:

1. **Opening (1 line)**: Reference {company_name}'s work in THE SPECIFIC DOMAIN FROM THE JOB
   - Example for embedded systems job: "I've been following {company_name}'s work in embedded systems."
   - Example for AI job: "I've been following {company_name}'s work in AI solutions."

2. **Brief Intro (1 line)**: Self-introduction matching the job domain
   - For embedded systems: "I'm an electronics/computer engineering student who builds firmware solutions."
   - For web development: "I'm a computer science student who builds web applications."
   - For AI/ML: "I'm a data science student who builds ML models."

3. **PROJECT SECTION (50%+ of email - 3-4 lines - MOST IMPORTANT)**:
   THIS IS THE CRITICAL PART - IT MUST BE RELEVANT TO THE JOB!
   
   Structure:
   - "One project I've spent time on is [ACTUAL PROJECT NAME FROM RESUME], [what it does in terms relevant to this job]."
   - "While building this, I worked with [TECHNOLOGIES FROM RESUME THAT MATCH JOB REQUIREMENTS]—skills that translate to [specific job responsibility]."
   
   EXAMPLE FOR EMBEDDED SYSTEMS JOB:
   "One project I've spent significant time on is SensorNode, an IoT device for environmental monitoring. While building this, I worked extensively with C/C++, STM32 microcontrollers, and FreeRTOS—skills that directly translate to the ARM-based firmware development your team focuses on."
   
   EXAMPLE FOR WEB DEVELOPMENT JOB:
   "One project I've spent significant time on is TaskFlow, a real-time collaboration platform. While building this, I worked extensively with React, Node.js, and PostgreSQL—skills that directly translate to the full-stack development your team focuses on."
   
   BAD EXAMPLE (generic/irrelevant):
   "One project I've spent time on is Proven, a technical solution built with Python."

4. **Connection (1-2 lines)**: Link the project to the company's needs
   - Use technical vocabulary from the job description
   - Example for embedded: "Designing this required balancing power consumption with real-time performance, important for production embedded systems."
   - Example for web: "Designing this required balancing user experience with backend scalability, important for production web applications."

5. **CTA (1 line)**: Lightweight ask
   - "I'd be happy to walk through the project if helpful."

6. **MANDATORY CLOSING (exact line)**:
   - "I've attached my resume below for more details on the project and related work."

## VALIDATION CHECKLIST BEFORE YOU WRITE:
☐ Have I identified what the job actually requires? (e.g., C/C++ for embedded, not Python)
☐ Does the resume have projects/experience that match those requirements?
☐ Am I using project names and technologies that are ACTUALLY RELEVANT to this specific job?
☐ If the job is about embedded systems, am I mentioning embedded/hardware/firmware projects (NOT web dev)?
☐ If the job is about web dev, am I mentioning web projects (NOT hardware)?

## EXAMPLE OUTPUTS:

### GOOD: For Embedded Systems Internship with C/C++, ARM requirements
"I've been following Vektor3D's work in embedded systems.

I'm an electronics engineering student who builds firmware for microcontrollers.

One project I've spent significant time on is AutoControl, a motor control system using ARM Cortex-M processors. While building this, I worked extensively with C/C++, ARM assembly, and bare-metal programming—skills that directly translate to the firmware development work your team focuses on.

Designing AutoControl required balancing real-time constraints with hardware limitations, something equally important when building production-grade embedded solutions.

I'd be happy to walk through the project if helpful.

I've attached my resume below for more details on the project and related work."

### BAD: For Embedded Systems Internship (mentions irrelevant tech)
"I've been following the company's work in technology.

I'm an engineering student who builds practical solutions.

One project I've spent time on is Proven, a technical solution built with Python and TypeScript—skills that translate to technical work.

[This is WRONG because job requires C/C++ and ARM, but email mentions Python and TypeScript!]"

## NOW WRITE THE EMAIL:
Use ACTUAL project names and technologies from the resume that MATCH THE JOB REQUIREMENTS. Do NOT use technologies or projects that are irrelevant to this specific job. Write ONLY the email body (no subject, no signature).
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
        """Fallback method with aggressive resume detail extraction matching job requirements"""
        try:
            print(f"[FALLBACK] Using enhanced fallback with job-requirement matching")
            
            # Parse info from prompt
            lines = original_prompt.split('\n')
            company = "the company"
            position = "this role"
            job_description = ""
            resume_text = ""
            
            # Extract sections
            in_resume = False
            in_job = False
            resume_lines = []
            job_lines = []
            
            for i, line in enumerate(lines):
                if "Company:" in line:
                    company = line.split("Company:")[-1].strip()
                if "Position:" in line:
                    position = line.split("Position:")[-1].strip()
                if "Description:" in line:
                    job_description = line.split("Description:")[-1].strip()
                    in_job = True
                    continue
                if "CANDIDATE'S RESUME:" in line or "Candidate Resume" in line:
                    in_resume = True
                    in_job = False
                    continue
                if in_job and line.strip() and not line.startswith("##"):
                    job_lines.append(line.strip())
                if in_resume:
                    if line.strip() and not line.startswith("##") and "STEP 2" not in line and "STEP 3" not in line:
                        resume_lines.append(line.strip())
                    if "## STEP" in line:
                        break
            
            resume_text = " ".join(resume_lines)
            if job_lines:
                job_description = " ".join(job_lines)
            
            print(f"[FALLBACK] Extracted resume text length: {len(resume_text)}")
            print(f"[FALLBACK] Job description: {job_description[:200]}...")
            
            # STEP 1: Analyze job requirements
            job_lower = (position + " " + job_description).lower()
            resume_lower = resume_text.lower()
            
            # Determine domain and required skills from job
            domain = "technology"
            domain_adj = "technical"
            required_skills = []
            intro_variant = "engineering student who builds practical solutions"
            
            # Detect specific domains and required skills
            if any(word in job_lower for word in ["embedded", "firmware", "microcontroller", "arm", "cortex", "iot device", "hardware"]):
                domain = "embedded systems"
                domain_adj = "embedded"
                intro_variant = "electronics/computer engineering student who builds firmware solutions"
                required_skills = ["C", "C++", "embedded", "microcontroller", "ARM", "firmware"]
            elif any(word in job_lower for word in ["ai", "ml", "machine learning", "deep learning", "neural", "llm", "nlp"]):
                domain = "AI and machine learning"
                domain_adj = "AI"
                intro_variant = "computer science student who builds AI/ML models"
                required_skills = ["Python", "TensorFlow", "PyTorch", "ML", "AI", "data"]
            elif any(word in job_lower for word in ["data scien", "data analy", "analytics", "data engineer"]):
                domain = "data science"
                domain_adj = "data"
                intro_variant = "data science student who builds analytical solutions"
                required_skills = ["Python", "SQL", "Pandas", "data", "analytics"]
            elif any(word in job_lower for word in ["backend", "api", "server", "database"]):
                domain = "backend development"
                domain_adj = "backend"
                intro_variant = "computer science student who builds backend systems"
                required_skills = ["Python", "Node.js", "SQL", "API", "backend"]
            elif any(word in job_lower for word in ["frontend", "react", "ui", "ux", "web design"]):
                domain = "frontend development"
                domain_adj = "frontend"
                intro_variant = "computer science student who builds user interfaces"
                required_skills = ["React", "JavaScript", "TypeScript", "CSS", "frontend"]
            elif any(word in job_lower for word in ["full stack", "fullstack", "mern", "mean"]):
                domain = "full-stack development"
                domain_adj = "full-stack"
                intro_variant = "computer science student who builds full-stack applications"
                required_skills = ["React", "Node.js", "JavaScript", "database", "full-stack"]
            
            print(f"[FALLBACK] Detected domain: {domain}")
            print(f"[FALLBACK] Required skills: {required_skills}")
            
            # STEP 2: Extract RELEVANT technologies from resume that match job requirements
            # STEP 2: Extract RELEVANT technologies from resume that match job requirements
            tech_stack = []
            
            # Comprehensive tech list with domain mappings
            tech_patterns = {
                # Embedded/Hardware (for embedded jobs)
                "C": {"patterns": [" c ", "c programming", " c,"], "domains": ["embedded", "firmware"]},
                "C++": {"patterns": ["c++", "cpp"], "domains": ["embedded", "firmware", "backend"]},
                "ARM": {"patterns": ["arm", "cortex"], "domains": ["embedded"]},
                "STM32": {"patterns": ["stm32", "stm"], "domains": ["embedded"]},
                "ESP32": {"patterns": ["esp32", "esp8266"], "domains": ["embedded", "iot"]},
                "Arduino": {"patterns": ["arduino"], "domains": ["embedded", "iot"]},
                "Raspberry Pi": {"patterns": ["raspberry pi", "raspi"], "domains": ["embedded", "iot"]},
                "FreeRTOS": {"patterns": ["freertos", "rtos"], "domains": ["embedded"]},
                "MQTT": {"patterns": ["mqtt"], "domains": ["iot", "embedded"]},
                "I2C/SPI": {"patterns": ["i2c", "spi", "uart"], "domains": ["embedded"]},
                
                # Web Development
                "Python": {"patterns": ["python"], "domains": ["backend", "ai", "data", "full-stack"]},
                "JavaScript": {"patterns": ["javascript", "js"], "domains": ["frontend", "full-stack", "backend"]},
                "TypeScript": {"patterns": ["typescript", "ts"], "domains": ["frontend", "full-stack", "backend"]},
                "React": {"patterns": ["react", "reactjs"], "domains": ["frontend", "full-stack"]},
                "Node.js": {"patterns": ["node", "nodejs", "node.js"], "domains": ["backend", "full-stack"]},
                "Next.js": {"patterns": ["next.js", "nextjs"], "domains": ["frontend", "full-stack"]},
                "Vue": {"patterns": ["vue", "vuejs"], "domains": ["frontend", "full-stack"]},
                "Angular": {"patterns": ["angular"], "domains": ["frontend", "full-stack"]},
                
                # Backend/Database
                "Django": {"patterns": ["django"], "domains": ["backend", "full-stack"]},
                "Flask": {"patterns": ["flask"], "domains": ["backend", "full-stack"]},
                "FastAPI": {"patterns": ["fastapi", "fast api"], "domains": ["backend", "full-stack"]},
                "Express": {"patterns": ["express", "expressjs"], "domains": ["backend", "full-stack"]},
                "SQL": {"patterns": ["sql", "mysql", "postgresql"], "domains": ["backend", "data", "full-stack"]},
                "MongoDB": {"patterns": ["mongodb", "mongo"], "domains": ["backend", "full-stack"]},
                "Redis": {"patterns": ["redis"], "domains": ["backend"]},
                
                # AI/ML
                "TensorFlow": {"patterns": ["tensorflow", "tf"], "domains": ["ai", "ml", "data"]},
                "PyTorch": {"patterns": ["pytorch", "torch"], "domains": ["ai", "ml", "data"]},
                "Keras": {"patterns": ["keras"], "domains": ["ai", "ml"]},
                "Scikit-learn": {"patterns": ["scikit", "sklearn"], "domains": ["ai", "ml", "data"]},
                "Pandas": {"patterns": ["pandas"], "domains": ["data", "ai"]},
                "NumPy": {"patterns": ["numpy"], "domains": ["data", "ai"]},
                
                # DevOps/Tools
                "Docker": {"patterns": ["docker"], "domains": ["backend", "devops", "full-stack"]},
                "Kubernetes": {"patterns": ["kubernetes", "k8s"], "domains": ["backend", "devops"]},
                "AWS": {"patterns": ["aws", "amazon web services"], "domains": ["backend", "devops", "full-stack"]},
                "Git": {"patterns": ["git", "github"], "domains": ["all"]},
            }
            
            # First, extract technologies that match the job domain
            for tech_name, tech_info in tech_patterns.items():
                patterns = tech_info["patterns"]
                tech_domains = tech_info["domains"]
                
                # Check if this tech is relevant to the job domain
                is_relevant = "all" in tech_domains or any(
                    domain_keyword in tech_domains 
                    for domain_keyword in [domain_adj, domain.split()[0].lower()]
                )
                
                if is_relevant:
                    for pattern in patterns:
                        if pattern in resume_lower:
                            if tech_name not in tech_stack:
                                tech_stack.append(tech_name)
                            break
            
            print(f"[FALLBACK] Extracted RELEVANT technologies for {domain}: {tech_stack[:5]}")
            
            # If no domain-specific tech found, look for any mentioned tech as fallback
            if not tech_stack:
                print(f"[FALLBACK] No domain-specific tech found, extracting any technologies...")
                for tech_name, tech_info in tech_patterns.items():
                    for pattern in tech_info["patterns"]:
                        if pattern in resume_lower:
                            if tech_name not in tech_stack:
                                tech_stack.append(tech_name)
                            break
                    if len(tech_stack) >= 3:
                        break
            
            # AGGRESSIVE project name extraction matching domain
            project_name = None
            project_desc = None
            
            # Look for capitalized words that might be project names
            words = resume_text.split()
            potential_projects = []
            
            # Domain-specific project keywords
            if domain_adj == "embedded":
                project_keywords = ["firmware", "microcontroller", "iot", "sensor", "control", "embedded", "hardware", "device"]
            elif domain_adj in ["ai", "ml"]:
                project_keywords = ["model", "prediction", "classification", "detection", "nlp", "vision", "learning"]
            elif domain_adj == "data":
                project_keywords = ["analysis", "analytics", "dashboard", "visualization", "pipeline", "etl"]
            elif domain_adj in ["backend", "full-stack"]:
                project_keywords = ["api", "server", "database", "backend", "service", "platform"]
            elif domain_adj == "frontend":
                project_keywords = ["app", "website", "ui", "interface", "dashboard", "portal"]
            else:
                project_keywords = ["project", "system", "application", "tool", "platform"]
            
            for i, word in enumerate(words):
                # Look for capitalized multi-word sequences (likely project names)
                if word and len(word) > 3 and word[0].isupper():
                    # Skip common words
                    if word not in ["I", "The", "A", "An", "In", "On", "At", "For", "With", "This", "That", company, "Professional", "Education", "Experience", "Skills", "Project", "Projects", "Work", "Using", "Built", "Technologies"]:
                        # Check if it's near domain-relevant keywords
                        context = " ".join(words[max(0,i-10):min(len(words),i+10)]).lower()
                        if any(keyword in context for keyword in project_keywords):
                            potential_projects.append(word)
            
            if potential_projects:
                project_name = potential_projects[0]
                print(f"[FALLBACK] Found domain-relevant project: {project_name}")
            else:
                # Generic project name based on domain
                if domain_adj == "embedded":
                    project_name = "a firmware solution"
                elif domain_adj in ["ai", "ml"]:
                    project_name = "an ML model"
                elif domain_adj == "data":
                    project_name = "a data pipeline"
                else:
                    project_name = "a technical solution"
            
            # Build specific project description based on tech and domain
            if not project_desc:
                if tech_stack:
                    primary_tech = tech_stack[0]
                    if domain_adj == "embedded":
                        project_desc = f"an embedded system built with {primary_tech}"
                    elif domain_adj in ["ai", "ml"]:
                        project_desc = f"an AI solution built with {primary_tech}"
                    elif domain_adj == "data":
                        project_desc = f"a data analytics solution built with {primary_tech}"
                    else:
                        project_desc = f"a {domain_adj} solution built with {primary_tech}"
                else:
                    project_desc = f"a solution focused on {domain}"
            
            # Generate highly specific, job-relevant email
            tech_line = ""
            if len(tech_stack) >= 3:
                tech_line = f"{tech_stack[0]}, {tech_stack[1]}, and {tech_stack[2]}"
            elif len(tech_stack) == 2:
                tech_line = f"{tech_stack[0]} and {tech_stack[1]}"
            elif len(tech_stack) == 1:
                tech_line = tech_stack[0]
            else:
                tech_line = f"tools relevant to {domain}"
            
            # Connection sentence based on domain
            if domain_adj == "embedded":
                connection = f"Designing {project_name} required balancing power efficiency with real-time performance, something equally important when building production-grade embedded solutions."
            elif domain_adj in ["ai", "ml"]:
                connection = f"Designing {project_name} required balancing model accuracy with inference speed, something equally important when deploying AI at scale."
            elif domain_adj == "data":
                connection = f"Designing {project_name} required balancing data quality with processing speed, something equally important for production data systems."
            elif domain_adj in ["backend", "full-stack"]:
                connection = f"Designing {project_name} required balancing scalability with maintainability, something equally important when building production systems."
            else:
                connection = f"Designing {project_name} required balancing functionality with real-world constraints, something equally important for production software."
            
            # Craft domain-matched, project-focused email
            email = f"""I've been following {company}'s work in {domain}.

I'm an {intro_variant} in {domain_adj} systems.

One project I've spent significant time on is {project_name}, {project_desc}. While building this, I worked extensively with {tech_line}—skills that directly translate to the {domain_adj} work your team focuses on.

{connection}

I'd be happy to walk through the project if helpful.

I've attached my resume below for more details on the project and related work."""
            
            print(f"[FALLBACK] Generated domain-matched email with {len(email.split())} words")
            print(f"[FALLBACK] Email preview: {email[:200]}...")
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
        """Generate a subject line following InternFlow project-first specification"""
        # Following new rules: 5-8 words, specific, avoid formal application language
        import random
        
        templates = [
            f"Built InternFlow — relevant to your team",
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
