# Internify Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                    (http://localhost:3000)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NEXT.JS FRONTEND                            │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐   │
│  │ Landing Page │ Login/Signup │   Dashboard  │  History   │   │
│  │  (page.tsx)  │   (Auth)     │   (Upload)   │  (Track)   │   │
│  └──────────────┴──────────────┴──────────────┴────────────┘   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              REUSABLE COMPONENTS                        │    │
│  │  • Navbar  • InternshipCard  • ResumeUploader        │    │
│  │  • EmailPreview  • Loader  • Toast                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                 LIB/UTILITIES                           │    │
│  │  • Supabase Client (Auth)                              │    │
│  │  • API Client (Axios)                                  │    │
│  │  • Helper Functions                                    │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Axios + JWT
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                              │
│                  (http://localhost:8000)                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API ROUTES                             │  │
│  │  • /auth/verify       - JWT validation                   │  │
│  │  • /resume/upload     - PDF upload & parse              │  │
│  │  • /internships/search - Internship search              │  │
│  │  • /llm/generate      - AI email gen                     │  │
│  │  • /email/send        - Send emails                      │  │
│  │  • /email/history     - Track emails                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   SERVICES LAYER                          │  │
│  │                                                            │  │
│  │  ┌───────────────┐  ┌────────────────┐                  │  │
│  │  │   Supabase    │  │   LLM Service  │                  │  │
│  │  │   Service     │  │  (Groq/Gemini) │                  │  │
│  │  │  • Auth       │  │  • Generate    │                  │  │
│  │  │  • Database   │  │    Email       │                  │  │
│  │  │  • Storage    │  │  • Customize   │                  │  │
│  │  └───────────────┘  └────────────────┘                  │  │
│  │                                                            │  │
│  │  ┌───────────────┐  ┌────────────────┐                  │  │
│  │  │  Resend API   │  │ SerpAPI        │                  │  │
│  │  │  Service      │  │ Service        │                  │  │
│  │  │  • Send Email │  │ • Internship   │                  │  │
│  │  │  • Format     │  │   Search       │                  │  │
│  │  └───────────────┘  └────────────────┘                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└───┬──────────────┬──────────────┬──────────────┬───────────────┘
    │              │              │              │
    │              │              │              │
    ▼              ▼              ▼              ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Supabase│  │  Resend  │  │ SerpAPI  │  │Groq/Gemini│
│(Cloud) │  │  (Email) │  │(Internshp)│  │   (AI)   │
│        │  │          │  │          │  │          │
│• Auth  │  │• Send    │  │• LinkedIn│  │• LLaMA-3 │
│• DB    │  │• Track   │  │• Google  │  │• Gemini  │
│• Store │  │          │  │ Internshp│  │• Smart   │
└────────┘  └──────────┘  └──────────┘  └──────────┘


DATA FLOW:
──────────

1. USER AUTHENTICATION
   User → Frontend → Supabase Auth → JWT Token → Backend validates

2. RESUME UPLOAD
   User uploads PDF → Frontend → Backend → Extract text (PyPDF2)
   → Store in Supabase Storage → Save metadata to DB

3. INTERNSHIP SEARCH
   User enters role → Frontend → Backend → SerpAPI → Parse results
   → Save to DB → Return to Frontend → Display as cards

4. EMAIL GENERATION
   User selects internship → Frontend → Backend → Fetch resume
   → Call Groq/Gemini API → Generate personalized email
   → Return to Frontend → Display in editor

5. SEND EMAIL
   User clicks send → Frontend → Backend → Resend API
   → Email sent → Save to DB → Update history → Confirm to user


DATABASE SCHEMA:
────────────────

┌─────────────┐       ┌──────────────┐
│   users     │       │   resumes    │
├─────────────┤       ├──────────────┤
│ id (PK)     │◄──────┤ user_id (FK) │
│ email       │       │ file_path    │
│ name        │       │ extracted_   │
│ created_at  │       │   text       │
└─────────────┘       └──────────────┘
      │
      │
      ▼
┌─────────────┐       ┌──────────────┐
│   emails    │       │ internships  │
├─────────────┤       ├──────────────┤
│ id (PK)     │       │ id (PK)      │
│ user_id(FK) │       │ title        │
│intership_id ├──────►│ company      │
│   (FK)      │       │ link         │
│ subject     │       │ description  │
│ body        │       │ location     │
│ recipient   │       └──────────────┘
│ sent_at     │
│ status      │
└─────────────┘


DEPLOYMENT ARCHITECTURE:
────────────────────────

┌─────────────────┐
│   VERCEL        │  ← Frontend hosting (Free)
│  (Frontend)     │     • Automatic builds
│  • Next.js App  │     • CDN distribution
│  • Edge network │     • SSL included
└────────┬────────┘
         │
         │ API calls
         ▼
┌─────────────────┐
│ RENDER/RAILWAY  │  ← Backend hosting (Free tier)
│   (Backend)     │     • Auto-deploy from Git
│ • FastAPI       │     • Environment variables
│ • Python 3.11+  │     • Logs & monitoring
└────────┬────────┘
         │
         │ Database queries
         ▼
┌─────────────────┐
│   SUPABASE      │  ← Database & Auth (Free tier)
│  (Cloud)        │     • PostgreSQL
│ • Database      │     • Authentication
│ • Auth          │     • File storage
│ • Storage       │     • Row-level security
└─────────────────┘


SECURITY LAYERS:
────────────────

1. AUTHENTICATION
   Supabase JWT → Verified on every request

2. AUTHORIZATION
   Row-level security → Users only see their data

3. VALIDATION
   Frontend (Zod) + Backend (Pydantic)

4. ENVIRONMENT VARS
   All secrets in .env files → Never committed

5. CORS
   Only allowed origins can access API

6. FILE UPLOADS
   PDF only → Size limits → Virus scan ready


TECHNOLOGY STACK:
─────────────────

Frontend:
• Next.js 14 (App Router)
• TypeScript (Type safety)
• Tailwind CSS (Styling)
• Framer Motion (Animations)
• Axios (HTTP client)
• React Hook Form + Zod (Forms)

Backend:
• FastAPI (Async Python)
• Pydantic (Validation)
• PyPDF2 (PDF parsing)
• Python 3.11+

Database & Services:
• Supabase (PostgreSQL + Auth + Storage)
• Resend (Email API)
• SerpAPI (Internship scraping)
• Groq/Gemini (AI/LLM)

Deployment:
• Vercel (Frontend)
• Render/Railway (Backend)
• Git/GitHub (Version control)


API ENDPOINT FLOW:
──────────────────

GET  /                     → Health check
POST /auth/verify          → Validate JWT, create/get user
POST /resume/upload        → Upload PDF, extract text, store
GET  /resume/latest        → Get user's latest resume
GET  /internships/search   → Search internships via SerpAPI
GET  /internships/{id}     → Get specific internship details
POST /llm/generate         → Generate email with AI
POST /email/send           → Send email via Resend
GET  /email/history        → Get user's sent emails


FREE TIER LIMITS:
─────────────────

Supabase:  500MB DB, 1GB file storage, 50,000 monthly active users
Resend:    100 emails/day, 3,000/month
SerpAPI:   100 searches/month
Groq:      Generous free tier, check their limits
Vercel:    Unlimited for personal projects
Render:    750 hours/month (enough for 1 app 24/7)


PERFORMANCE OPTIMIZATIONS:
──────────────────────────

1. Database indexes on frequently queried columns
2. FastAPI async for non-blocking I/O
3. Next.js automatic code splitting
4. Image optimization (Next.js built-in)
5. CDN for static assets (Vercel)
6. Connection pooling (Supabase)
7. Lazy loading components
8. Debounced search inputs


This architecture is:
✅ Scalable - Can handle thousands of users
✅ Secure - Multiple security layers
✅ Fast - Optimized at every layer
✅ Reliable - Cloud providers with 99.9% uptime
✅ Cost-effective - Free tier covers most use cases
✅ Maintainable - Clean code structure
✅ Modern - Latest tech stack
✅ Production-ready - Error handling & monitoring
```
