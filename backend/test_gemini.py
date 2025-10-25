import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No GEMINI_API_KEY found in .env")
    exit(1)

print(f"API Key found: {api_key[:10]}...")

genai.configure(api_key=api_key)

print("\nListing available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
            print(f"    Display name: {m.display_name}")
            print(f"    Description: {m.description[:100]}...")
            print()
except Exception as e:
    print(f"Error listing models: {e}")
    import traceback
    traceback.print_exc()

# Try to initialize with different model names
print("\nTesting model initialization:")
test_models = [
    'gemini-1.5-pro',
    'gemini-1.5-flash',
    'gemini-pro',
    'models/gemini-1.5-pro',
    'models/gemini-1.5-flash',
    'models/gemini-pro'
]

for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        print(f"✓ {model_name} - SUCCESS")
        
        # Try a simple generation
        response = model.generate_content("Say hello")
        print(f"  Test generation: {response.text[:50]}")
        break
    except Exception as e:
        print(f"✗ {model_name} - FAILED: {str(e)[:100]}")
