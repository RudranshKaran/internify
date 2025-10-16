# 🚀 Quick Setup Guide - Internify

## Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Supabase account created
- [ ] API keys obtained:
  - [ ] Resend API key
  - [ ] SerpAPI key  
  - [ ] Groq API key (or Gemini)

---

## Step 1: Supabase Setup (5 minutes)

### Create Project
1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Note down your project URL and anon key

### Create Database Tables

Run these SQL queries in Supabase SQL Editor:

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    link TEXT,
    description TEXT,
    location TEXT,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Emails table
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    job_id UUID REFERENCES jobs(id),
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'sent',
    recipient_email TEXT
);

-- Resumes table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    file_path TEXT NOT NULL,
    extracted_text TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

### Create Storage Bucket
1. Go to Storage in Supabase dashboard
2. Create new bucket named `resumes`
3. Set it to private

---

## Step 2: Get API Keys (10 minutes)

### Resend API Key
1. Visit [resend.com](https://resend.com)
2. Sign up and create API key
3. Free tier: 100 emails/day

### SerpAPI Key
1. Visit [serpapi.com](https://serpapi.com)
2. Sign up for free account
3. Get API key from dashboard
4. Free tier: 100 searches/month

### Groq API Key (Recommended)
1. Visit [groq.com](https://console.groq.com)
2. Sign up and get API key
3. Fast and free!

**Alternative:** Gemini API
1. Visit [makersuite.google.com](https://makersuite.google.com/app/apikey)
2. Create API key

---

## Step 3: Backend Setup (5 minutes)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
Copy-Item .env.example .env

# Edit .env with your API keys
notepad .env
```

Fill in your `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
RESEND_API_KEY=re_your-key
SERPAPI_KEY=your-serpapi-key
GROQ_API_KEY=gsk_your-key
```

Start backend:
```powershell
uvicorn main:app --reload --port 8000
```

Backend will run at: http://localhost:8000

---

## Step 4: Frontend Setup (5 minutes)

```powershell
# Open new terminal
cd frontend

# Install dependencies
npm install

# Create .env.local
Copy-Item .env.local.example .env.local

# Edit .env.local
notepad .env.local
```

Fill in your `.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Start frontend:
```powershell
npm run dev
```

Frontend will run at: http://localhost:3000

---

## Step 5: Test the Application

1. Open http://localhost:3000
2. Click "Get Started" and create an account
3. Upload a test resume (PDF)
4. Search for jobs (e.g., "Software Engineer Intern")
5. Select a job
6. Generate email
7. Review and send!

---

## Deployment

### Deploy Backend to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. New Web Service → Connect GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`
5. Add environment variables
6. Deploy!

### Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import GitHub repository
3. Settings:
   - **Root Directory:** `frontend`
   - **Framework:** Next.js
4. Add environment variables
5. Deploy!

### Update Frontend ENV

After backend deploys, update:
```env
NEXT_PUBLIC_BACKEND_URL=https://your-app.onrender.com
```

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.11+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Clear cache: `rm -rf node_modules package-lock.json && npm install`

### "Module not found" errors
- Make sure you're in correct directory
- Verify .env files exist and are filled out

### Can't upload resume
- Check Supabase storage bucket exists
- Verify bucket is named `resumes`
- Check SUPABASE_SERVICE_KEY in backend .env

### Emails not sending
- Verify RESEND_API_KEY is correct
- Check Resend dashboard for errors
- Make sure you're within free tier limits (100/day)

---

## Free Tier Limits

- **Supabase:** 500MB database, 1GB bandwidth/month
- **Resend:** 100 emails/day, 3,000/month
- **SerpAPI:** 100 searches/month
- **Groq:** Very generous free tier
- **Render:** 750 hours/month (enough for 1 app)
- **Vercel:** Unlimited personal projects

---

## Need Help?

Check the main README.md for full documentation.

Happy job hunting! 🎯
