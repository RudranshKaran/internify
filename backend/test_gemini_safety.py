import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Configure safety settings
safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

print("Testing gemini-2.5-flash with safety settings...")

model = genai.GenerativeModel('gemini-2.5-flash', safety_settings=safety_settings)

test_prompt = """You are a professional email writer helping a student apply for an internship.

Generate a concise, personalized cold email for an internship application.

**Internship Details:**
- Position: AI Engineer Intern
- Company: Google AI
- Internship Description: Working on machine learning models and AI systems

**Candidate Resume Summary:**
Computer Science student with experience in Python, TensorFlow, and machine learning projects.

**Requirements:**
1. Professional yet friendly tone suitable for students
2. 100-150 words maximum
3. Include greeting and relevant skills
4. Clear call-to-action

Generate ONLY the email body text, nothing else."""

print("\nGenerating email...")
try:
    response = model.generate_content(
        test_prompt,
        generation_config={'temperature': 0.7, 'max_output_tokens': 500}
    )
    
    print(f"\nFinish reason: {response.candidates[0].finish_reason}")
    print(f"Safety ratings: {response.candidates[0].safety_ratings}")
    
    if response.text:
        print("\n✓ SUCCESS! Generated email:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
    else:
        print("\n✗ No text in response")
        
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
