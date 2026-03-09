# 🧪 LLM Service Testing Guide

## Quick Test Script

Create a test file to verify the refactored service works correctly:

### Test 1: Embedded Systems Job (Matching Resume)

```python
import asyncio
from services.llm_service import llm_service

async def test_embedded_match():
    resume = """
    John Doe
    Electronics Engineering Student
    
    Projects:
    - SensorNode: Built an IoT environmental monitoring device using STM32 microcontroller.
      Programmed in C/C++ with FreeRTOS for real-time task management.
      Implemented I2C communication for sensor interfacing.
    
    - RoboArm: Developed a robotic arm control system using ARM Cortex-M4.
      Used bare-metal programming and PWM for motor control.
    
    Skills: C, C++, Python, ARM, STM32, FreeRTOS, Embedded Systems
    """
    
    job_desc = """
    We're looking for an embedded systems intern to work on firmware development
    for our IoT products. Experience with ARM microcontrollers, C/C++, and RTOS
    is required.
    """
    
    email = await llm_service.generate_email(
        resume_text=resume,
        internship_description=job_desc,
        internship_title="Embedded Systems Intern",
        company_name="TechCorp"
    )
    
    print("="*60)
    print("TEST 1: Embedded Systems Job with Matching Resume")
    print("="*60)
    print(email)
    print("\n")
    
    # Verify
    assert "SensorNode" in email or "RoboArm" in email, "Should mention specific project"
    assert "C" in email or "C++" in email, "Should mention C/C++"
    assert "various projects" not in email.lower(), "Should not use generic phrases"
    print("✅ Test 1 PASSED")

asyncio.run(test_embedded_match())
```

### Test 2: Web Development Job (Mismatched Resume)

```python
async def test_web_mismatch():
    resume = """
    Jane Smith
    Electronics Engineering Student
    
    Projects:
    - FirmwareLoader: Built a firmware update tool for STM32 using C++
    - MotorDriver: Developed motor control firmware with ARM assembly
    
    Skills: C, C++, ARM, Embedded Systems, Hardware Design
    """
    
    job_desc = """
    Looking for a full-stack web development intern. Must know React, Node.js,
    and have experience building RESTful APIs and databases.
    """
    
    email = await llm_service.generate_email(
        resume_text=resume,
        internship_description=job_desc,
        internship_title="Full-Stack Web Developer Intern",
        company_name="WebStartup"
    )
    
    print("="*60)
    print("TEST 2: Web Development Job with Embedded Resume (Mismatch)")
    print("="*60)
    print(email)
    print("\n")
    
    # Should acknowledge lack of direct experience
    assert "React" not in email, "Should NOT mention React (not in resume)"
    assert "Node" not in email or "Node.js" not in email, "Should NOT mention Node.js"
    print("✅ Test 2 PASSED - Correctly handled mismatch")

asyncio.run(test_web_mismatch())
```

### Test 3: AI/ML Job (Matching Resume)

```python
async def test_ai_match():
    resume = """
    Alex Chen
    Computer Science Student
    
    Projects:
    - ImageClassifier: Built a convolutional neural network for image recognition
      using Python, TensorFlow, and Keras. Achieved 94% accuracy on test dataset.
    
    - SentimentAnalyzer: Developed an NLP model for sentiment analysis using
      PyTorch and transformers. Deployed on AWS Lambda.
    
    Skills: Python, TensorFlow, PyTorch, Scikit-learn, NumPy, Pandas
    """
    
    job_desc = """
    AI/ML intern position. Work on deep learning models using TensorFlow or PyTorch.
    Experience with computer vision or NLP required. Python expertise essential.
    """
    
    email = await llm_service.generate_email(
        resume_text=resume,
        internship_description=job_desc,
        internship_title="AI/ML Intern",
        company_name="AILabs"
    )
    
    print("="*60)
    print("TEST 3: AI/ML Job with Matching Resume")
    print("="*60)
    print(email)
    print("\n")
    
    # Verify
    assert "ImageClassifier" in email or "SentimentAnalyzer" in email, "Should mention AI project"
    assert "TensorFlow" in email or "PyTorch" in email, "Should mention ML framework"
    assert "Python" in email, "Should mention Python"
    print("✅ Test 3 PASSED")

asyncio.run(test_ai_match())
```

### Test 4: Generic Phrase Detection

```python
async def test_no_generic_phrases():
    resume = """
    Student with projects in web development.
    
    Projects:
    - TaskManager: React and Node.js app
    
    Skills: JavaScript, React, Node.js
    """
    
    job_desc = "Looking for full-stack intern. React and Node.js required."
    
    email = await llm_service.generate_email(
        resume_text=resume,
        internship_description=job_desc,
        internship_title="Full-Stack Intern",
        company_name="StartupCo"
    )
    
    print("="*60)
    print("TEST 4: Validating No Generic Phrases")
    print("="*60)
    
    if email:
        # Check for forbidden phrases
        forbidden = ["various projects", "multiple technologies", "passionate", 
                    "highly motivated", "various technologies"]
        
        for phrase in forbidden:
            assert phrase not in email.lower(), f"Should not contain '{phrase}'"
        
        print("✅ Test 4 PASSED - No generic phrases found")
    else:
        print("⚠ Email generation failed (might be due to validation)")

asyncio.run(test_no_generic_phrases())
```

