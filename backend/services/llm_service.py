import os
import asyncio
from typing import Optional, Dict, List
from dotenv import load_dotenv
import re

load_dotenv()


class LLMService:
    """
    Service for AI email generation using Gemini
    
    ANTI-CONTAMINATION ARCHITECTURE:
    - Every request is stateless with NO memory of previous resumes
    - 3-Phase pipeline enforces resume boundary
    - Validation prevents hallucination and generic output
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if not self.gemini_api_key:
            raise ValueError("No LLM API key found. Please set GEMINI_API_KEY in your .env file")
        
        # Initialize Gemini client
        try:
            from google import genai
            from google.genai import types
            
            # Initialize the client
            self.genai_client = genai.Client(api_key=self.gemini_api_key)
            
            # Configure safety settings to disable all safety filters for professional content
            # This prevents false positives on job-related emails
            self.safety_settings = [
                types.SafetySetting(
                    category='HARM_CATEGORY_HATE_SPEECH',
                    threshold='OFF'
                ),
                types.SafetySetting(
                    category='HARM_CATEGORY_HARASSMENT',
                    threshold='OFF'
                ),
                types.SafetySetting(
                    category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                    threshold='OFF'
                ),
                types.SafetySetting(
                    category='HARM_CATEGORY_DANGEROUS_CONTENT',
                    threshold='OFF'
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
            
            print(f"✓ Initialized Gemini with anti-contamination system (model={self.gemini_model})")
        except ImportError:
            raise RuntimeError("Google GenAI library not installed. Install with: pip install google-genai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini: {e}")
    
    async def generate_email(
        self,
        resume_text: str,
        internship_description: str,
        internship_title: str,
        company_name: str,
        extracted_data: Optional[Dict] = None,
        candidate_name: str = "",
    ) -> Dict:
        """
        Generate a personalized cold email using 3-PHASE PIPELINE.

        When *extracted_data* (from the run-once Gemini extraction) is
        provided, the pipeline is:

          Phase 1 — Structured job requirement extraction (Gemini call)
          Phase 2 — Resume-to-job matching (set overlap)
          Phase 3 — Email generation via matched-data prompt (Gemini call)

        Returns a dict with ``subject`` and ``body`` keys.
        """
        print(f"\n{'='*60}")
        print(f"[PIPELINE] Starting 3-Phase Email Generation")
        print(f"[PIPELINE] Job: {internship_title} at {company_name}")
        print(f"[PIPELINE] Has extracted_data: {extracted_data is not None}")
        print(f"{'='*60}\n")

        if extracted_data:
            # ── New pipeline: extract job requirements → match → write ──
            print("[PIPELINE] Phase 1 — Extracting job requirements via Gemini…")
            job_reqs = await self._extract_job_requirements_structured(
                internship_description, internship_title
            ) or self._extract_job_requirements(internship_description, internship_title)

            print("[PIPELINE] Phase 2 — Matching resume to job requirements…")
            match_statements = self._match_resume_to_job(extracted_data, job_reqs)

            print("[PIPELINE] Phase 3 — Generating email from explicit match data…")
            prompt = self._create_matched_prompt(
                match_statements=match_statements,
                job_reqs=job_reqs,
                internship_title=internship_title,
                company_name=company_name,
                candidate_name=candidate_name,
            )

            result = await self._generate_with_gemini_json(prompt)

            if result and result.get("subject") and result.get("body"):
                return result  # {"subject": ..., "body": ...}

            print("[PIPELINE] JSON generation returned incomplete result, falling back to text generation")
            # Fall through to text-based generation with old prompt path

        # ── Fallback: deterministic 3-phase pipeline ───────────
        print("[PHASE 1] Extracting job requirements (deterministic)...")
        job_requirements = self._extract_job_requirements(
            internship_description,
            internship_title
        )
        print(f"[PHASE 1] ✓ Detected domain: {job_requirements['domain']}")

        print("\n[PHASE 2] Filtering resume for job-relevant content...")
        resume_match = self._filter_resume_by_job(resume_text, job_requirements)
        print(f"[PHASE 2] ✓ Found {len(resume_match['projects'])} relevant project(s)")
        print(f"[PHASE 2] ✓ Found {len(resume_match['technologies'])} matching technologies")

        if not resume_match['technologies']:
            print(f"[PHASE 2] ⚠ WARNING: No matching technologies found!")

        print("\n[PHASE 3] Generating email...")
        prompt = self._create_3phase_prompt(
            job_requirements,
            resume_match,
            company_name,
            internship_title
        )

        email_body = await self._generate_with_gemini(prompt)

        if not email_body:
            error_hint = f"Gemini API returned empty result. Check GEMINI_API_KEY validity, quota, and that the model '{self.gemini_model}' is accessible."
            print(f"\n[PIPELINE] ⚠️ {error_hint}")
            raise RuntimeError(error_hint)

        # Old-style subject generation for fallback path
        subject = await self.generate_subject_line(
            job_title=internship_title,
            company_name=company_name
        )

        print(f"\n[PIPELINE] Email generation complete (fallback path)")
        return {"subject": subject, "body": email_body}

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

    def _create_structured_prompt(
        self,
        extracted_data: Dict,
        internship_description: str,
        internship_title: str,
        company_name: str,
    ) -> str:
        """
        Generate a prompt that uses pre-extracted structured resume data
        (skills, projects, experience, achievements) instead of running
        the deterministic Phase 1 / Phase 2 parsing.

        The model sees the candidate's actual pre-parsed background and can
        write a much richer, more specific email.
        """
        skills = extracted_data.get("skills", [])
        projects = extracted_data.get("projects", [])
        experience = extracted_data.get("experience", [])
        achievements = extracted_data.get("achievements", [])

        # Format sections
        skills_block = "\n".join(f"  - {s}" for s in skills) if skills else "  (none listed)"
        projects_block = ""
        for p in projects:
            techs = ", ".join(p.get("tech_stack", []))
            projects_block += f"  - {p.get('name', '')}: {p.get('description', '')} [{techs}]\n"
        exp_block = ""
        for e in experience:
            highlights = "\n      • ".join(e.get("highlights", []))
            exp_block += f"  - {e.get('role', '')} @ {e.get('company', '')} ({e.get('duration', '')})\n      • {highlights}\n"
        ach_block = "\n".join(f"  - {a}" for a in achievements) if achievements else "  (none listed)"

        prompt = f"""GENERATION TASK: Write a professional internship cold email

