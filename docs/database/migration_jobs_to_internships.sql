-- ===================================================================
-- MIGRATION SCRIPT: Rename jobs table to internships
-- ===================================================================
-- WARNING: This will modify your existing database!
-- BACKUP YOUR DATABASE BEFORE RUNNING THIS SCRIPT!
-- ===================================================================

-- This script renames the 'jobs' table to 'internships' and updates all 
-- related foreign keys, indexes, and policies.

BEGIN;

-- Step 1: Rename the jobs table to internships
ALTER TABLE IF EXISTS jobs RENAME TO internships;

-- Step 2: Rename the foreign key column in emails table
ALTER TABLE IF EXISTS emails 
RENAME COLUMN job_id TO internship_id;

-- Step 3: Rename indexes
ALTER INDEX IF EXISTS idx_jobs_company 
RENAME TO idx_internships_company;

-- Step 4: Drop old policies
DROP POLICY IF EXISTS "Authenticated users can read jobs" ON internships;
DROP POLICY IF EXISTS "Service role can insert jobs" ON internships;

-- Step 5: Create new policies with updated names
CREATE POLICY "Authenticated users can read internships" ON internships
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Service role can insert internships" ON internships
    FOR INSERT
    WITH CHECK (true);

-- Step 6: Update the email_history view if it exists
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
    i.title as internship_title,
    i.company,
    i.location,
    i.link as internship_link
FROM emails e
LEFT JOIN internships i ON e.internship_id = i.id
ORDER BY e.sent_at DESC;

-- Grant access to the view
GRANT SELECT ON email_history TO authenticated;

-- Step 7: Update table comment
COMMENT ON TABLE internships IS 'Internship postings scraped from LinkedIn/SerpAPI';

COMMIT;

-- Verify the migration
SELECT 'Migration completed successfully!' as message;
SELECT 'Verifying table exists...' as step;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'internships';

SELECT 'Verifying foreign key exists...' as step;
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'emails' 
AND column_name = 'internship_id';

SELECT 'Migration verification complete!' as message;

-- ===================================================================
-- ROLLBACK (if needed):
-- If something goes wrong, you can rollback with:
-- 
-- BEGIN;
-- ALTER TABLE internships RENAME TO jobs;
-- ALTER TABLE emails RENAME COLUMN internship_id TO job_id;
-- ALTER INDEX idx_internships_company RENAME TO idx_jobs_company;
-- DROP POLICY IF EXISTS "Authenticated users can read internships" ON jobs;
-- DROP POLICY IF EXISTS "Service role can insert internships" ON jobs;
-- CREATE POLICY "Authenticated users can read jobs" ON jobs
--     FOR SELECT TO authenticated USING (true);
-- CREATE POLICY "Service role can insert jobs" ON jobs
--     FOR INSERT WITH CHECK (true);
-- COMMIT;
-- ===================================================================
