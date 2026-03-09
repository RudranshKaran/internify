-- Diagnostic and Fix Script for Resume Upload Issue
-- Run this ENTIRE script in Supabase SQL Editor

-- ============================================================
-- STEP 1: Check if tables exist
-- ============================================================
SELECT 'Checking tables...' as status;

SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'resumes', 'emails', 'internships');

-- ============================================================
-- STEP 2: Check table structures
-- ============================================================
SELECT 'Checking resumes table structure...' as status;

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'resumes'
ORDER BY ordinal_position;

-- ============================================================
-- STEP 3: Drop ALL existing policies completely
-- ============================================================
SELECT 'Dropping all existing policies...' as status;

-- Drop all policies on users table
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'users') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON users';
    END LOOP;
END $$;

-- Drop all policies on resumes table
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'resumes') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON resumes';
    END LOOP;
END $$;

-- Drop all policies on emails table
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'emails') LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON emails';
    END LOOP;
END $$;

-- ============================================================
-- STEP 4: Create fresh, correct policies
-- ============================================================
SELECT 'Creating new policies...' as status;

-- USERS TABLE POLICIES
CREATE POLICY "users_insert_own"
ON users FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = id);

CREATE POLICY "users_select_own"
ON users FOR SELECT
TO authenticated
USING (auth.uid() = id);

CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- RESUMES TABLE POLICIES
CREATE POLICY "resumes_insert_own"
ON resumes FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "resumes_select_own"
ON resumes FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "resumes_update_own"
ON resumes FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "resumes_delete_own"
ON resumes FOR DELETE
TO authenticated
USING (auth.uid() = user_id);

-- EMAILS TABLE POLICIES
CREATE POLICY "emails_insert_own"
ON emails FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "emails_select_own"
ON emails FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- INTERNSHIPS TABLE POLICIES
CREATE POLICY "internships_select_all"
ON internships FOR SELECT
TO authenticated
USING (true);

-- ============================================================
-- STEP 5: Ensure RLS is enabled
-- ============================================================
SELECT 'Enabling RLS...' as status;

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE internships ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- STEP 6: Grant permissions
-- ============================================================
SELECT 'Granting permissions...' as status;

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON users TO authenticated;
GRANT ALL ON resumes TO authenticated;
GRANT ALL ON emails TO authenticated;
GRANT SELECT ON internships TO authenticated;

-- ============================================================
-- STEP 7: Verify setup
-- ============================================================
SELECT 'Verification complete! Check results below:' as status;

-- Show all policies
SELECT tablename, policyname, cmd, qual 
FROM pg_policies 
WHERE tablename IN ('users', 'resumes', 'emails', 'internships')
ORDER BY tablename, policyname;

SELECT 'Setup complete! Try uploading your resume now.' as final_status;