## PRE-EXTRACTED RESUME DATA (ONLY DATA — DO NOT FABRICATE):

**Technical Skills:**
{skills_block}

**Projects:**
{projects_block}

**Experience:**
{exp_block}

**Achievements:**
{ach_block}

## JOB TARGET:
- Position: {internship_title}
- Company: {company_name}
- Description: {internship_description[:1000] if internship_description else 'N/A'}

## STRICT RULES:

1. **RESUME BOUNDARY**: You MUST ONLY reference the specific skills, projects, experience entries, and achievements listed above.  Do NOT fabricate details.
2. **PROJECT-FIRST**: At least 50% of the email must focus on ONE specific project from the Projects section.  Describe it concretely.
3. **ANTI-GENERIC**: Do NOT use "passionate", "highly motivated", "various projects", "multiple technologies", "several".
4. **LENGTH**: 140–180 words.
5. **CLOSING**: End with: "I've attached my resume below for more details on the project and related work."

## INSTRUCTIONS:

Write a concise, professional email that:
- Opens with a line showing you know what {company_name} does in the relevant space.
- Introduces yourself as someone who has built things relevant to this role.
- Devotes the core paragraph to ONE project from the list — describe what it does, the problem it solved, and the tech stack used.
- Connects the project to the role you're applying for.
- Closes with an offer to discuss further and the required closing line.

Write ONLY the email body (no subject, no signature):
"""
        return prompt

    def _create_3phase_prompt(
        self,
        job_requirements: Dict,
        resume_match: Dict,
        company_name: str,
        internship_title: str
    ) -> str:
        """
        PHASE 3: Create prompt using ONLY Phase 2 approved data
        
        This prompt enforces:
        - Project-first structure (50%+ on specific project)
        - Anti-generic rules
        - Resume boundary (can only use approved data)
        """
        
        domain = job_requirements['domain']
        work_type = job_requirements['work_type']
        technologies = resume_match['technologies']
        projects = resume_match['projects']
        
        # Build intro variant based on domain
        if "embedded" in domain:
            intro = "electronics/computer engineering student who builds firmware solutions"
        elif "ai" in domain.lower() or "machine learning" in domain:
            intro = "computer science student who builds AI/ML models"
        elif "data" in domain:
            intro = "data science student who builds analytical solutions"
        elif "backend" in domain:
            intro = "computer science student who builds backend systems"
        elif "frontend" in domain:
            intro = "computer science student who builds user interfaces"
        elif "full-stack" in domain:
            intro = "computer science student who builds full-stack applications"
        else:
            intro = "engineering student who builds software solutions"
        
        # Technology line (from Phase 2 ONLY)
        if len(technologies) >= 3:
            tech_line = f"{technologies[0]}, {technologies[1]}, and {technologies[2]}"
        elif len(technologies) == 2:
            tech_line = f"{technologies[0]} and {technologies[1]}"
        elif len(technologies) == 1:
            tech_line = technologies[0]
        else:
            tech_line = None  # Will signal no match
        
        # Project details (from Phase 2 ONLY)
        primary_project = projects[0] if projects else None
        
        # Build the STRICT prompt
        prompt = f"""GENERATION TASK: Write a professional internship cold email

