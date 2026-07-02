# Supabase Setup

This guide covers the Supabase setup used by InternFlow end to end: authentication, database tables, storage, row-level security, and the environment variables required by the backend and frontend.

Use this guide if you are starting a new Supabase project, fixing missing-table or missing-bucket errors, or rebuilding the database from scratch.

## What InternFlow Uses Supabase For

- Authentication through Supabase Auth JWTs.
- Database storage for `users`, `internships`, `emails`, and `resumes`.
- Private storage for uploaded resume PDFs.

The backend verifies Supabase JWTs in [backend/routes/auth.py](../../backend/routes/auth.py) and uses the service key through [backend/services/supabase_service.py](../../backend/services/supabase_service.py). The frontend uses the browser session client in [frontend/lib/supabaseClient.ts](../../frontend/lib/supabaseClient.ts).

## Prerequisites

- A Supabase account and project.
- Access to the Supabase dashboard SQL Editor and Storage section.
- The repo checked out locally.

## Recommended Setup Path

1. Create or open your Supabase project.
2. Run [docs/database/supabase_complete_setup.sql](../database/supabase_complete_setup.sql).
3. Add the environment variables listed below.
4. Restart the backend and frontend.
5. Test login and resume upload.

## 1) Create or Select a Supabase Project

1. Go to https://supabase.com/dashboard.
2. Create a new project or open an existing one.
3. Copy the Project URL and the keys from the project settings.

You will need:

- `SUPABASE_URL` for the backend.
- `SUPABASE_SERVICE_KEY` for the backend.
- `NEXT_PUBLIC_SUPABASE_URL` for the frontend.
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` for the frontend.

## 2) Run the Database Setup Script

Open the Supabase SQL Editor and run the full contents of [docs/database/supabase_complete_setup.sql](../database/supabase_complete_setup.sql).

This script creates:

- `users`
- `internships`
- `emails`
- `resumes`
- indexes for common lookups
- row-level security policies
- the private `resumes` storage bucket
- storage policies for authenticated users

### Important schema note

Some older docs in the repo mention a `jobs` table. The current schema uses `internships` instead, matching the backend code and documentation refresh.

## 3) Confirm Storage Setup

The setup script inserts a private storage bucket named `resumes` with a 10 MB size limit and PDF-only MIME type.

If you prefer to create it manually in the dashboard, use:

- Bucket name: `resumes`
- Public: `false`
- File size limit: `10485760`
- Allowed MIME types: `application/pdf`

### Storage policy behavior

Resume uploads are expected to live under a user-owned folder path. The policies allow access when the first folder segment matches the authenticated user ID:

```sql
(storage.foldername(name))[1] = auth.uid()::text
```

That is why the app can safely keep the bucket private while still letting users manage their own files.

## 4) Add Environment Variables

### Backend `.env`

Set these in `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

The backend uses `SUPABASE_SERVICE_KEY` first and falls back to `SUPABASE_ANON_KEY` only if needed, but for production the service role key should be present.

### Frontend `.env.local`

Set these in `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Only the anon key should be exposed to the browser.

## 5) Restart the App

After updating the SQL schema and environment variables:

1. Restart the backend.
2. Restart the frontend.
3. Sign in again so the client gets a fresh session.

## 6) Verify the Setup

In Supabase, confirm the following exist:

- Tables: `users`, `internships`, `emails`, `resumes`
- Storage bucket: `resumes`
- RLS policies: enabled for the tables and storage objects

From the application side, verify:

- Login succeeds.
- `/auth/verify` returns the signed-in user.
- Resume upload creates a file in the `resumes` bucket.
- Resume metadata is saved to the `resumes` table.

## How the App Uses These Records

- `users` stores the authenticated user profile row.
- `internships` stores internship postings used by the app.
- `emails` stores generated or sent email history.
- `resumes` stores resume metadata and extracted text.

The backend service methods in [backend/services/supabase_service.py](../../backend/services/supabase_service.py) read and write these tables directly.

## Troubleshooting

### `Bucket not found`

- Confirm the bucket name is exactly `resumes`.
- Confirm the SQL script finished successfully.
- Check Storage in the Supabase dashboard.

### `Could not find the table 'public.resumes'`

- Re-run [docs/database/supabase_complete_setup.sql](../database/supabase_complete_setup.sql).
- Check the Table Editor for `resumes`.
- Make sure you are in the correct Supabase project.

### Authentication works in the browser but fails on the backend

- Confirm `SUPABASE_URL` is set.
- Confirm `SUPABASE_SERVICE_KEY` is set in the backend environment.
- Make sure the frontend and backend are pointing at the same Supabase project.

### Resume upload returns a permission error

- Confirm the storage policies were created.
- Confirm the file path includes the user ID folder expected by the policy.
- Confirm the logged-in user has a valid JWT session.

### `users` row is missing after login

- The backend creates the `users` row in `/auth/verify` after validating the JWT.
- If that route has not been called, sign in again and hit the app flow that triggers auth verification.

## Related Files

- [docs/database/supabase_complete_setup.sql](../database/supabase_complete_setup.sql)
- [backend/services/supabase_service.py](../../backend/services/supabase_service.py)
- [backend/routes/auth.py](../../backend/routes/auth.py)
- [frontend/lib/supabaseClient.ts](../../frontend/lib/supabaseClient.ts)
- [docs/guides/SETUP.md](SETUP.md)
- [docs/README.md](../README.md)

## After Setup

Once you've completed these steps:
1. ✅ Database tables created
2. ✅ Storage bucket created
3. ✅ Storage policies configured
4. ✅ Resume upload should work!

You should be able to:
- Upload PDF resumes
- View your uploaded resumes
- Search for jobs
- Generate personalized emails

---

## Need Help?

If you encounter any issues:
1. Check the backend terminal for error messages
2. Check browser console for frontend errors
3. Check Supabase dashboard logs
4. Make sure all environment variables are set correctly in `backend/.env`
