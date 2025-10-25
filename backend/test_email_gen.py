import os
import asyncio
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import llm_service

load_dotenv()

async def test_email_generation():
    print("Testing email generation with new configuration...\n")
    
    resume_text = """RUDRANSH KARAN
Computer Science student with hands-on experience in Generative AI and backend development using Python.
Experience with LLMs, LangChain, and CrewAI."""
    
    internship_description = """AI Agents & Tools Development Intern
Work on AI agents, LLM frameworks, and intelligent systems."""
    
    internship_title = "AI Development Intern"
    company_name = "Tech Company"
    
    result = await llm_service.generate_email(
        resume_text=resume_text,
        internship_description=internship_description,
        internship_title=internship_title,
        company_name=company_name
    )
    
    if result:
        print("✓ SUCCESS! Generated email:")
        print("-" * 60)
        print(result)
        print("-" * 60)
    else:
        print("✗ FAILED: Could not generate email")

if __name__ == "__main__":
    asyncio.run(test_email_generation())
