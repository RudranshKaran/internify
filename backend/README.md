# Internify Backend - FastAPI

This is the backend API for the Internify platform, built with FastAPI.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from `.env.example` and fill in your API keys

4. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Authentication
- `POST /auth/verify` - Verify Supabase JWT

### Resume
- `POST /resume/upload` - Upload resume and extract data

### Jobs
- `GET /jobs/search` - Search for jobs using SerpAPI

### LLM
- `POST /llm/generate-email` - Generate personalized email

### Email
- `POST /email/send` - Send email via Resend
- `GET /email/history` - Get user's email history