## APPROVED DATA FROM PHASE 2 (USE ONLY THIS - NO OTHER DATA ALLOWED):

**Job Requirements:**
- Position: {internship_title}
- Company: {company_name}
- Domain: {domain}
- Work Type: {work_type}

**Resume-Matched Technologies (THESE ARE THE ONLY TECHNOLOGIES YOU MAY MENTION):**
{chr(10).join(f'- {tech}' for tech in technologies) if technologies else '- [No matching technologies found]'}

**Resume-Matched Projects (THESE ARE THE ONLY PROJECTS YOU MAY MENTION):**
"""
        
        if primary_project:
            prompt += f"""
- Name: {primary_project['name']}
- Context: {primary_project['context']}
"""
        else:
            prompt += "- [No matching projects found]\n"
        
        prompt += f"""

## STRICT GENERATION RULES:

1. **RESUME BOUNDARY (NON-NEGOTIABLE):**
   - You are FORBIDDEN from mentioning ANY technology not listed above
   - You are FORBIDDEN from mentioning ANY project not listed above
   - If the approved data is insufficient, you write a SHORT, HONEST email acknowledging the gap
   - You NEVER fabricate or hallucinate content

2. **PROJECT-FIRST STRUCTURE (50%+ of email):**
   - Opening: 1 line mentioning {company_name}'s work in {domain}
   - Intro: 1 line as "{intro}"
   - PROJECT SECTION (3-4 lines): MUST use approved project name and technologies
   - Connection: 1-2 lines linking project to {work_type}
   - CTA: 1 line offering to discuss
   - Closing: "I've attached my resume below for more details on the project and related work."

3. **ANTI-GENERIC ENFORCEMENT:**
   - FORBIDDEN PHRASES: "various projects", "multiple technologies", "passionate", "highly motivated", "dear hiring", "several"
   - Minimum length: 120 words
   - MUST mention at least ONE specific project name from approved list

4. **VALIDATION REQUIREMENTS:**
   - Every technology mentioned must be from the approved list above
   - Every project mentioned must be from the approved list above
   - Email must be 140-180 words
   - At least 50% must focus on the specific project

## EXAMPLE STRUCTURE (using ONLY approved data):

```
I've been following {company_name}'s work in {domain}.

I'm an {intro}.

One project I've spent significant time on is [APPROVED PROJECT NAME], [describe using APPROVED TECHNOLOGIES]. While building this, I worked extensively with [APPROVED TECH 1], [APPROVED TECH 2], and [APPROVED TECH 3]—skills that directly translate to the {work_type} your team focuses on.

Designing [PROJECT NAME] required balancing [relevant challenge for domain], something equally important when building production-grade {domain} solutions.

I'd be happy to walk through the project if helpful.

I've attached my resume below for more details on the project and related work.
```

## NOW GENERATE THE EMAIL:

Use ONLY the approved technologies and projects listed above. If no match exists, write: "I don't have directly relevant experience in {domain}, but I'm eager to learn." Do NOT fabricate details.

