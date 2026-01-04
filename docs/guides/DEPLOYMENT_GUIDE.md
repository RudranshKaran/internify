# 🚀 Internify Deployment Guide

Complete step-by-step guide to deploy your Internify application to production.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- ✅ Supabase project already set up and running
- ✅ All environment variables ready
- ✅ GitHub account
- ✅ Vercel account (for frontend)
- ✅ Railway account (for backend)
- ✅ API keys: SERPAPI_KEY, GROQ_API_KEY or GEMINI_API_KEY

---

## 🗂️ Deployment Architecture

```
┌─────────────────┐
│   Vercel        │  Frontend (Next.js)
│  (Frontend)     │  → https://your-app.vercel.app
└────────┬────────┘
         │
         ↓ API Calls
┌─────────────────┐
│   Railway       │  Backend (FastAPI)
│  (Backend)      │  → https://your-api.up.railway.app
└────────┬────────┘
         │
         ↓ Database
┌─────────────────┐
│   Supabase      │  PostgreSQL + Auth + Storage
│  (Database)     │  → Already Cloud Hosted
└─────────────────┘
```

---

## Part 1: Push Code to GitHub

### Step 1: Initialize Git (if not already done)

```bash
# In project root
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

### Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create a new repository named `internify`
3. **Do NOT** initialize with README (you already have one)
4. Copy the repository URL

### Step 3: Push to GitHub

```bash
# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/internify.git

# Push code
git branch -M main
git push -u origin main
```

---

## Part 2: Deploy Backend (Railway)

### Step 1: Sign Up for Railway

1. Go to [Railway](https://railway.app)
2. Sign up with GitHub
3. Authorize Railway to access your repositories

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your `internify` repository
4. Click **"Deploy Now"**

**Railway will automatically:**
- Detect it's a Python project
- Install dependencies from `requirements.txt`
- Start your application

**Configure Settings (if needed):**
1. Click on your service in Railway dashboard
2. Go to **"Settings"** tab
3. Set **"Root Directory"** to `backend`
4. **Start Command** (if not auto-detected):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### Step 3: Add Environment Variables

In Railway dashboard:
1. Click on your deployed service
2. Go to **"Variables"** tab
3. Click **"New Variable"** and add each of these:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
SERPAPI_KEY=your_serpapi_key
GROQ_API_KEY=your_groq_api_key
# OR if using Gemini:
GEMINI_API_KEY=your_gemini_api_key
```