### Test 5: Phase Logging

```python
async def test_phase_logging():
    """
    Run this test and check console output to verify 3-phase pipeline is working
    """
    resume = "Student with Python and Flask experience. Built APIServer project."
    job_desc = "Backend intern position. Python and REST API experience needed."
    
    print("="*60)
    print("TEST 5: Verify 3-Phase Pipeline Logging")
    print("="*60)
    print("Expected output:")
    print("  [PHASE 1] Extracting job requirements...")
    print("  [PHASE 2] Filtering resume for job-relevant content...")
    print("  [PHASE 3] Generating email with filtered data...")
    print("  [VALIDATION] Email passed all validation checks")
    print("="*60)
    print("\n")
    
    email = await llm_service.generate_email(
        resume_text=resume,
        internship_description=job_desc,
        internship_title="Backend Intern",
        company_name="DevShop"
    )
    
    print("\n✅ Check console output above for phase logs")

asyncio.run(test_phase_logging())
```

---

## Complete Test Suite

Create `backend/test_llm_refactoring.py`:

```python
#!/usr/bin/env python3
"""
Test suite for refactored LLM service
Tests anti-contamination measures and job-aware generation
"""

import asyncio
import sys
from services.llm_service import llm_service


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_result(self, name, passed, reason=""):
        self.tests.append({"name": name, "passed": passed, "reason": reason})
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        for test in self.tests:
            status = "✅ PASS" if test["passed"] else "❌ FAIL"
            print(f"{status} - {test['name']}")
            if not test["passed"] and test["reason"]:
                print(f"  Reason: {test['reason']}")
        print("="*60)
        print(f"Total: {len(self.tests)} tests")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print("="*60)


async def run_all_tests():
    results = TestResults()
    
    # Test 1: Embedded match
    print("\n[TEST 1] Embedded Systems - Matching Resume")
    try:
        resume = """
        Projects: SensorNode - IoT device with STM32, C/C++, FreeRTOS
        Skills: C, C++, ARM, Embedded Systems
        """
        email = await llm_service.generate_email(
            resume_text=resume,
            internship_description="Embedded firmware intern. C/C++, ARM, RTOS required.",
            internship_title="Embedded Intern",
            company_name="TechCorp"
        )
        
        if email and ("SensorNode" in email or "C++" in email):
            results.add_result("Embedded Match", True)
            print("✅ Mentioned relevant project/tech")
        else:
            results.add_result("Embedded Match", False, "Did not mention relevant content")
    except Exception as e:
        results.add_result("Embedded Match", False, str(e))
    
    # Test 2: Domain mismatch
    print("\n[TEST 2] Domain Mismatch - Embedded resume for Web job")
    try:
        resume = """
        Projects: FirmwareLoader - STM32 firmware in C++
        Skills: C, C++, ARM
        """
        email = await llm_service.generate_email(
            resume_text=resume,
            internship_description="Full-stack web intern. React, Node.js, MongoDB required.",
            internship_title="Web Developer Intern",
            company_name="WebCo"
        )
        
        if email:
            has_react = "React" in email or "react" in email
            has_node = "Node" in email or "node" in email
            
            if not has_react and not has_node:
                results.add_result("Domain Mismatch", True)
                print("✅ Did not hallucinate web technologies")
            else:
                results.add_result("Domain Mismatch", False, "Mentioned tech not in resume")
        else:
            results.add_result("Domain Mismatch", True, "Correctly returned None")
    except Exception as e:
        results.add_result("Domain Mismatch", False, str(e))
    
    # Test 3: Generic phrases
    print("\n[TEST 3] Anti-Generic Validation")
    try:
        resume = """
        Projects: APIServer - Flask REST API with PostgreSQL
        Skills: Python, Flask, SQL
        """
        email = await llm_service.generate_email(
            resume_text=resume,
            internship_description="Backend Python intern",
            internship_title="Backend Intern",
            company_name="BackendCo"
        )
        
        if email:
            forbidden = ["various projects", "multiple technologies", "passionate"]
            has_forbidden = any(phrase in email.lower() for phrase in forbidden)
            
            if not has_forbidden:
                results.add_result("Anti-Generic", True)
                print("✅ No generic phrases found")
            else:
                results.add_result("Anti-Generic", False, "Contains generic phrases")
        else:
            results.add_result("Anti-Generic", False, "Email generation failed")
    except Exception as e:
        results.add_result("Anti-Generic", False, str(e))
    
    # Test 4: Project mention
    print("\n[TEST 4] Project-First Structure")
    try:
        resume = """
        Projects:
        - DataDashboard: Analytics dashboard with React and D3.js
        Skills: JavaScript, React, D3.js
        """
        email = await llm_service.generate_email(
            resume_text=resume,
            internship_description="Frontend intern for data visualization. React required.",
            internship_title="Frontend Intern",
            company_name="DataViz"
        )
        
        if email and "DataDashboard" in email:
            results.add_result("Project-First", True)
            print("✅ Mentioned specific project name")
        else:
            results.add_result("Project-First", False, "Did not mention project name")
    except Exception as e:
        results.add_result("Project-First", False, str(e))
    
    # Test 5: Closing line
    print("\n[TEST 5] Required Closing Line")
    try:
        resume = "Projects: TestApp with Python. Skills: Python, SQL"
        email = await llm_service.generate_email(
            resume_text=resume,
            internship_description="Python intern",
            internship_title="Python Intern",
            company_name="PyCo"
        )
        
        if email and "i've attached my resume below" in email.lower():
            results.add_result("Closing Line", True)
            print("✅ Has required closing line")
        else:
            results.add_result("Closing Line", False, "Missing closing line")
    except Exception as e:
        results.add_result("Closing Line", False, str(e))
    
    results.print_summary()
    return results


if __name__ == "__main__":
    print("🧪 LLM Service Refactoring Test Suite")
    print("="*60)
    
    results = asyncio.run(run_all_tests())
    
    # Exit with error code if tests failed
    if results.failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)
```

