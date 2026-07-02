"""
Check Gemini API Usage and Quota

This script analyzes how many API calls are made per email generation
and provides recommendations for reducing API load.
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("GEMINI API USAGE ANALYSIS")
print("=" * 80)

# Check if key is configured
gemini_key = os.getenv("GEMINI_API_KEY")

print("\n📊 Current Configuration:")
print(f"   Gemini API Key: {'✓ Configured' if gemini_key else '✗ Not configured'}")

if gemini_key:
    print(f"   Gemini Key (partial): {gemini_key[:10]}...{gemini_key[-6:]}")

print("\n" + "=" * 80)
print("API CALLS PER EMAIL GENERATION")
print("=" * 80)

print("""
📈 Normal Flow (Success):
   1. _generate_with_gemini() → 1 API call
   ────────────────────────────────────────
   Total: 1 API call ✓

🔄 Safety Filter Fallback:
   1. _generate_with_gemini() → 1 API call (blocked)
   2. _generate_with_gemini_simplified() → 1 API call (retry)
   ────────────────────────────────────────
   Total: 2 API calls

⚠️ Rate Limit with Retry:
   1. _generate_with_gemini() → 1 API call (429 error)
   2. Sleep + retry → 1 API call (retry attempt 1)
   3. Sleep + retry → 1 API call (retry attempt 2)
   ────────────────────────────────────────
   Total: Up to 3 API calls (if all retries fail)

💥 Worst Case (Rate Limit → Retry → Safety Filter):
   1. _generate_with_gemini() → 1 API call (429, retries exhausted)
   2. _generate_with_gemini_simplified() → 1 API call (fallback)
   ────────────────────────────────────────
   Total: 2 API calls
""")

print("=" * 80)
print("GEMINI FREE TIER LIMITS")
print("=" * 80)

print("""
Gemini 2.0 Flash Experimental FREE Tier:
   • Requests per minute: 10 RPM
   • Requests per day: 1,500 RPD
   • Tokens per minute: 1,000,000 TPM

Your Current Usage Pattern:
   • Average tokens per email: ~2,000-3,000 tokens
     (prompt ~1,500 + response ~800)
   
   • Emails per request: 1 email
   • API calls per email: 1-2 calls (avg 1.2)
   
Estimated Capacity:
   ✓ You can generate ~1,250 emails/day (at 1.2 calls each)
   ✓ You can generate ~8-10 emails/minute
""")

print("=" * 80)
print("WHY YOUR QUOTA IS EXHAUSTING QUICKLY")
print("=" * 80)

print("""
🔍 Possible Reasons:

1. ⚡ RAPID REPEATED TESTING
   - Testing same email generation multiple times
   - Frontend auto-retry on failure
   - Multiple users or browser tabs hitting the API
   
2. 🔄 SAFETY FILTER TRIGGER RATE
   - Every safety filter block = 2 API calls (original + fallback)
   - If 50% of emails trigger safety filters → 1.5 calls/email average
   
3. 📉 VALIDATION FAILURES NOT LOGGED
   - Emails might be regenerating internally without your knowledge
   - Check backend logs for validation failure messages
   
4. 🌐 EXTERNAL USAGE
   - API key might be used elsewhere
   - Check Google AI Studio for usage dashboard
   
5. 🐛 BUG: Infinite Retry Loop
   - Rate limit retry logic might cause cascading retries
   - Max 2 retries enforced, but check logs for confirmation
""")

print("=" * 80)
print("IMMEDIATE ACTIONS TO REDUCE LOAD")
print("=" * 80)

print("""
🚀 Quick Wins:

1. REDUCE RETRY ATTEMPTS:
   • Current: max 2 retries on rate limit
   • Reduce to: max 1 retry (or 0)
   • Edit llm_service.py: retry_count < 1
   
2. DISABLE SAFETY FILTER FALLBACK:
   • Remove simplified generation fallback
   • Fail fast instead of retrying with different prompt
   • Reduces 2-call pattern to 1-call pattern
   
3. ADD RATE LIMITING ON FRONTEND:
   • Debounce email generation button (2-3 sec delay)
   • Disable button after click until response
   • Show "Generating..." state to prevent double-clicks
   
4. CACHE EMAIL GENERATIONS:
   • Cache generated emails by (resume_id + internship_id)
   • Return cached email if same job + resume combo
   • Reduces duplicate generations
""")

print("=" * 80)
print("CHECK YOUR API USAGE")
print("=" * 80)

print("""
📊 View your actual usage:
   1. Go to: https://aistudio.google.com/apikey
   2. Click on your API key
   3. View "Quota" and "Usage" tabs
   4. Check when your quota resets

🔬 Monitor backend logs:
   • Watch for "[GEMINI] ⚠️ RATE LIMIT EXCEEDED"
   • Count how many emails trigger safety fallback
   • Look for retry patterns
""")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)

if gemini_key:
    print("\n✅ Gemini API key is configured.")
    print("   Check Google AI Studio for your current quota usage.")
else:
    print("\n⚠️ NO GEMINI API KEY DETECTED!")
    print("   Solution: Get a Gemini API key:")
    print("   1. Visit: https://aistudio.google.com/apikey")
    print("   2. Sign up (free)")
    print("   3. Generate API key")
    print("   4. Add to .env: GEMINI_API_KEY=your_key_here")
    print("   5. Restart backend")

print("\n" + "=" * 80)
input("Press Enter to exit...")
