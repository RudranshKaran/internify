# Internify Terminology Update Summary

## Changes Required: JOB → INTERNSHIP

This document summarizes all the changes needed to update the codebase from "job" terminology to "internship" terminology since this is a platform for finding internships, not general jobs.

---

## Files Requiring Changes

### 1. Backend - Models
- ✅ **backend/models/job.py** → **internship.py** (RENAMED)
  - `JobBase` → `InternshipBase`
  - `JobCreate` → `InternshipCreate`
  - `JobResponse` → `InternshipResponse`
  - `JobSearchQuery` → `InternshipSearchQuery`

- ✅ **backend/models/__init__.py** - Update imports and exports

- **backend/models/email.py**
  - `job_id` → `internship_id`
  - `job_description` → `internship_description`
  - `job_title` → `internship_title`

###  2. Backend - Routes
- ✅ **backend/routes/jobs.py** → **internships.py** (RENAMED)
  - `/jobs/search` → `/internships/search`
  - `/jobs/{id}` → `/internships/{id}`
  - Update all function names and documentation

- **backend/routes/__init__.py** - Update imports
- **backend/routes/llm.py** - Update parameter names
- **backend/main.py** - Update router imports

### 3. Backend - Services
- **backend/services/supabase_service.py**
  - `save_job()` → `save_internship()`
  - `get_job_by_id()` → `get_internship_by_id()`
  - Table references: `jobs` → `internships`

- **backend/services/scraper_service.py**
  - `search_linkedin_jobs()` → `search_internships()`
  - `get_job_details()` → `get_internship_details()`
  - Update all variable names and comments

### 4. Database
- **database_schema.sql**
  - `jobs` table → `internships` table
  - All foreign key references
  - Policies and indexes

- **supabase_complete_setup.sql**
  - Same as above

### 5. Frontend - Components
- **frontend/components/JobCard.tsx** → **InternshipCard.tsx** (RENAME)
  - `JobCardProps` → `InternshipCardProps`
  - `job` prop → `internship` prop

### 6. Frontend - API
- **frontend/lib/api.ts**
  - `jobsAPI` → `internshipsAPI`
  - `/jobs/search` → `/internships/search`
  - All type references

### 7. Frontend - Pages
- **frontend/app/dashboard/page.tsx**
  - `jobs` state → `internships`
  - `selectedJob` → `selectedInternship`
  - `handleJobSelect` → `handleInternshipSelect`
  - All UI text

- **frontend/app/email-preview/page.tsx**
  - `job` state → `internship`
  - localStorage keys
  - Parameter names

- **frontend/app/history/page.tsx**
  - Update display text

### 8. Documentation
- Update all .md files to use internship terminology
- Update API examples
- Update architecture diagrams

---

## User-Facing Text Changes

### Dashboard
- "Search for Jobs" → "Search for Internships"
- "Job Search Section" → "Internship Search"
- "Select a Job" → "Select an Internship"
- "Job Selected" → "Internship Selected"
- "No jobs found" → "No internships found"
- "Found X jobs" → "Found X internships"
- "Searching for jobs..." → "Searching for internships..."

### Email Preview
- "No job selected" → "No internship selected"
- job_description → internship_description
- job_title → internship_title

### History
- "Job Search History" → "Internship Search History"
- "job postings" → "internship postings"

### Privacy & Terms
- "job listings" → "internship listings"
- "job application" → "internship application"

---

## Implementation Strategy

Due to the extensive nature of these changes and risk of breaking the application, I recommend:

1. **Test Current State** - Ensure everything works before changes
2. **Create Git Branch** - `git checkout -b feature/job-to-internship-rename`
3. **Backend First** - Update models, routes, services
4. **Database Second** - Update table names (with migration)
5. **Frontend Third** - Update components, API, pages
6. **Documentation Last** - Update all .md files
7. **Full Testing** - Test entire workflow
8. **Deploy** - Merge to main after successful testing

---

## Risk Assessment

**HIGH RISK AREAS:**
- Database table rename (affects all existing data)
- API endpoint changes (breaks frontend immediately)
- localStorage keys (user session data)

**MITIGATION:**
- Use database migrations for table rename
- Update frontend and backend together
- Clear localStorage during deployment

---

## Estimated Time
- Backend Updates: 30-45 minutes
- Frontend Updates: 30-45 minutes
- Database Migration: 15-30 minutes
- Documentation: 15-20 minutes
- Testing: 30-45 minutes

**Total: 2-3 hours**

---

## Status: IN PROGRESS

✅ backend/models/job.py → internship.py (RENAMED)
✅ backend/models/__init__.py (UPDATED)
✅ backend/routes/jobs.py → internships.py (RENAMED)
⬜ Continue with remaining files...