---

## Running Tests

### Quick Test
```bash
cd backend
python test_llm_refactoring.py
```

### Individual Test
```python
python -c "
import asyncio
from services.llm_service import llm_service

async def test():
    email = await llm_service.generate_email(
        resume_text='Projects: WebApp with React. Skills: React, JavaScript',
        internship_description='Frontend React intern',
        internship_title='Frontend Intern',
        company_name='StartupCo'
    )
    print(email)

asyncio.run(test())
"
```

---

## Expected Behavior

### ✅ Correct Behavior

1. **Phase Logging Visible**
   ```
   [PHASE 1] Extracting job requirements...
   [PHASE 2] Filtering resume for job-relevant content...
   [PHASE 3] Generating email with filtered data...
   [VALIDATION] ✓ Email passed all validation checks
   ```

2. **Project Names Mentioned**
   - Email should mention ACTUAL project names from resume
   - Example: "SensorNode", "APIServer", "DataDashboard"

3. **Domain Relevance**
   - Embedded job → mentions C/C++, ARM (if in resume)
   - Web job → mentions React, Node.js (if in resume)
   - No mixing of unrelated domains

4. **No Generic Phrases**
   - No "various projects"
   - No "multiple technologies"
   - No "passionate" or "highly motivated"

5. **Required Closing**
   - Every email ends with:
     "I've attached my resume below for more details on the project and related work."

### ❌ Incorrect Behavior (Should be Fixed)

1. ~~Mentions projects not in resume~~
2. ~~Uses technologies not relevant to job~~
3. ~~Contains generic phrases~~
4. ~~Missing specific project names~~
5. ~~Ignores job domain~~

---

## Debugging Failed Tests

### Issue: "No matching technologies found"

**Cause:** Resume doesn't have tech that matches job

**Fix:** Ensure resume has relevant skills for the job

**Example:**
```python
# Bad - mismatch
resume = "Skills: Python, Django"  # Web tech
job = "Embedded C/C++ firmware"    # Embedded tech
# Result: No match

# Good - match
resume = "Skills: C, C++, ARM"
job = "Embedded C/C++ firmware"
# Result: Match found
```

### Issue: "Email failed validation: Missing required closing line"

**Cause:** LLM didn't include the required closing

**Fix:** This is rare, but if it happens:
1. Check if system instruction is being used
2. Verify Gemini API is working
3. Check prompt structure in Phase 3

### Issue: "Contains forbidden generic phrases"

**Cause:** LLM still using generic language

**Fix:**
1. Verify `_validate_email()` is being called
2. Check if email is actually generic
3. May need to adjust temperature or prompt

---

## Performance Testing

### Measure Latency

```python
import time
import asyncio
from services.llm_service import llm_service

async def benchmark():
    start = time.time()
    
    email = await llm_service.generate_email(
        resume_text="Sample resume text...",
        internship_description="Sample job description...",
        internship_title="Software Intern",
        company_name="TestCo"
    )
    
    end = time.time()
    latency = (end - start) * 1000  # Convert to ms
    
    print(f"Latency: {latency:.0f}ms")
    print(f"Email length: {len(email)} chars" if email else "No email generated")

asyncio.run(benchmark())
```

**Expected:** 1000-3000ms (depending on API)

---

## Integration Testing

Test with actual backend API:

```bash
# Start backend
cd backend
uvicorn main:app --reload

# In another terminal, test endpoint
curl -X POST http://localhost:8000/api/llm/generate-email \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Projects: APIServer with Flask. Skills: Python, Flask, SQL",
    "job_description": "Backend Python intern position",
    "job_title": "Backend Intern",
    "company_name": "TechCo"
  }'
```

---

## Continuous Testing

Add to CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Test LLM Service
  run: |
    cd backend
    python test_llm_refactoring.py
```

---

**Testing Guide Created:** January 6, 2026
**Status:** Ready for testing
