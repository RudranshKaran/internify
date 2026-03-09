# InternFlow - AI-Powered Internship Application Platform

InternFlow is a modern, full-stack web platform that automates the entire internship application process. It helps users send personalized cold emails to companies by leveraging AI, real-time internship scraping, and automated email outreach.

![Tech Stack](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-green)
![Supabase](https://img.shields.io/badge/Supabase-Database-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-Strict-blue)

> 📚 **Documentation**: All project documentation is organized in the [`docs/`](./docs) folder. Start with [`docs/README.md`](./docs/README.md) for navigation.

---

## Features

- 🔐 **Secure Authentication** - Supabase Auth with JWT validation
- 📄 **Resume Upload & Parsing** - Extract key information from PDF resumes
- 🔍 **Real-Time Internship Search** - Fetch latest internship postings from LinkedIn via SerpAPI
- 🤖 **AI Email Generation** - Personalized cold emails using Groq/Gemini LLM
- 📋 **Easy Copy & Use** - Copy generated emails to use in your email client
- 📊 **Application History** - Track all generated email applications
- 🎨 **Beautiful UI** - Modern design with Tailwind CSS and shadcn/ui
- 📱 **Fully Responsive** - Works seamlessly on all devices

---

## Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **Forms:** React Hook Form + Zod
- **HTTP Client:** Axios
- **Animations:** Framer Motion

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Database:** PostgreSQL (Supabase)
- **Authentication:** Supabase Auth
- **File Storage:** Supabase Storage
- **AI/LLM:** Groq API (LLaMA-3) / Gemini API
- **Job Scraping:** SerpAPI

---

## Project Structure

```
internflow/
│
├── backend/                  # FastAPI Backend
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt     # Python dependencies
│   │
│   ├── models/              # Pydantic models
│   │   ├── user.py
│   │   ├── internship.py
│   │   ├── email.py
│   │   └── resume.py
│   │
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── resume.py
│   │   ├── internships.py
│   │   ├── llm.py
│   │   ├── email.py
│   │   └── utils.py
│   │
│   └── services/            # Business logic
│       ├── supabase_service.py
│       ├── llm_service.py

│       └── scraper_service.py
│
└── frontend/                # Next.js Frontend
    ├── app/                 # App router pages
    │   ├── page.tsx        # Landing page
    │   ├── login/
    │   ├── dashboard/
    │   ├── email-preview/
    │   └── history/
    │
    ├── components/          # React components
    │   ├── Navbar.tsx
    │   ├── InternshipCard.tsx
    │   ├── ResumeUploader.tsx
    │   ├── EmailPreview.tsx
    │   ├── Loader.tsx
    │   └── Toast.tsx
    │
    ├── lib/                 # Utilities
    │   ├── supabaseClient.ts
    │   └── api.ts
    │
    └── package.json
```

---

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Supabase account
- API Keys:
  - SerpAPI key
  - Groq API key or Gemini API key

---

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   SERPAPI_KEY=your_serpapi_key
   GROQ_API_KEY=your_groq_api_key
   # OR
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. **Run the server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

Backend will be available at `http://localhost:8000`

---

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Create `.env.local` file:**
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

4. **Run development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

Frontend will be available at `http://localhost:3000`

---

## Database Schema

Create these tables in your Supabase database:

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Internships Table
```sql
CREATE TABLE internships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    link TEXT,
    description TEXT,
    location TEXT,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Emails Table
```sql
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    internship_id UUID REFERENCES internships(id),
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'sent',
    recipient_email TEXT
);
```

### Resumes Table
```sql
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    file_path TEXT NOT NULL,
    extracted_text TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

### Authentication
- `POST /auth/verify` - Verify Supabase JWT token

### Resume
- `POST /resume/upload` - Upload and parse resume PDF

### Internships
- `GET /internships/search?role={role}` - Search for internship listings

### LLM
- `POST /llm/generate-email` - Generate personalized email

### Email
- `GET /email/history` - Get user's generated email history

---

## Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Connect repository to Vercel
3. Add environment variables
4. Deploy

### Backend (Render / Railway)

1. Create new web service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### Database (Supabase)

Already cloud-hosted. Just configure connection strings.

---

## Environment Variables

### Backend `.env`
```env
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
SERPAPI_KEY=
GROQ_API_KEY=
```

### Frontend `.env.local`
```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_BACKEND_URL=
```

---

## 📝 Usage Flow

1. **Sign Up / Login** - Create account using email/password
2. **Upload Resume** - Upload your PDF resume for parsing
3. **Search Jobs** - Enter desired role (e.g., "Software Engineer Intern")
4. **Select Job** - Choose from real-time LinkedIn listings
5. **Generate Email** - AI creates personalized cold email
6. **Review & Edit** - Customize the generated email
7. **Copy** - Copy email to use in your email client
8. **Track** - View all generated emails in history dashboard

---

## UI/UX Highlights

- Clean, modern SaaS-inspired design
- Soft color palette (blue, white, gray tones)
- Smooth animations with Framer Motion
- Responsive layout for all screen sizes
- Accessible components from shadcn/ui
- Intuitive user flow

---

## Future Enhancements

- [ ] Email analytics (open/reply tracking)
- [ ] Chrome extension for direct LinkedIn integration
- [ ] Company bookmarking system
- [ ] OAuth login (Google, GitHub)
- [ ] Resume templates
- [ ] A/B testing for email variants
- [ ] Bulk email campaigns
- [ ] AI-powered follow-up suggestions

---

## License

MIT License

---

## Author

Built with ❤️ for automating internship applications

---

## Acknowledgments

- Supabase for authentication and database
- Groq for AI email generation
- SerpAPI for job scraping
- Vercel for frontend hosting

---

**Happy Job Hunting! 🎯**