Write ONLY the email body (no subject, no signature):
"""
        
        return prompt
    
    def _validate_email(self, email: str, resume_match: Dict) -> Dict:
        """
        Validate email for contamination, hallucination, and generic content
        
        Returns:
            {"valid": bool, "reason": str}
        """
        if not email or len(email.strip()) == 0:
            return {
                "valid": False,
                "reason": "Empty email"
            }
        
        email_lower = email.lower()
        
        # Check 1: Minimum length (100 words - relaxed from 120)
        word_count = len(email.split())
        if word_count < 100:
            return {
                "valid": False,
                "reason": f"Too short ({word_count} words, minimum 100)"
            }
        
        # Check 2: Generic phrases (FORBIDDEN) - but only fail if multiple found
        forbidden_phrases = [
            "various projects",
            "multiple projects",
            "several projects",
            "many projects",
            "various technologies",
            "multiple technologies",
            "several technologies",
            "different technologies",
        ]
        
        found_forbidden = [phrase for phrase in forbidden_phrases if phrase in email_lower]
        if len(found_forbidden) >= 2:  # Allow 1, fail on 2+
            return {
                "valid": False,
                "reason": f"Contains too many generic phrases: {', '.join(found_forbidden)}"
            }
        
        # Check 3: Must mention approved project or have honest acknowledgment (relaxed)
        # Only check if we have projects - otherwise pass
        if resume_match['projects']:
            has_project_mention = False
            for project in resume_match['projects']:
                if project['name'].lower() in email_lower:
                    has_project_mention = True
                    break
            
            has_honest_ack = "don't have directly relevant" in email_lower or "no direct experience" in email_lower or "eager to learn" in email_lower
            
            # Also check if email mentions ANY capitalized project-like word
            words = email.split()
            has_capitalized_project = any(
                len(word) > 3 and word[0].isupper() and word.isalpha() 
                for word in words
            )
            
            if not has_project_mention and not has_honest_ack and not has_capitalized_project:
                return {
                    "valid": False,
                    "reason": "No specific project name mentioned despite approved projects available"
                }
        
        # Check 4: Must end with required closing (relaxed - check for variations)
        closing_variations = [
            "i've attached my resume",
            "i have attached my resume",
            "attached my resume",
            "resume below",
            "resume attached"
        ]
        
        has_closing = any(variation in email_lower for variation in closing_variations)
        if not has_closing:
            return {
                "valid": False,
                "reason": "Missing required closing line about resume"
            }
        
        # All checks passed
        return {"valid": True, "reason": "All validation passed"}
    
    async def _generate_with_gemini(self, prompt: str, retry_count: int = 0) -> Optional[str]:
        """Generate email using Gemini API with safety filter and rate limit handling"""
        model_name = self.gemini_model
        print(f"[GEMINI] Calling model={model_name} prompt_len={len(prompt)} retry={retry_count}")
        try:
            from google.genai import types
            import asyncio
            
            # Create generation config with relaxed safety
            config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=600,
                system_instruction=self.system_instruction,
                safety_settings=self.safety_settings
            )
            
            # Generate content using the new API
            response = self.genai_client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            
            # Check if response was blocked by safety filters
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Check finish reason for safety blocks
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = str(candidate.finish_reason)
                    if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                        print(f"[GEMINI] ⚠️ Content blocked by safety filters: {finish_reason}")
                        print("[GEMINI] Attempting simplified generation...")
                        
                        # Try with simplified, more neutral prompt
                        return await self._generate_with_gemini_simplified(prompt)
            
            print(f"[GEMINI] ✓ Response received finish_reason={candidate.finish_reason if hasattr(response, 'candidates') and response.candidates else 'unknown'}")
            
            # Check if response has text
            if response.text:
                email_text = response.text.strip()
                print(f"[GEMINI] ✓ Text generated: {len(email_text)} chars")
                return email_text
            else:
                print("[GEMINI] No text in response - attempting fallback")
                return await self._generate_with_gemini_simplified(prompt)
                
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for rate limit / quota exceeded
            if '429' in str(e) or 'quota' in error_msg or 'resource_exhausted' in error_msg or 'rate limit' in error_msg:
                print(f"[GEMINI] ⚠️ RATE LIMIT EXCEEDED")
                print(f"[GEMINI] Your Gemini API free tier quota is exhausted")
                print(f"[GEMINI] Error: {str(e)[:200]}...")
                
                # Extract retry delay if provided
                import re
                retry_match = re.search(r'retry in ([0-9.]+)s', str(e))
                if retry_match and retry_count < 2:
                    retry_delay = float(retry_match.group(1))
                    print(f"[GEMINI] Retrying in {retry_delay} seconds... (attempt {retry_count + 1}/2)")
                    import asyncio
                    await asyncio.sleep(retry_delay)
                    return await self._generate_with_gemini(prompt, retry_count + 1)
                else:
                    print(f"[GEMINI] ❌ Cannot retry - quota exhausted")
                    print(f"[GEMINI] Solutions:")
                    print(f"[GEMINI]   1. Wait for quota reset (usually daily)")
                    print(f"[GEMINI]   2. Upgrade Gemini API plan")
                    raise RuntimeError(f"Gemini quota exhausted: {str(e)[:300]}") from e
            
            # Check for safety filter blocks
            elif 'safety' in error_msg or 'blocked' in error_msg or 'filter' in error_msg:
                print(f"[GEMINI] ⚠️ Safety filter error: {e}")
                print("[GEMINI] Attempting simplified generation...")
                return await self._generate_with_gemini_simplified(prompt)
            
            # Other errors — preserve the actual API error message
            else:
                print(f"[GEMINI] API error: {e}")
                raise RuntimeError(f"Gemini API error: {str(e)}") from e
    
    async def _generate_with_gemini_simplified(self, original_prompt: str) -> Optional[str]:
        """
        Fallback generation with simplified prompt to avoid safety filters
        
        This version uses more neutral language and avoids words that might
        trigger safety filters (like "hiring", "job", etc.)
        """
        try:
            from google.genai import types
            
            # Extract key info from original prompt
            # Parse the approved data section
            lines = original_prompt.split('\n')
            company = "the company"
            position = "this role"
            domain = "technology"
            technologies = []
            project_name = None
            project_context = None
            
            for i, line in enumerate(lines):
                if "Company:" in line:
                    company = line.split("Company:")[-1].strip()
                if "Position:" in line:
                    position = line.split("Position:")[-1].strip()
                if "Domain:" in line:
                    domain = line.split("Domain:")[-1].strip()
                if "- Name:" in line and project_name is None:
                    project_name = line.split("Name:")[-1].strip()
                if "- Context:" in line and project_context is None:
                    project_context = line.split("Context:")[-1].strip()
                if line.strip().startswith("- ") and not any(x in line for x in ["Name:", "Context:", "[No"]):
                    tech = line.strip()[2:].strip()
                    if tech and len(tech) < 50:  # Reasonable tech name length
                        technologies.append(tech)
            
            # Build intro based on domain
            if "embedded" in domain.lower():
                intro = "an engineering student focused on firmware development"
            elif "ai" in domain.lower() or "machine learning" in domain.lower():
                intro = "a student who builds AI and machine learning systems"
            elif "backend" in domain.lower():
                intro = "a student who builds backend systems"
            elif "frontend" in domain.lower():
                intro = "a student who builds user interfaces"
            else:
                intro = "an engineering student who builds software"
            
            # Create simplified, neutral prompt
            simplified_prompt = f"""Write a brief professional introduction email for a student internship opportunity.

