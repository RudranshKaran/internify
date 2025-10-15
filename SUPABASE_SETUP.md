# 🔧 Supabase Setup Instructions

## Problem
When uploading a resume, you get these errors:
1. `Bucket not found` - The storage bucket for resumes doesn't exist
2. `Could not find the table 'public.resumes'` - The database tables haven't been created

## Solution

You need to set up your Supabase database and storage. Follow these steps:

---

## Step 1: Create Database Tables

1. Go to your Supabase dashboard: https://app.supabase.com
2. Select your project: `nrcoscehjfbxwafjhxvq`
3. Click on **SQL Editor** in the left sidebar
4. Click **New Query**
5. Copy and paste the ENTIRE contents of `database_schema.sql` from this project
6. Click **Run** button (or press Ctrl+Enter)

You should see: `Success. No rows returned`

### What this creates:
- ✅ `users` table - stores user information
- ✅ `resumes` table - stores resume metadata
- ✅ `jobs` table - stores job postings
- ✅ `emails` table - stores email history
- ✅ Row Level Security (RLS) policies for data protection

---

## Step 2: Create Storage Bucket

1. Still in Supabase dashboard
2. Click on **Storage** in the left sidebar
3. Click **New Bucket** button
4. Configure the bucket:
   ```
   Name: resumes
   Public: No (keep it private)
   File size limit: 10 MB
   Allowed MIME types: application/pdf
   ```
5. Click **Create bucket**

### Set up Storage Policies

After creating the bucket, you need to set up policies:

1. Click on the `resumes` bucket you just created
2. Go to **Policies** tab
3. Click **New Policy** button
4. You'll see options for templates - click **"For full customization"** at the bottom

#### Policy 1: Users can upload their own resumes

Click **New Policy** and fill in:

**Policy name:**
```
Users can upload own resumes
```

**Allowed operation:** Check **INSERT** only

**Target roles:** Select `authenticated` from dropdown (or leave as "Defaults to all (public) roles")

**Policy definition:** Paste this in the SQL editor:
```sql
(
  bucket_id = 'resumes'
  AND (storage.foldername(name))[1] = auth.uid()::text
)
```

**Explanation:** This checks that:
- The file is being uploaded to the 'resumes' bucket
- The first folder in the path matches the user's ID (auth.uid())

Click **Review** then **Save policy**

#### Policy 2: Users can read their own resumes

Click **New Policy** again and fill in:

**Policy name:**
```
Users can read own resumes
```

**Allowed operation:** Check **SELECT** only

**Target roles:** Select `authenticated` from dropdown

**Policy definition:** Paste this in the SQL editor:
```sql
(
  bucket_id = 'resumes'
  AND (storage.foldername(name))[1] = auth.uid()::text
)
```

Click **Review** then **Save policy**

#### Policy 3: Users can update their own resumes

Click **New Policy** again and fill in:

**Policy name:**
```
Users can update own resumes
```

**Allowed operation:** Check **UPDATE** only

**Target roles:** Select `authenticated` from dropdown

**Policy definition:** Paste this in the SQL editor:
```sql
(
  bucket_id = 'resumes'
  AND (storage.foldername(name))[1] = auth.uid()::text
)
```

Click **Review** then **Save policy**

#### Policy 4: Users can delete their own resumes

Click **New Policy** again and fill in:

**Policy name:**
```
Users can delete own resumes
```

**Allowed operation:** Check **DELETE** only

**Target roles:** Select `authenticated` from dropdown

**Policy definition:** Paste this in the SQL editor:
```sql
(
  bucket_id = 'resumes'
  AND (storage.foldername(name))[1] = auth.uid()::text
)
```

Click **Review** then **Save policy**

---

**Note:** After creating all 4 policies, you should see them listed in the Policies tab of your `resumes` bucket. Make sure all 4 are enabled (toggle switch is ON).

---

## Step 3: Verify Setup

### Check Tables
1. Go to **Table Editor** in Supabase
2. You should see: `users`, `resumes`, `jobs`, `emails` tables

### Check Storage
1. Go to **Storage**
2. You should see: `resumes` bucket

---

## Step 4: Test Resume Upload

1. Go back to your application
2. Log in
3. Try uploading a resume
4. It should work now!

---

## Quick Setup via SQL (Alternative)

If you prefer, you can do everything via SQL:

### 1. Create Tables
Go to SQL Editor and run:
```sql
-- Copy the entire contents of database_schema.sql file
```

### 2. Create Storage Bucket and Policies
Go to SQL Editor and run:
```sql
-- Create storage bucket (this creates the bucket structure)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'resumes',
  'resumes',
  false,
  10485760, -- 10 MB in bytes
  ARRAY['application/pdf']
);

-- Add storage policies
CREATE POLICY "Users can upload own resumes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can read own resumes"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can update own resumes"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete own resumes"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'resumes' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

---

## Troubleshooting

### If you still get "Bucket not found":
- Make sure the bucket name is exactly `resumes` (lowercase, no spaces)
- Check that the bucket was created successfully in Storage tab

### If you still get "Table not found":
- Make sure you ran the entire `database_schema.sql` script
- Check in Table Editor that tables were created
- Make sure you're in the correct Supabase project

### If you get "Permission denied":
- Check that RLS policies were created correctly
- Make sure you're logged in with a valid user
- Check that the JWT token is being sent correctly

### If upload still fails:
- Check backend terminal for detailed error messages
- Check browser console for error details
- Make sure the PDF file is valid and under 10MB

---

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
