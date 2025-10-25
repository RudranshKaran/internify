import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Testing gemini-2.5-flash model...")
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    test_prompt = """Generate a short professional email for an internship application.
    
Company: Google
Position: Software Engineering Intern
Keep it under 100 words."""
    
    print("\nGenerating content...")
    response = model.generate_content(test_prompt)
    
    print("\n✓ SUCCESS! Generated email:")
    print("-" * 50)
    print(response.text)
    print("-" * 50)
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