Context:
- Student is {intro}
- Writing to: {company}
- Opportunity area: {domain}

Student's relevant work:
"""
            
            if project_name and project_context:
                simplified_prompt += f"- Built a project called {project_name}: {project_context}\n"
            
            if technologies:
                tech_str = ", ".join(technologies[:3])
                simplified_prompt += f"- Technical skills: {tech_str}\n"
            
            simplified_prompt += """
Requirements:
1. Keep it professional and factual
2. Focus on the specific project mentioned
3. Mention how the technical skills relate to the opportunity
4. End with: "I've attached my resume below for more details on the project and related work."
5. Length: 140-160 words
6. Do NOT use generic phrases like "passionate" or "highly motivated"

Write only the email body (no subject line, no signature):"""
            
            # Use even more relaxed safety settings for fallback
            ultra_safe_settings = [
                types.SafetySetting(
                    category='HARM_CATEGORY_HATE_SPEECH',
                    threshold='OFF'
                ),
                types.SafetySetting(
                    category='HARM_CATEGORY_HARASSMENT',
                    threshold='OFF'
                ),
                types.SafetySetting(
                    category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                    threshold='OFF'
                ),
                types.SafetySetting(
                    category='HARM_CATEGORY_DANGEROUS_CONTENT',
                    threshold='OFF'
                ),
            ]
            
            config = types.GenerateContentConfig(
                temperature=0.6,  # Even lower temperature
                max_output_tokens=500,
                safety_settings=ultra_safe_settings
            )
            
            print(f"[GEMINI] Using simplified prompt with ultra-safe settings (prompt_len={len(simplified_prompt)})...")
            
            response = self.genai_client.models.generate_content(
                model=self.gemini_model,
                contents=simplified_prompt,
                config=config
            )
            
            if response.text:
                email_text = response.text.strip()
                print(f"[GEMINI] ✓ Simplified generation successful: {len(email_text)} chars")
                return email_text
            else:
                print("[GEMINI] Simplified generation also failed (empty response)")
                raise RuntimeError("Gemini simplified fallback also returned empty response")
                
        except RuntimeError:
            raise
        except Exception as e:
            print(f"[GEMINI] ❌ Simplified generation error: {e}")
            raise RuntimeError(f"Gemini simplified fallback failed: {str(e)}") from e
    
    async def generate_subject_line(self, job_title: str, company_name: str) -> str:
        """Generate a subject line following InternFlow project-first specification"""
        import random
        
        templates = [
            f"Built InternFlow — relevant to your team",
            f"Applying AI to {job_title.split()[0].lower()} problems",
            f"A project aligned with {company_name}",
            f"Built a tool for {job_title.split()[0].lower()}",
            f"Project relevant to your hiring focus",
            f"How I built an AI tool"
        ]
        
        return random.choice(templates)

    async def _generate_with_gemini_json(self, prompt: str) -> Optional[Dict]:
        """
        Generate a JSON response from Gemini using ``response_mime_type``.

        Uses a dedicated config with ``max_output_tokens=800`` and
        ``response_mime_type="application/json"`` so the model returns
        proper structured output that never gets cut off mid-sentence.
        """
        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=800,
            safety_settings=self.safety_settings,
            response_mime_type="application/json",
        )

        try:
            response = self.genai_client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=config,
            )

            text = response.text.strip() if response.text else ""
            if not text:
                print("[GEMINI_JSON] Empty response")
                return None

            import json, re
            match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            raw = json.loads(match.group(1) if match else text)

            subject = (raw.get("subject") or "").strip()
            body = (raw.get("body") or "").strip()

            if not subject or not body:
                print(f"[GEMINI_JSON] Incomplete: subject={bool(subject)} body={bool(body)}")
                return None

            print(f"[GEMINI_JSON] ✓ subject={len(subject)}ch body={len(body)}ch "
                  f"({len(body.split())} words)")
            return {"subject": subject, "body": body}

        except Exception as e:
            print(f"[GEMINI_JSON] ❌ Failed: {e}")
            return None

    # ── Structured Job Requirement Extraction ──────────────────────

    _JOB_EXTRACT_PROMPT = """You are a job description parser. Extract structured JSON from the job posting below.