**Where to find these:**
- **Supabase Keys:** [Supabase Dashboard](https://supabase.com/dashboard) → Your Project → Settings → API
- **SerpAPI Key:** [SerpAPI Dashboard](https://serpapi.com/manage-api-key)
- **Groq API Key:** [Groq Console](https://console.groq.com/keys)
- **Gemini API Key:** [Google AI Studio](https://makersuite.google.com/app/apikey)

### Step 4: Get Your Deployment URL

1. Once deployment completes (2-5 minutes)
2. Go to **"Settings"** tab
3. Find **"Domains"** section
4. Copy the generated domain: `https://your-app.up.railway.app`
5. Or click **"Generate Domain"** if not automatically created

**⚠️ Important:** Keep this URL - you'll need it for frontend deployment!

---

## Part 3: Deploy Frontend (Vercel)

### Step 1: Sign Up for Vercel

1. Go to [Vercel](https://vercel.com)
2. Sign up with GitHub
3. Authorize Vercel to access your repositories

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Import your `internify` repository
3. Configure the project:

**Framework Preset:**
- Vercel should auto-detect **Next.js**

**Root Directory:**
- Click **Edit** next to Root Directory
- Select `frontend` folder
- Click **Continue**

### Step 3: Configure Environment Variables

Add these environment variables:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_BACKEND_URL=https://your-app.up.railway.app
```

**⚠️ Important:** 
- Replace `https://your-app.up.railway.app` with YOUR actual Railway backend URL
- DO NOT add trailing slashes

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait for deployment (2-5 minutes)
3. Once deployed, you'll get a URL like: `https://internify-xyz123.vercel.app`

---

## Part 4: Configure Supabase

### Step 1: Update Authentication Redirect URLs

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Authentication** → **URL Configuration**
4. Add these URLs to **Redirect URLs:**

```
https://your-app.vercel.app/dashboard
https://your-app.vercel.app/login
https://your-app.vercel.app/
```

Replace `your-app.vercel.app` with your actual Vercel domain

### Step 2: Update CORS Settings (if needed)

In Supabase Dashboard:
1. Go to **Settings** → **API**
2. Scroll to **CORS Settings**
3. Add your Vercel domain if not already allowed

---

## Part 5: Test Your Deployment

### Test Checklist

1. **Frontend Access**
   - [ ] Visit your Vercel URL
   - [ ] Homepage loads correctly
   - [ ] No console errors (F12 → Console)

2. **Authentication**
   - [ ] Click "Get Started" or "Login"
   - [ ] Sign up with email/password
   - [ ] Verify you're redirected to dashboard
   - [ ] Sign out and sign back in

3. **Resume Upload**
   - [ ] Upload a PDF resume
   - [ ] Verify upload completes
   - [ ] Check Supabase Storage bucket has the file

4. **Internship Search**
   - [ ] Search for "Software Engineer Intern"
   - [ ] Verify internships load from LinkedIn
   - [ ] Select an internship

5. **Email Generation**
   - [ ] Click to generate email
   - [ ] Verify AI generates personalized email
   - [ ] Edit subject and body
   - [ ] Copy email successfully

6. **Email History**
   - [ ] Navigate to History page
   - [ ] Verify generated emails are listed

---

## Part 6: Custom Domain (Optional)

### Vercel Custom Domain

1. Go to Vercel project dashboard
2. Click **Settings** → **Domains**
3. Add your domain (e.g., `internify.com`)
4. Follow DNS configuration instructions
5. Wait for DNS propagation (up to 48 hours)

### Update URLs After Custom Domain

Update in Supabase:
- Add `https://internify.com/dashboard` to redirect URLs

Update frontend env variables in Vercel:
- Keep `NEXT_PUBLIC_BACKEND_URL` pointing to Railway URL

---

## 🔧 Post-Deployment Configuration

### Enable HTTPS

Both Vercel and Render automatically provide SSL certificates. Ensure:
- Your backend URL uses `https://`
- Your frontend URL uses `https://`

### Set Up Monitoring

**Railway:**
1. Check **Deployments** tab for build logs
2. Monitor **Metrics** tab for CPU/Memory usage
3. Set up **Webhooks** for deploy notifications (Settings → Webhooks)

**Vercel:**
1. Check **Analytics** for performance
2. Set up **Log Drains** for debugging

### Environment Variables Management

**Never commit these files:**
- `frontend/.env.local`
- `backend/.env`

They should be in `.gitignore` already.

**To update environment variables:**
- **Railway:** Dashboard → Variables tab → Add/Edit → Save (auto-redeploys)
- **Vercel:** Dashboard → Settings → Environment Variables → Add → Redeploy

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Backend not starting
- **Check:** Railway logs (Deployments tab → View Logs)
- **Fix:** Verify all environment variables are set
- **Fix:** Ensure `requirements.txt` has all dependencies
- **Fix:** Check if Railway detected the correct start command

**Problem:** CORS errors
- **Check:** Browser console for CORS errors
- **Fix:** Verify Vercel domain is allowed in backend CORS settings
- **Fix:** Check `main.py` has correct CORS origins

**Problem:** 500 Internal Server Error
- **Check:** Railway logs for detailed error messages
- **Fix:** Missing environment variables
- **Fix:** Check Supabase connection

### Frontend Issues

**Problem:** "Network Error" or "Failed to fetch"
- **Check:** Verify `NEXT_PUBLIC_BACKEND_URL` is correct
- **Fix:** Make sure backend URL has NO trailing slash
- **Fix:** Ensure backend is deployed and running

**Problem:** Authentication not working
- **Check:** Supabase redirect URLs are configured
- **Fix:** Add all possible URLs to Supabase Auth settings

**Problem:** Images/files not loading
- **Check:** Supabase Storage bucket is public (if needed)
- **Fix:** Verify Storage policies in Supabase

### Database Issues

**Problem:** "Invalid JWT" errors
- **Check:** Verify Supabase keys match in all environments
- **Fix:** Regenerate Supabase service key if compromised

---

## 📊 Monitoring & Maintenance

### Check Application Health

**Daily:**
- Visit your app to ensure it's running
- Check Railway dashboard for uptime and metrics

**Weekly:**
- Review Vercel analytics
- Check Railway usage and metrics
- Check Supabase database usage
- Monitor API usage (SerpAPI, Groq/Gemini)

### Keep Dependencies Updated

**Monthly:**
```bash
# Frontend
cd frontend
npm update

# Backend
cd backend
pip list --outdated
```

### Backup Your Database

Supabase provides automatic backups on paid plans. For free tier:
1. Go to Supabase Dashboard
2. Database → Backups
3. Configure backup schedule or download manual backups

---

## 💰 Cost Estimates (Free Tier)

| Service | Free Tier Limits | Upgrade Cost |
|---------|------------------|--------------|
| **Vercel** | 100GB bandwidth/month | $20/month |
| **Railway** | $5 free credit/month (500 hours) | $5-20/month (usage-based) |
| **Supabase** | 500MB database, 1GB storage | $25/month |
| **SerpAPI** | 100 searches/month | $50/month (5k searches) |
| **Groq** | Free tier available | Variable |
| **Gemini** | Free tier available | Variable |

**Total Monthly Cost (Free Tier):** $0 (with $5 Railway credit)
**If you upgrade everything:** ~$100/month

---

## 🎉 You're Done!

Your application is now live at:
- **Frontend:** `https://your-app.vercel.app`
- **Backend:** `https://your-app.up.railway.app`

### Share Your Project

- Add the live URL to your GitHub repo description
- Share with friends and on social media
- Add to your portfolio

### Next Steps

1. Set up analytics (Google Analytics, Plausible)
2. Add error tracking (Sentry)
3. Create user documentation
4. Gather feedback and iterate

---

## 📞 Need Help?

- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **Supabase Docs:** https://supabase.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Next.js Docs:** https://nextjs.org/docs

---

**Congratulations on deploying Internify! 🚀🎊**
