# Emergency Fix Guide - Email Generation & Database Issues

## Issues Identified

### 1. ❌ Gemini API Error
**Error Message:**
```
Gemini API error: 404 models/gemini-pro is not found for API version v1beta
```

**Root Cause:** The model name `gemini-pro` is outdated and no longer available in Gemini API v1beta.

**Fix Applied:** ✅ Updated to `gemini-1.5-flash` (current stable model)

---

### 2. ❌ Supabase Table Not Found
**Error Message:**
```
Error saving internship: {'message': "Could not find the table 'public.internships' in the schema cache", 'code': 'PGRST205'}
```

**Root Cause:** The internships table either:
- Doesn't exist in your Supabase database
- Exists but Supabase API schema cache is outdated
- Missing the new contact information columns

**Fix Required:** You need to apply the database migration

---

## Quick Fix Steps

### Step 1: Fix Gemini Model (Already Done ✅)
The code has been updated. Just restart the backend.

### Step 2: Apply Database Migration

#### Option A: Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard:**
   - Go to https://supabase.com/dashboard
   - Select your Internify project

2. **Open SQL Editor:**
   - Click "SQL Editor" in left sidebar
   - Click "New Query"

3. **Check if internships table exists:**
   ```sql
   SELECT EXISTS (
     SELECT FROM information_schema.tables 
     WHERE table_schema = 'public' 
     AND table_name = 'internships'
   );
   ```
   - If returns `false`, the table doesn't exist
   - If returns `true`, the table exists but may need columns

4. **Create/Update the table:**
   
   **If table doesn't exist** - Run the full schema:
   ```sql
   -- Create internships table
   CREATE TABLE IF NOT EXISTS internships (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       title TEXT NOT NULL,
       company TEXT NOT NULL,
       link TEXT,
       description TEXT,
       location TEXT,
       posted_at TIMESTAMP,
       contact_email TEXT,
       contact_phone TEXT,
       contact_website TEXT,
       created_at TIMESTAMP DEFAULT NOW()
   );

   -- Create indexes
   CREATE INDEX IF NOT EXISTS idx_internships_company ON internships(company);
   CREATE INDEX IF NOT EXISTS idx_internships_location ON internships(location);
   CREATE INDEX IF NOT EXISTS idx_internships_contact_email ON internships(contact_email) WHERE contact_email IS NOT NULL;

   -- Enable RLS
   ALTER TABLE internships ENABLE ROW LEVEL SECURITY;

   -- RLS Policy
   CREATE POLICY "Authenticated users can read internships" ON internships
       FOR SELECT
       TO authenticated
       USING (true);
   
   CREATE POLICY "Service role can insert internships" ON internships
       FOR INSERT
       WITH CHECK (true);
   ```

   **If table exists** - Just add the new columns:
   ```sql
   -- Add contact information columns
   ALTER TABLE internships 
   ADD COLUMN IF NOT EXISTS contact_email TEXT,
   ADD COLUMN IF NOT EXISTS contact_phone TEXT,
   ADD COLUMN IF NOT EXISTS contact_website TEXT;

   -- Create indexes
   CREATE INDEX IF NOT EXISTS idx_internships_contact_email ON internships(contact_email) WHERE contact_email IS NOT NULL;
   CREATE INDEX IF NOT EXISTS idx_internships_location ON internships(location);
   ```

5. **Verify the changes:**
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'internships' 
   ORDER BY ordinal_position;
   ```
   
   Should show all columns including:
   - contact_email
   - contact_phone
   - contact_website

#### Option B: Refresh Supabase Schema Cache

Sometimes Supabase just needs to refresh its cache:

1. Go to Supabase Dashboard
2. Click on "Database" → "Tables"
3. Find the `internships` table
4. This forces a schema refresh
5. Wait 30 seconds
6. Restart your backend

### Step 3: Restart Backend

In PowerShell terminal running uvicorn:
```powershell
# Press Ctrl+C to stop
# Then restart:
cd c:\Users\rudra\Desktop\projects\internify\backend
uvicorn main:app --reload
```

### Step 4: Test Email Generation

1. Go to your app: http://localhost:3000
2. Search for internships: "ai engineer"
3. Select an internship
4. Click "Generate Email"
5. Should now work without errors

---

## Verification Checklist

After applying fixes, verify:

- [ ] Backend restarts without errors
- [ ] No Gemini API 404 errors in logs
- [ ] Internship search returns results
- [ ] No "PGRST205" errors when searching
- [ ] Contact information appears on internship cards (if available)
- [ ] Email generation works without errors
- [ ] Generated emails look professional

---

## Expected Backend Logs (Success)

After fixes, you should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:XXXXX - "GET /internships/search?role=ai+engineer HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "POST /llm/generate-email HTTP/1.1" 200 OK
```

No more:
- ❌ "models/gemini-pro is not found"
- ❌ "Could not find the table 'public.internships' in the schema cache"

---

## Troubleshooting

### Issue: Still getting Gemini errors
**Solution:**
1. Make sure backend restarted after code changes
2. Check if GEMINI_API_KEY is valid in .env
3. Try using GROQ instead (set GROQ_API_KEY in .env)

### Issue: Still getting table not found errors
**Solution:**
1. Verify the SQL ran successfully in Supabase
2. Check for any SQL errors in Supabase dashboard
3. Make sure you're using the correct Supabase project
4. Try refreshing the schema cache (Option B above)

### Issue: "Service role can insert" policy fails
**Solution:**
Make sure you're using SUPABASE_SERVICE_KEY not SUPABASE_ANON_KEY in your .env file for the backend.

### Issue: Email generation returns 500 error
**Check:**
1. Is resume uploaded?
2. Is internship selected?
3. Check backend logs for specific error
4. Verify GEMINI_API_KEY or GROQ_API_KEY in .env

---

## Alternative: Use GROQ Instead of Gemini

If Gemini continues to cause issues, switch to GROQ:

1. Get GROQ API key from https://console.groq.com
2. Add to .env:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
3. Install GROQ library:
   ```powershell
   cd backend
   pip install groq
   ```
4. Restart backend

The code will automatically prefer GROQ over Gemini if both keys exist.

---

## Files Changed

### Backend Files Updated:
1. ✅ `backend/services/llm_service.py` - Fixed Gemini model name
2. ✅ `backend/services/supabase_service.py` - Better error handling
3. ✅ `backend/routes/internships.py` - Added contact fields to save

### Database Migration Required:
- `docs/database/migration_add_contact_info.sql` - Run this in Supabase

---

## Summary

**Immediate Actions Required:**
1. ⚠️ Apply database migration in Supabase (Step 2 above)
2. ⚠️ Restart backend (Step 3 above)
3. ✅ Test email generation (Step 4 above)

**Already Fixed in Code:**
- ✅ Gemini model updated to `gemini-1.5-flash`
- ✅ Better error messages for debugging
- ✅ Contact information fields added to internship saves

Once you complete Steps 2 and 3, everything should work! 🚀
