# 📄 API Documentation - Internify

Base URL: `http://localhost:8000` (development)

## Authentication

All endpoints except root require authentication via Supabase JWT token.

Add to headers:
```
Authorization: Bearer <supabase_access_token>
```

---

## Endpoints

### 🔐 Authentication

#### POST `/auth/verify`
Verify Supabase JWT and create/fetch user

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### 📄 Resume

#### POST `/resume/upload`
Upload resume PDF and extract text

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
```json
{
  "id": "uuid",
  "file_path": "user-id/resumes/resume_timestamp.pdf",
  "extracted_text": "Resume content...",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

#### GET `/resume/latest`
Get user's most recent resume

**Response:**
```json
{
  "success": true,
  "resume": {
    "id": "uuid",
    "file_path": "path/to/resume.pdf",
    "extracted_text": "Resume content...",
    "uploaded_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### 💼 Jobs

#### GET `/jobs/search`
Search for job listings

**Query Parameters:**
- `role` (required): Job title/role
- `location` (optional): Location filter
- `limit` (optional, default=10): Max results (1-50)

**Example:**
```
GET /jobs/search?role=Software Engineer Intern&location=San Francisco&limit=20
```

**Response:**
```json
{
  "success": true,
  "jobs": [
    {
      "id": "uuid",
      "title": "Software Engineer Intern",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "description": "Job description...",
      "link": "https://...",
      "posted_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 15
}
```

#### GET `/jobs/{job_id}`
Get specific job details

**Response:**
```json
{
  "success": true,
  "job": {
    "id": "uuid",
    "title": "Software Engineer Intern",
    "company": "Tech Corp",
    "link": "https://...",
    "description": "Full description..."
  }
}
```

---

### 🤖 LLM (Email Generation)

#### POST `/llm/generate-email`
Generate personalized cold email using AI

**Request Body:**
```json
{
  "job_description": "We're looking for...",
  "resume_text": "My resume content...",
  "job_title": "Software Engineer Intern",
  "company_name": "Tech Corp"
}
```

**Response:**
```json
{
  "subject": "Application for Software Engineer Intern Position at Tech Corp",
  "body": "Dear Hiring Manager,\n\nI am writing to express...",
  "success": true
}
```

#### POST `/llm/regenerate-email`
Regenerate email (same as generate-email, returns new version)

---

### ✉️ Email

#### POST `/email/send`
Send cold email to company

**Request Body:**
```json
{
  "job_id": "uuid",
  "recipient_email": "hr@company.com",
  "subject": "Application for...",
  "body": "Email content..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully!",
  "email": {
    "id": "uuid",
    "sent_at": "2024-01-15T10:30:00Z",
    "status": "sent"
  }
}
```

#### GET `/email/history`
Get user's email history

**Query Parameters:**
- `limit` (optional, default=50): Max emails (1-100)

**Response:**
```json
{
  "success": true,
  "emails": [
    {
      "id": "uuid",
      "subject": "Application for...",
      "body": "Email content...",
      "recipient_email": "hr@company.com",
      "sent_at": "2024-01-15T10:30:00Z",
      "status": "sent",
      "jobs": {
        "title": "Software Engineer Intern",
        "company": "Tech Corp",
        "link": "https://..."
      }
    }
  ],
  "count": 25
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing/invalid token)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limits

- **SerpAPI:** 100 searches/month (free tier)
- **Resend:** 100 emails/day (free tier)
- **Groq:** Generous free tier, check their docs

---

## Testing with cURL

### Example: Search for jobs
```bash
curl -X GET "http://localhost:8000/jobs/search?role=Software%20Engineer%20Intern" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example: Generate email
```bash
curl -X POST "http://localhost:8000/llm/generate-email" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Looking for a passionate developer",
    "resume_text": "My skills include...",
    "job_title": "Software Engineer",
    "company_name": "Tech Corp"
  }'
```

---

## Interactive Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly!

---

For more information, see the main README.md
