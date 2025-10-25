import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Testing different prompts to find the issue...")

model = genai.GenerativeModel('gemini-2.5-flash')

# Test 1: Very simple prompt
print("\n1. Testing simple prompt:")
try:
    response = model.generate_content("Write a short professional email greeting.")
    print(f"✓ Success! Response: {response.text[:100]}")
except Exception as e:
    print(f"✗ Failed: {str(e)[:100]}")

# Test 2: Job application context
print("\n2. Testing job application:")
try:
    response = model.generate_content("Write a brief email expressing interest in a software internship at a tech company.")
    print(f"✓ Success! Response: {response.text[:100]}")
except Exception as e:
    print(f"✗ Failed: {str(e)[:100]}")

# Test 3: With more context
print("\n3. Testing with resume context:")
try:
    prompt = """Write a professional email for a student applying to an internship.
    
Student background: Computer Science major with Python experience
Position: Software Engineer Intern at TechCorp
Keep it brief and professional."""
    response = model.generate_content(prompt)
    print(f"✓ Success! Response: {response.text[:100]}")
except Exception as e:
    print(f"✗ Failed: {str(e)[:100]}")

# Test 4: Check what's actually in the response when it fails
print("\n4. Detailed response inspection:")
try:
    response = model.generate_content("Write an internship application email.")
    print(f"Candidates: {len(response.candidates)}")
    if response.candidates:
        candidate = response.candidates[0]
        print(f"Finish reason: {candidate.finish_reason}")
        print(f"Safety ratings: {candidate.safety_ratings}")
        if candidate.content and candidate.content.parts:
            print(f"Has parts: {len(candidate.content.parts)}")
            print(f"✓ Text: {response.text[:100]}")
        else:
            print(f"✗ No content parts")
except Exception as e:
    print(f"✗ Failed: {str(e)[:150]}")