Return ONLY valid JSON with exactly this structure — no markdown, no explanation:

{
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "core_responsibilities": ["responsibility1", "responsibility2", ...],
  "technologies_mentioned": ["tech1", "tech2", ...],
  "domain": "brief description of the domain or industry"
}

Rules:
- "required_skills" — explicitly stated must-haves (languages, frameworks, methodologies).
- "preferred_skills" — nice-to-haves, bonus points, or "plus" items.
- "core_responsibilities" — what the role actually does day-to-day (2-5 items).
- "technologies_mentioned" — any specific tools, platforms, libraries named anywhere.
- "domain" — one short phrase like "embedded firmware", "full-stack web", "AI/ML".
- If a section has no data, use an empty array [].

Job posting:
"""

    async def _extract_job_requirements_structured(self, job_description: str, job_title: str) -> Optional[Dict]:
        """
        Call Gemini once to extract structured requirements from a job posting.

        Returns a dict with ``required_skills``, ``preferred_skills``,
        ``core_responsibilities``, ``technologies_mentioned``, ``domain``,
        or ``None`` on failure.
        """
        combined = f"Title: {job_title}\n\nDescription:\n{job_description}"
        prompt = self._JOB_EXTRACT_PROMPT + "\n" + combined

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024,
                safety_settings=self.safety_settings,
            )

            response = self.genai_client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=config,
            )

            text = response.text.strip() if response.text else ""
            if not text:
                print("[JOB_EXTRACT] Gemini returned empty response — falling back to deterministic")
                return None

            import json, re
            match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            raw = match.group(1) if match else text
            data = json.loads(raw)

            validated = {
                "required_skills": data.get("required_skills", []),
                "preferred_skills": data.get("preferred_skills", []),
                "core_responsibilities": data.get("core_responsibilities", []),
                "technologies_mentioned": data.get("technologies_mentioned", []),
                "domain": data.get("domain", ""),
            }
            print(f"[JOB_EXTRACT] ✓ Domain={validated['domain']}, "
                  f"req_skills={len(validated['required_skills'])}, "
                  f"pref_skills={len(validated['preferred_skills'])}, "
                  f"resp={len(validated['core_responsibilities'])}, "
                  f"techs={len(validated['technologies_mentioned'])}")
            return validated

        except Exception as e:
            print(f"[JOB_EXTRACT] ❌ Failed: {e}")
            return None

    # ── Resume-to-Job Matching ──────────────────────────────────────

    def _match_resume_to_job(self, extracted_data: Dict, job_reqs: Dict) -> List[str]:
        """
        Compare structured resume data against job requirements and produce
        2–3 explicit match statements like:

          "candidate has a project 'Foo' using TypeScript & React,
           which matches the job's need for frontend development"

        Uses simple set overlap for skills/technologies first, then falls
        back to matching project descriptions and experience highlights
        against job responsibilities.
        """
        matches: List[str] = []
        seen_project_names: set = set()
        seen_exp_indices: set = set()

        skill_overlap = self._skill_overlap_statements(
            extracted_data.get("skills", []),
            job_reqs.get("required_skills", []) + job_reqs.get("preferred_skills", []),
            job_reqs.get("technologies_mentioned", []),
        )
        matches.extend(skill_overlap)

        project_matches = self._project_overlap_statements(
            extracted_data.get("projects", []),
            job_reqs.get("technologies_mentioned", []),
            job_reqs.get("core_responsibilities", []),
            seen_project_names,
        )
        matches.extend(project_matches)

        exp_matches = self._experience_overlap_statements(
            extracted_data.get("experience", []),
            job_reqs.get("core_responsibilities", []),
            job_reqs.get("technologies_mentioned", []),
            seen_exp_indices,
        )
        matches.extend(exp_matches)

        # Limit to 3 strongest — skill matches are always relevant, then
        # take up to 2 project/experience matches on top.
        result = matches[:3]

        if not result:
            result.append(
                f"candidate has a background in "
                f"{', '.join(extracted_data.get('skills', [])[:3]) or 'general engineering'} "
                f"and is eager to apply their learning to the {job_reqs.get('domain', 'role')}"
            )

        for i, m in enumerate(result):
            print(f"[MATCH] {i+1}. {m}")
        return result

    @staticmethod
    def _skill_overlap_statements(
        candidate_skills: List[str],
        all_job_skills: List[str],
        job_techs: List[str],
    ) -> List[str]:
        """Produce match statements from skill/tech set overlap."""
        if not candidate_skills or not all_job_skills:
            return []

        cs_lower = {s.strip().lower() for s in candidate_skills}
        js_lower = {s.strip().lower() for s in all_job_skills}
        techs_lower = {t.strip().lower() for t in job_techs}

        overlapping = cs_lower & js_lower
        overlapping_techs = cs_lower & techs_lower
        all_overlap = overlapping | overlapping_techs

        if not all_overlap:
            return []

        overlap_list = sorted(all_overlap)
        display = overlap_list[:5]
        display_str = display[0] if len(display) == 1 else (
            ", ".join(display[:-1]) + f" and {display[-1]}"
        )
        return [f"candidate has skills in {display_str}, which the job explicitly requires"]

    def _project_overlap_statements(
        self,
        projects: List[Dict],
        job_techs: List[str],
        job_resp: List[str],
        seen: set,
    ) -> List[str]:
        """Match projects against job technologies and responsibilities."""
        if not projects:
            return []

        techs_lower = {t.strip().lower() for t in job_techs}
        resp_lower_words = set()
        for r in job_resp:
            resp_lower_words.update(r.lower().split())

        statements = []
        for proj in projects:
            pname = proj.get("name", "")
            if not pname or pname.lower() in seen:
                continue

            proj_techs = [t.strip().lower() for t in (proj.get("tech_stack") or [])]
            proj_desc = (proj.get("description") or "").lower()

            # Tech overlap
            matching_techs = [t for t in proj_techs if t in techs_lower]
            # Responsibility keyword overlap in description
            desc_words = set(proj_desc.split())
            matching_resp_words = desc_words & resp_lower_words

            if matching_techs or matching_resp_words:
                tech_str = ", ".join(matching_techs[:3]) if matching_techs else ""
                pivot = (f"which uses {tech_str}, matching the job's tech requirements"
                         if matching_techs else
                         f"which involves {' '.join(list(matching_resp_words)[:3])}, "
                         f"matching a core responsibility")
                statements.append(
                    f"candidate has a project '{pname}' ({proj.get('description', '')[:100]}), "
                    f"{pivot}"
                )
                seen.add(pname.lower())

        return statements[:2]

    def _experience_overlap_statements(
        self,
        experience: List[Dict],
        job_resp: List[str],
        job_techs: List[str],
        seen: set,
    ) -> List[str]:
        """Match experience highlights against job responsibilities."""
        if not experience:
            return []

        techs_lower = {t.strip().lower() for t in job_techs}
        resp_lower_words = set()
        for r in job_resp:
            resp_lower_words.update(r.lower().split())

        statements = []
        for i, exp in enumerate(experience):
            if i in seen:
                continue

            highlights = [h.lower() for h in (exp.get("highlights") or [])]
            role = exp.get("role", "")
            company = exp.get("company", "")

            # Check if any highlight words overlap with responsibilities or techs
            matching_words = set()
            for h in highlights:
                h_words = set(h.split())
                matching_words.update(h_words & resp_lower_words)
                # Also check tech overlap inside highlights
                matching_words.update(h_words & techs_lower)

            if matching_words:
                top_words = list(matching_words)[:3]
                statements.append(
                    f"candidate's experience as {role} at {company} involved "
                    f"{' '.join(top_words)}, which maps to the job's "
                    f"requirement for {', '.join(job_resp[:2]).lower()}"
                )
                seen.add(i)

        return statements[:2]

    # ── Matched Prompt Builder ──────────────────────────────────────

    _STRUCTURED_PROMPT_CONFIG = {
        "temperature": 0.7,
        "max_output_tokens": 800,
        "safety_settings": None,  # set at call time
        "response_mime_type": "application/json",
    }

    def _create_matched_prompt(
        self,
        match_statements: List[str],
        job_reqs: Dict,
        internship_title: str,
        company_name: str,
        candidate_name: str = "",
    ) -> str:
        """
        Build the email-generation prompt that instructs Gemini to return
        **JSON** with ``subject`` and ``body`` fields.  The model receives
        only the explicit match statements — not raw resume text or full
        structured data.

        Rules are tighter than the old prompt: no "following your work"
        openers, body must be 100–130 words, and at least one match must
        be referenced by name.
        """
        matches_block = "\n".join(f"  • {m}" for m in match_statements)

        skills = ", ".join(job_reqs.get("required_skills", [])[:5]) or "N/A"
        resp = "\n".join(f"  • {r}" for r in job_reqs.get("core_responsibilities", []) or ["N/A"])
        domain = job_reqs.get("domain", "software development")

        prompt = f"""GENERATION TASK: Write a professional internship cold email.

