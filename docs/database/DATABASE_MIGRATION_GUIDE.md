# 🚀 QUICK DATABASE MIGRATION GUIDE

## ⚠️ READ THIS FIRST!

**IMPORTANT**: This migration will rename your `jobs` table to `internships` and update all related foreign keys, indexes, and policies.

---

## 📋 PRE-MIGRATION CHECKLIST

- [ ] **BACKUP YOUR DATABASE** (Supabase Dashboard → Database → Backups)
- [ ] Verify you have admin access to Supabase SQL Editor
- [ ] Ensure no critical operations are running
- [ ] Have the rollback script ready (see below)
- [ ] Test in development environment first

---

## 🎯 MIGRATION STEPS

### Step 1: Open Supabase SQL Editor
1. Go to your Supabase Dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**

### Step 2: Run Migration Script
1. Open `migration_jobs_to_internships.sql` from your project root
2. Copy the entire contents
3. Paste into Supabase SQL Editor
4. Click **Run** (or press Ctrl/Cmd + Enter)

### Step 3: Verify Migration
The script includes verification queries. You should see:
- ✅ "Migration completed successfully!"
- ✅ Table name: `internships` (not `jobs`)
- ✅ Column name: `internship_id` in emails table

### Step 4: Update Backend Service
The backend `supabase_service.py` still references table names. No code changes needed - the function names are already updated, but they interact with the new table name automatically.

---

## 🔍 WHAT GETS CHANGED

| Item | Before | After |
|------|--------|-------|
| **Table Name** | `jobs` | `internships` |
| **Foreign Key** | `emails.job_id` | `emails.internship_id` |
| **Index** | `idx_jobs_company` | `idx_internships_company` |
| **RLS Policy** | "...read jobs" | "...read internships" |
| **View** | email_history (job columns) | email_history (internship columns) |

---

## ✅ POST-MIGRATION TESTING

### Test in Supabase Dashboard
```sql
-- 1. Check table exists
SELECT * FROM internships LIMIT 1;

-- 2. Check foreign key exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'emails' 
AND column_name = 'internship_id';

-- 3. Test join
SELECT e.id, e.subject, i.title, i.company
FROM emails e
LEFT JOIN internships i ON e.internship_id = i.id
LIMIT 5;
```

### Test with Backend
```bash
# Start your backend
cd backend
uvicorn main:app --reload

# Visit API docs
# http://localhost:8000/docs

# Test the /internships/search endpoint
```

---

## 🔄 ROLLBACK (If Something Goes Wrong)

### Immediate Rollback
If the migration fails or you need to rollback immediately:

```sql
BEGIN;

-- Rename table back
ALTER TABLE internships RENAME TO jobs;

-- Rename foreign key back
ALTER TABLE emails RENAME COLUMN internship_id TO job_id;

-- Rename index back
ALTER INDEX idx_internships_company RENAME TO idx_jobs_company;

-- Drop new policies
DROP POLICY IF EXISTS "Authenticated users can read internships" ON jobs;
DROP POLICY IF EXISTS "Service role can insert internships" ON jobs;

-- Recreate old policies
CREATE POLICY "Authenticated users can read jobs" ON jobs
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Service role can insert jobs" ON jobs
    FOR INSERT WITH CHECK (true);

-- Recreate old view
DROP VIEW IF EXISTS email_history;
CREATE OR REPLACE VIEW email_history AS
SELECT 
    e.id,
    e.user_id,
    e.subject,
    e.body,
    e.recipient_email,
    e.sent_at,
    e.status,
    j.title as job_title,
    j.company,
    j.location,
    j.link as job_link
FROM emails e
LEFT JOIN jobs j ON e.job_id = j.id
ORDER BY e.sent_at DESC;

GRANT SELECT ON email_history TO authenticated;

COMMIT;
```

---

## 💡 TIPS

1. **Test First**: If possible, test this on a development/staging database first
2. **Off-Peak Hours**: Run migration during low-traffic times
3. **Monitor**: Watch for errors in your application logs after migration
4. **Quick Verify**: After migration, check that your frontend can still search and display internships

---

## 🆘 TROUBLESHOOTING

### Error: "relation 'jobs' does not exist"
**Solution**: The migration already ran, or the table never existed. Check if `internships` table exists:
```sql
SELECT * FROM internships LIMIT 1;
```

### Error: "column 'job_id' does not exist"
**Solution**: The foreign key was already renamed. Check for `internship_id`:
```sql
SELECT internship_id FROM emails LIMIT 1;
```

### Error: "policy already exists"
**Solution**: Policies were already updated. This is safe to ignore.

### Frontend Still Shows "Jobs"
**Solution**: 
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Check that frontend code was updated and redeployed

---

## 📞 NEED HELP?

If you encounter issues:
1. Check the main `REFACTORING_COMPLETE.md` for detailed information
2. Review `migration_jobs_to_internships.sql` for inline comments
3. Verify all code changes were committed and deployed
4. Check Supabase logs for any database errors

---

## ✨ SUCCESS INDICATORS

You'll know the migration was successful when:
- ✅ SQL Editor shows "Migration completed successfully!"
- ✅ `SELECT * FROM internships;` returns data
- ✅ `SELECT internship_id FROM emails;` works (not job_id)
- ✅ Backend `/internships/search` endpoint works
- ✅ Frontend displays internship cards correctly
- ✅ Email history shows internship details

---

**Ready?** 
1. Backup your database
2. Open `migration_jobs_to_internships.sql`
3. Run it in Supabase SQL Editor
4. Test everything
5. Deploy your updated code

Good luck! 🚀
