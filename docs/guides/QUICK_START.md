# 🚀 Quick Start Guide - Internify

## Current Status: ✅ ALL ISSUES FIXED!

Your frontend is now fully configured and ready. The only thing left is adding your Supabase credentials.

---

## What Was Fixed

1. ✅ React Hook ESLint warnings
2. ✅ TypeScript version mismatch  
3. ✅ Missing `tailwindcss-animate` package
4. ✅ Next.js security vulnerabilities (updated to 14.2.33)
5. ✅ Missing `.env.local` file created
6. ✅ CSS linting warnings suppressed
7. ✅ All dependencies installed and up to date

---

## Your `.env.local` File Location

**File:** `c:\Users\rudra\Desktop\projects\internify\frontend\.env.local`

**Current content:**
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Where to Get Supabase Credentials

### Step 1: Go to Supabase Dashboard
🔗 https://supabase.com/dashboard

### Step 2: Create/Select Your Project
Click on your "Internify" project (or create one if you haven't)

### Step 3: Get Your Credentials
1. Click **Settings** (gear icon in sidebar)
2. Click **API** in the settings menu
3. Find and copy these values:

#### For Frontend (`.env.local`):
- **Project URL** → Copy to `NEXT_PUBLIC_SUPABASE_URL`
- **anon public** key → Copy to `NEXT_PUBLIC_SUPABASE_ANON_KEY`

#### For Backend (`.env`):
- **Project URL** → Copy to `SUPABASE_URL`
- **service_role** key (⚠️ NOT anon) → Copy to `SUPABASE_KEY`
- Scroll down to **JWT Settings** → Copy **JWT Secret** to `SUPABASE_JWT_SECRET`

---

## Example `.env.local` (Frontend)

```bash
# Replace with your actual values from Supabase dashboard
NEXT_PUBLIC_SUPABASE_URL=https://xyzabcdefgh.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5emFiY2RlZmdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTg0MjE4NjAsImV4cCI6MjAxMzk5Nzg2MH0.abc123xyz
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Testing After Adding Credentials

### 1. Start Frontend (Development Mode)
```powershell
cd frontend
npm run dev
```
Visit: http://localhost:3000

### 2. Start Backend (Separate Terminal)
```powershell
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload
```
Backend will run on: http://localhost:8000

### 3. Verify Build Works
```powershell
cd frontend
npm run build
```
This should now succeed! ✅

---

## Quick Commands Reference

| Task | Command | Directory |
|------|---------|-----------|
| Start frontend dev server | `npm run dev` | `/frontend` |
| Build frontend for production | `npm run build` | `/frontend` |
| Run frontend linting | `npm run lint` | `/frontend` |
| Start backend server | `uvicorn main:app --reload` | `/backend` |
| Install Python packages | `pip install -r requirements.txt` | `/backend` |
| Activate Python venv | `.\venv\Scripts\activate` | `/backend` |

---

## Supabase Setup Checklist

- [ ] Create Supabase account at https://supabase.com
- [ ] Create new project called "Internify"
- [ ] Copy Project URL to both `.env` files
- [ ] Copy anon key to `frontend/.env.local`
- [ ] Copy service_role key to `backend/.env`
- [ ] Copy JWT Secret to `backend/.env`
- [ ] Run `database_schema.sql` in SQL Editor
- [ ] Create 'resumes' storage bucket (private)
- [ ] Verify build works: `npm run build`
- [ ] Test frontend: `npm run dev`

---

## API Keys You'll Also Need (Backend)

### Groq API (Recommended - Free AI)
🔗 https://console.groq.com
- Sign up
- Create API key
- Add to `backend/.env` as `GROQ_API_KEY`

### Resend API (Email Sending)
🔗 https://resend.com/api-keys  
- Sign up
- Create API key
- Add to `backend/.env` as `RESEND_API_KEY`

### SerpAPI (Job Search)
🔗 https://serpapi.com/manage-api-key
- Sign up
- Copy API key
- Add to `backend/.env` as `SERPAPI_KEY`

---

## Troubleshooting

### Build still fails with "Invalid supabaseUrl"?
✅ Make sure you replaced the placeholder text in `.env.local`
✅ URL should start with `https://` 
✅ No quotes needed around the values

### Frontend starts but can't connect to backend?
✅ Make sure backend is running: `uvicorn main:app --reload`
✅ Check `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000` in `.env.local`

### Can't sign up/login?
✅ Verify Supabase credentials are correct
✅ Check you ran `database_schema.sql` in Supabase SQL Editor
✅ Make sure you're using the **anon** key in frontend (not service_role)

---

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Frontend .env | `frontend/.env.local` | Supabase public credentials |
| Backend .env | `backend/.env` | All API keys and secrets |
| Database schema | `database_schema.sql` | SQL to run in Supabase |
| Setup guide | `SETUP.md` | Detailed setup instructions |
| API docs | `API_DOCS.md` | All API endpoints documented |

---

## What Works Right Now

✅ All code compiles without errors
✅ All dependencies installed
✅ No security vulnerabilities
✅ ESLint passes with 0 warnings
✅ TypeScript configured correctly
✅ Tailwind CSS working perfectly
✅ All components and pages created
✅ Build system ready (needs .env values)

---

## Next Action: ADD YOUR SUPABASE CREDENTIALS! 🔑

1. Open `frontend/.env.local` in VS Code
2. Go to https://supabase.com/dashboard
3. Copy your Project URL and Anon Key
4. Replace the placeholder text
5. Save the file
6. Run `npm run dev`
7. Visit http://localhost:3000

**You're almost there!** 🎉