Return ONLY valid JSON with exactly these two keys — no markdown, no explanation:

{{"subject": "the subject line here", "body": "the email body here"}}

## MATCHED DATA (THIS IS THE ONLY DATA YOU MAY USE):

The following explicit matches were found between the candidate's resume and the job requirements:

{matches_block}

## JOB TARGET:
- Position: {internship_title}
- Company: {company_name}
- Domain: {domain}
- Required Skills: {skills}
- Core Responsibilities:
{resp}

## CANDIDATE NAME (use this in the subject line):
{candidate_name or "the applicant"}

## STRICT RULES:

1. **MATCH BOUNDARY**: You MUST ONLY reference the content in the Matched Data section above.  Do NOT fabricate additional projects, skills, or experience.

2. **MANDATORY PROJECT/ACHIEVEMENT MENTION**: The body MUST reference at least ONE specific project name or achievement from the Matched Data section by its actual name.  A generic reference like "my project work" does not count.

3. **FORBIDDEN OPENERS**: Do NOT open with "I've been following your work in", "I'm excited to apply to", or "I've been tracking {company_name}'s growth".  Open directly with the candidate's relevant match.

4. **BODY LENGTH**: The body MUST be 100–130 words.  Be concise — every sentence should add a concrete detail.

5. **ANTI-GENERIC**: Forbidden phrases: "passionate", "highly motivated", "various projects", "multiple technologies", "several projects", "team player".

