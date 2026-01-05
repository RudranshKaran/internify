# Fix: "Failed to create user account in database"

## The Problem
Your resume upload is failing because RLS (Row Level Security) policies in Supabase are blocking user creation.

## The Solution

### Step 1: Run the RLS Fix Script

1. Open your **Supabase Dashboard**
2. Go to **SQL Editor** (left sidebar)
3. Click **New Query**
4. Copy and paste the contents of `FIX_RLS_POLICIES.sql` (in this same folder)
5. Click **Run** (or press Ctrl+Enter)

This will:
- ✅ Allow authenticated users to create their own user records
- ✅ Allow users to upload and manage their own resumes
- ✅ Fix all RLS policies for users, resumes, emails, and internships tables

### Step 2: Restart Your Backend

```bash
# Stop the backend (Ctrl+C in the terminal)
# Then restart:
cd c:\Users\rudra\Desktop\projects\internify\backend
python main.py
```

### Step 3: Try Uploading Again

1. Refresh your browser
2. Try uploading your resume again
3. Check the backend terminal for logs

## What the Logs Will Show

After the fix, you should see:
```
[RESUME] Upload request from user_id: xxx, email: xxx
[SUPABASE] Fetching user by ID: xxx
[SUPABASE] No user found with ID: xxx
[RESUME] User xxx not found in database, creating...
[SUPABASE] Creating user with data: {...}
[SUPABASE] User created successfully: {...}
[RESUME] File uploaded to storage successfully
[SUPABASE] Attempting to save resume for user_id: xxx
[SUPABASE] Resume saved successfully with id: xxx
```

## If It Still Fails

Check the backend logs for the exact error. Common issues:

1. **"relation 'users' does not exist"** - Run the database schema from `docs/database/supabase_complete_setup.sql`
2. **"permission denied"** - Make sure RLS policies are set up correctly (run FIX_RLS_POLICIES.sql)
3. **"invalid UUID"** - Auth token issue, try logging out and back in

## Alternative: Disable RLS Temporarily (Not Recommended for Production)

If you just want to test quickly:

```sql
-- Temporarily disable RLS (ONLY FOR TESTING)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE resumes DISABLE ROW LEVEL SECURITY;
```

**⚠️ Warning:** Only do this for local testing. Re-enable RLS before deploying!
