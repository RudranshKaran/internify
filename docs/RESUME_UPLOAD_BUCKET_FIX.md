# 🔧 Resume Upload "Bucket Not Found" Fix

## Date: October 15, 2025

## Problem Summary
When trying to upload a resume, the application fails with:
```
Error uploading file: {'statusCode': 404, 'error': Bucket not found, 'message': Bucket not found}
Error fetching resume: {'message': "Could not find the table 'public.resumes' in the schema cache"}
```

## Root Cause
The Supabase database and storage have not been set up yet:
1. ❌ Database tables (`users`, `resumes`, `jobs`, `emails`) don't exist
2. ❌ Storage bucket (`resumes`) doesn't exist
3. ❌ Storage policies for access control don't exist

## Solution

### Quick Fix (5 minutes):
1. Go to https://app.supabase.com
2. Open your project: `nrcoscehjfbxwafjhxvq`
3. Go to **SQL Editor**
4. Open the file `supabase_complete_setup.sql` from this project
5. Copy and paste the ENTIRE script
6. Click **Run** (or Ctrl+Enter)
7. Wait for "Setup complete!" message

That's it! Now try uploading a resume.

### What the script does:
✅ Creates all database tables (users, resumes, jobs, emails)
✅ Creates indexes for better performance
✅ Enables Row Level Security (RLS)
✅ Creates RLS policies for data protection
✅ Creates `resumes` storage bucket
✅ Creates storage policies for file access control

## Detailed Setup (if you prefer manual steps)

### Step 1: Create Database Tables
Run the SQL in `database_schema.sql` in Supabase SQL Editor

### Step 2: Create Storage Bucket
1. Go to **Storage** in Supabase dashboard
2. Click **New Bucket**
3. Name: `resumes`
4. Public: No (private)
5. Max file size: 10 MB
6. Allowed types: `application/pdf`

### Step 3: Set Storage Policies
Run these SQL commands:
```sql
-- Users can upload their own resumes
CREATE POLICY "Users can upload own resumes"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can read their own resumes
CREATE POLICY "Users can read own resumes"
ON storage.objects FOR SELECT TO authenticated
USING (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

## Verification

After running the setup, verify:

### Check Tables:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'resumes', 'jobs', 'emails');
```

Should return 4 rows.

### Check Bucket:
```sql
SELECT id, name, public FROM storage.buckets WHERE id = 'resumes';
```

Should return 1 row with bucket name 'resumes'.

### Check Policies:
```sql
SELECT policyname FROM pg_policies WHERE tablename = 'resumes';
```

Should return policies for reading and inserting.

## How Resume Upload Works (After Setup)

```
1. User uploads PDF file
   ↓
2. Frontend sends file to /resume/upload endpoint
   ↓
3. Backend extracts text from PDF
   ↓
4. Backend uploads PDF to Supabase Storage bucket: resumes/[user_id]/resumes/resume_[timestamp].pdf
   ↓
5. Backend saves metadata to database table: resumes
   (user_id, file_path, extracted_text, uploaded_at)
   ↓
6. Success! User can now search for jobs and generate emails
```

## File Structure in Storage

After upload, files are organized like:
```
resumes/
  └── [user_id]/
      └── resumes/
          ├── resume_20251015_123456.pdf
          ├── resume_20251015_134567.pdf
          └── resume_20251015_145678.pdf
```

Each user has their own folder, protected by RLS policies.

## Testing

After setup, test the upload:

1. Log in to the application
2. Go to Dashboard
3. Upload a PDF resume (under 10MB)
4. Check browser console for:
   ```
   Dashboard: Uploading resume file: my_resume.pdf 123456 bytes
   Dashboard: Resume upload successful
   ```
5. Check backend terminal for:
   ```
   WARNING: SUPABASE_JWT_SECRET not set. Decoding token without verification.
   INFO: 127.0.0.1:xxxxx - "POST /resume/upload HTTP/1.1" 200 OK
   ```

If successful, you'll see:
- ✅ "Resume uploaded successfully!" toast message
- ✅ Green checkmark with filename shown
- ✅ Job search section becomes available

## Troubleshooting

### Still getting "Bucket not found"?
- Check that bucket was created: Go to Storage in Supabase
- Verify bucket name is exactly `resumes` (lowercase)
- Try creating bucket manually via UI

### Still getting "Table not found"?
- Check tables exist: Go to Table Editor in Supabase
- Run setup script again (it's safe to run multiple times)
- Check you're in the correct Supabase project

### Getting "Permission denied"?
- Check RLS policies are created
- Make sure you're logged in
- Check that JWT token is being sent (see browser console)

### Upload works but can't retrieve resume?
- Check the `resumes` table has data:
  ```sql
  SELECT * FROM resumes ORDER BY uploaded_at DESC LIMIT 5;
  ```
- Check file exists in storage bucket
- Check user_id matches between session and database

## Security Notes

### Row Level Security (RLS)
- Users can only see their own resumes
- Users can only upload to their own folder
- Service role can bypass RLS for admin operations

### Storage Policies
- Files are organized by user_id
- Each user can only access their own files
- Files are private (not publicly accessible)

### JWT Token
- Currently development mode (no signature verification)
- For production, set `SUPABASE_JWT_SECRET` in backend/.env
- Tokens expire after a set time (configured in Supabase)

## Next Steps

After successful setup:
1. ✅ Upload a resume
2. ✅ Search for internship jobs
3. ✅ Generate personalized cold emails
4. ✅ View email history

For production deployment:
1. Set `SUPABASE_JWT_SECRET` in backend/.env
2. Set up proper CORS policies
3. Configure rate limiting
4. Set up monitoring and logging

## Files Created/Modified

1. `SUPABASE_SETUP.md` - Detailed setup instructions
2. `supabase_complete_setup.sql` - One-click setup script
3. `docs/RESUME_UPLOAD_BUCKET_FIX.md` - This documentation

## Summary

**Problem**: Database and storage not set up
**Solution**: Run `supabase_complete_setup.sql` in Supabase SQL Editor
**Time**: 5 minutes
**Result**: Resume upload works! 🎉