6. **SUBJECT LINE**: Concise, includes {candidate_name or "the applicant"} and {company_name}.  Do NOT use generic templates like "Application for {internship_title}".

## INSTRUCTIONS:

Write a tight, professional email where:
- Subject line is unique and mentions the candidate and company.
- First sentence immediately states the candidate's relevant match (project/experience/skill).
- Core paragraph (1–2 sentences) expands on ONE specific matched project or experience — describe it concretely.
- Final sentence connects the match to the role and offers to discuss further.
- No opening pleasantries, no "I've been following" language.

Return ONLY JSON with "subject" and "body" keys."""
        return prompt

    # ── Structured Resume Extraction ─────────────────────────────────

    _EXTRACT_PROMPT = """You are a resume parser. Extract structured JSON from the resume text below.

Return ONLY valid JSON with exactly this structure — no markdown, no explanation, no extra text:

{
  "skills": ["skill1", "skill2", ...],
  "projects": [
    {
      "name": "Project Name",
      "description": "Brief description of the project",
      "tech_stack": ["tech1", "tech2", ...]
    }
  ],
  "experience": [
    {
      "role": "Job Title",
      "company": "Company Name",
      "duration": "Start – End",
      "highlights": ["Key achievement or responsibility", "Another highlight"]
    }
  ],
  "achievements": ["Certification or award", "Notable metric or result"]
}

Rules:
- If a section has no data, use an empty array [].
- For "skills", list individual technical skills — programming languages, frameworks, tools, platforms.
- For "projects", include name, a 1-sentence description of what it does, and the key technologies used.
- For "experience", include role, company, duration string, and 2–3 concise highlights.
- For "achievements", include certifications, competition wins, notable metrics, or awards.
- Keep descriptions concise.  Do not fabricate.

Resume text:
"""

    async def extract_structured_resume(self, resume_text: str) -> Optional[Dict]:
        """
        Call Gemini once to parse resume text into structured JSON.

        Returns a dict with keys ``skills``, ``projects``, ``experience``,
        ``achievements``, or ``None`` on failure.
        """
        prompt = self._EXTRACT_PROMPT + "\n" + resume_text

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=2048,
                safety_settings=self.safety_settings,
            )

            response = self.genai_client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=config,
            )

            text = response.text.strip() if response.text else ""
            if not text:
                print("[EXTRACT] Gemini returned empty response")
                return None

            # Strip markdown fences if present
            import json
            import re
            match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
            raw = match.group(1) if match else text

            data = json.loads(raw)

            # Validate shape
            validated = {
                "skills": data.get("skills", []),
                "projects": data.get("projects", []),
                "experience": data.get("experience", []),
                "achievements": data.get("achievements", []),
            }
            print(f"[EXTRACT] ✓ Parsed: {len(validated['skills'])} skills, "
                  f"{len(validated['projects'])} projects, "
                  f"{len(validated['experience'])} experience entries, "
                  f"{len(validated['achievements'])} achievements")
            return validated

        except Exception as e:
            print(f"[EXTRACT] ❌ Failed: {e}")
            return None


# Singleton instance
llm_service = LLMService()
